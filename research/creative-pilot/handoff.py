"""Build the second concept for each preselected case/approach in an identical, fresh context."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re

from run import CASES, codex

CASES_USED = ("lab-loan", "orchard")
ARMS_USED = ("A", "B")
TECH = """Recreate the proposal as a small working page. Treat the given proposal as a handoff and preserve its change to the experience. The full set of facts and actions must still work. Give it care in full composition, including at 1440 and 390 pixels. Use one complete HTML document with internal CSS and JS; no dependencies or network calls. You have only the named local asset. Do not call tools, add new claims, or use boilerplate copy. This is a preview without a backend. Use native keyboard-accessible controls. End state should be visibly and accurately updated. Return only HTML."""
EXTRA = {
    "lab-loan": """No photos supplied. For comparable tests, eligible confirmation must include “Pickup confirmed”, the iron and the chosen time; both pickup windows are available. If needed, use a checkbox for already completing the free induction. Let a browser test choose the Saturday option and request an iron. Keep camera and bench-only item easy to find and unrequestable.""",
    "orchard": """../assets/basket.jpg is a licensed illustrative basket photo; credit Oxfordian Kissuth · CC BY-SA 3.0 in a caption or source link, disambiguate the photo from this orchard. Use a schematic for the hand-marked map if the design requires it: no precise dimensions or distances. For comparable tests offer 14:00 (other times only if clearly marked as demonstration). The selected picking time appears beside “Reservation confirmed”. No reservation required for shop-only visitors. Show scenario-based mock operation, not an actual booking."""
}
VISUAL = {
    "lab-loan": "The three task choices are the physical working surface, with the available or blocked tool response attached to the selected row. Begin the working rows near the top edge, with the page title contained in the same surface. Let the density, boundaries and type hierarchy come from those rows and their changing state. On a phone, show the first task controls without scrolling. Keep the selected row and its confirmed outcome adjacent. Give that hierarchy a visible identity without requiring a separate decorative area.",
    "orchard": "Treat the map as the main view down into the site: the two available rows and bypass should make up the first substantial visual surface. Keep the title and closure note part of that map composition, with each row carrying its real picking control and the bypass leading visibly to shop information. On a phone both row controls are visible at first arrival; move supplementary imagery and hours after the first read if needed. Put the result immediately below the map so the visitor can relate it to the chosen row. Use the same basket photo assets and copy facts."
}


def build(c, a, args):
    source = args.in_dir / "gpt" / f'{c["id"]}-{a}.json'
    concept = json.loads(source.read_text())["proposals"][1]
    body = "\n\n".join((TECH, EXTRA[c["id"]], json.dumps(c), json.dumps(concept)))
    if args.visual_handoff:
        body += "\n\nMatched visual handoff: " + VISUAL[c["id"]]
    tag = "V" if args.visual_handoff else a
    dest = args.out / f'{c["id"]}-{tag}'
    dest.mkdir(parents=True, exist_ok=True)
    raw, _ = codex(body, "gpt-6.2-sol")
    result = re.search(r"<!doctype\s+html\b.*?</html\s*>",raw,re.I|re.S)
    if not result:
        raise ValueError(f"No complete HTML for {dest.name}")
    (dest / "index.html").write_text(result.group(0) + "\n")
    print(dest.name, len(result.group(0)), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--visual-handoff", action="store_true", help="Replay arm B with a concrete scene and coordinate-free visual relation")
    args = p.parse_args()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(build,c,a,args) for c in CASES if c["id"] in CASES_USED for a in (("B",) if args.visual_handoff else ARMS_USED)]
        for f in futures:
            f.result()


if __name__ == "__main__":
    main()
