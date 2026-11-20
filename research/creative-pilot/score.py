"""Anonymize concepts and audit concrete differences against a narrow rubric."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import random
from pathlib import Path

from run import CASES, codex

RUBRIC = """Review these anonymous concept pairs as concept sketches. Score each pair separately before comparing. Use the available facts. A short sketch may leave secondary details implicit when they can be added without changing its central decision. A factual contradiction, invented operational rule, unavailable required material, or an approach that blocks/changes a must-work task invalidates that direction. Give credit for a difference only if you can point to a distinct useful information or decision order, first action, where its result appears, or specific visual material/geometry that changes reading or perception for this project. Merely discussing a different theme, naming a different inspiration, rearranging equivalent controls, or making a secondary shortcut more prominent does not earn a second route. Keep task fit separate from difference; call a plan borderline for a material ambiguity. Do not infer the author's approach or score text polish. Use only these pair IDs.
Return a JSON object keyed by the provided pair IDs. Value for each:
{"a_usable":"yes|no|unclear","b_usable":"yes|no|unclear","fork":"yes|no|unclear","why":"specific difference and any issue, up to 45 words"}. No tools."""
VALS = {"yes", "no", "unclear"}


def grade(case, args):
    rows = [json.loads(p.read_text()) for p in args.in_dir.glob(f'*/{case["id"]}-*.json')]
    rows = sorted((r for r in rows if r.get("proposals")), key=lambda r: (r["engine"],r["arm"]))
    if not rows:
        return []
    rnd = random.Random("untemplate-review-1:"+case["id"])
    rnd.shuffle(rows)
    payload = {}
    by_id = {}
    for i, row in enumerate(rows, 1):
        label = hashlib.sha256(f'{case["id"]}:{i}'.encode()).hexdigest()[:5]
        payload[label] = row["proposals"]
        by_id[label] = row
    body = "\n\n".join((RUBRIC, json.dumps(case,ensure_ascii=False),json.dumps(payload,ensure_ascii=False)))
    raw, meta = codex(body, args.judge)
    ix = raw.index("{")
    verdicts, _ = json.JSONDecoder().raw_decode(raw[ix:])
    assert set(verdicts) == set(by_id)
    assert all(v[k] in VALS for v in verdicts.values() for k in ('a_usable','b_usable','fork'))
    return [{**{k:r[k] for k in ("case","engine","model","arm")},
             "anonymous_id":i, **verdicts[i]} for i,r in by_id.items()]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--in-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--judge",default="gpt-6.2-sol")
    a=p.parse_args()
    with ThreadPoolExecutor(max_workers=6) as ex:
        outcome=[row for rr in ex.map(lambda c:grade(c,a),CASES) for row in rr]
    a.out.write_text(json.dumps({"judge":a.judge,"observations":outcome}, ensure_ascii=False,indent=2)+"\n")
    for key in sorted({(r["engine"],r["arm"]) for r in outcome}):
        group = [r for r in outcome if (r["engine"],r["arm"])==key]
        print(key, "usable forks", sum(r["a_usable"]==r["b_usable"]==r["fork"]=="yes" for r in group),
              "both usable", sum(r["a_usable"]==r["b_usable"]=="yes" for r in group), "total",len(group))


if __name__ == "__main__":
    main()
