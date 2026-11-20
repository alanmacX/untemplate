"""Reproduce paired concept generation with a Codex or Chat Completions backend."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "cases.json").read_text())
ARMS = json.loads((HERE / "prompts.json").read_text())
FORMAT = """Use only facts below. Keep both directions usable; no tools, invented evidence, or citations.
Return exactly a JSON array of two objects. For each, use four short string fields:
premise (the specific piece of evidence and design inference),
opening (what a desktop and phone user actually see first, and what shares space),
move (the first real control, what it does and where the result appears),
tradeoff (a specific gain or cost). About 85 words per direction. Use English."""
FIELDS = ("premise", "opening", "move", "tradeoff")


def prompt(case, arm):
    constraints = "\n".join("- " + x for x in case["facts"])
    return f"""{FORMAT}

Brief: {case["brief"]}
Facts:
{constraints}
Must work: {case["must"]}

Design approach: {ARMS[arm]}"""


def codex(message, model, effort="medium"):
    with tempfile.TemporaryDirectory(prefix="untemplate-") as wd:
        cmd = ["codex", "exec", "--ignore-user-config", "--skip-git-repo-check",
               "--ephemeral", "--sandbox", "read-only", "-C", wd, "-m", model,
               "-c", f'model_reasoning_effort="{effort}"', "--json", "-"]
        p = subprocess.run(cmd, input=message, encoding="utf-8",
                           cwd=wd, capture_output=True, timeout=210)
    if p.returncode:
        raise RuntimeError(f"Codex exited with status {p.returncode}")
    events = [json.loads(line) for line in p.stdout.splitlines() if line.startswith("{")]
    messages = [e["item"]["text"] for e in events
                if e["type"] == "item.completed" and e["item"]["type"] == "agent_message"]
    if not messages:
        raise RuntimeError("No final response")
    return messages[-1], {"usage": next((e["usage"] for e in reversed(events)
                                        if e["type"] == "turn.completed"), None)}


def chat(message, name, api, seed=None, max_tokens=670):
    data = {"model": name, "messages": [{"role": "user", "content": message}],
            "temperature": 0.65, "top_p": 0.9, "max_tokens": max_tokens}
    if seed is not None:
        data["seed"] = seed
    headers = {"Content-Type": "application/json"}
    if key := os.environ.get("UNTEMPLATE_CHAT_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"
    with urlopen(Request(api.rstrip("/") + "/chat/completions",
                         json.dumps(data).encode(), headers=headers), timeout=210) as response:
        parsed = json.load(response)
    choice = parsed["choices"][0]
    return choice["message"]["content"], {"usage": parsed.get("usage"),
                                         "finish_reason": choice.get("finish_reason"),
                                         "model_id": parsed.get("model")}


def parse(text):
    for match in re.finditer(r"\[\s*\{", text):
        try:
            arr, _ = json.JSONDecoder().raw_decode(text[match.start():])
        except ValueError:
            continue
        if (len(arr) == 2 and all(isinstance(row, dict)
            and all(isinstance(row.get(k), str) and row[k].strip() for k in FIELDS)
            for row in arr)):
            return [{k: row[k].strip() for k in FIELDS} for row in arr]
    raise ValueError("Expected two complete objects")


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def one(args, case, arm):
    body = prompt(case, arm)
    output = args.out / args.label / (case["id"] + "-" + arm + ".json")
    if output.exists():
        record = json.loads(output.read_text())
        if record["prompt_sha256"] != fingerprint(body) or record["model"] != args.model:
            raise ValueError(f"Stale cache {output}")
        if record.get("proposals"):
            return record
    seed = int(fingerprint(case["id"])[:6], 16)
    started = time.monotonic()
    can_seed = args.api and not args.omit_seed
    record = {"engine": args.label, "model": args.model, "case": case["id"], "arm": arm,
              "seed": seed if can_seed else None, "prompt_sha256": fingerprint(body)}
    for attempt in range(2):
        try:
            if args.api:
                raw, meta = chat(body, args.model, args.api, seed+attempt if can_seed else None)
            else:
                raw, meta = codex(body, args.model)
            record.update(meta)
            record["proposals"] = parse(raw)
            record.pop("error", None)
            break
        except (OSError, subprocess.TimeoutExpired, ValueError, RuntimeError, KeyError) as ex:
            record["error"] = type(ex).__name__ + ": " + str(ex)[:160]
            if attempt == 0:
                time.sleep(1)
    record.update(attempts=attempt+1, seconds=round(time.monotonic()-started, 2))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(args.label, case["id"], arm, record.get("error", "ok"), record["seconds"], flush=True)
    return record


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--api", help="Optional base URL ending in /v1; otherwise Codex CLI")
    p.add_argument("--omit-seed", action="store_true", help="For endpoints that do not support seed")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--jobs", type=int, default=3)
    p.add_argument("--case", action="append", choices=[c["id"] for c in CASES])
    args = p.parse_args()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        jobs = [pool.submit(one, args, c, a) for c in CASES if not args.case or c["id"] in args.case for a in ARMS]
        results = [f.result() for f in as_completed(jobs)]
    if any("proposals" not in row for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
