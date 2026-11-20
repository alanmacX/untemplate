"""Compare two real browser renders. Requires Python 3 and Playwright.
Run: python render_gate.py spec.json output [--baseline http://localhost:8000/old/]
                                         [--candidate http://localhost:8000/new/] [--channel chrome]
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

VIEWPORTS = {"desktop": [1440, 1000], "mobile": [390, 844]}
MEASURE = r"""({entry, keep, drop, measure}) => {
  const b = e => e.getBoundingClientRect();
  const text = e => (e.innerText || e.textContent || '').replace(/\s+/g, ' ').trim();
  const style = e => getComputedStyle(e);
  const visible = e => {
    const r = b(e);
    if (r.width < 2 || r.height < 2 || !e.checkVisibility({
      checkOpacity: true, checkVisibilityCSS:true, contentVisibilityAuto:true
    })) return false;
    return !/inset\((?:50%|100%)\)/.test(style(e).clipPath)
      && style(e).clip !== 'rect(0px, 0px, 0px, 0px)';
  };
  const inFrame = e => {
    const r = b(e);
    return visible(e) && r.top >= -.5 && r.bottom <= innerHeight + .5 && r.left >= -.5 && r.right <= innerWidth + .5;
  };
  const reachable = e => {
    if (!inFrame(e) || e.matches(':disabled,[aria-disabled=true]') || style(e).pointerEvents === 'none') return false;
    const r = b(e), hit = document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2);
    return hit === e || e.contains(hit);
  };
  const nodes = s => Array.from(document.querySelectorAll(s));
  const required = keep.map(rule => {
    const found = nodes(rule.selector).filter(rule.first_view ? inFrame : visible);
    const matching = found.filter(e => !rule.text || text(e).includes(rule.text));
    return {name:rule.name, visible:found.length, matching:matching.length, pass:matching.length >= (rule.min ?? 1)};
  });
  const rejected = drop.map(rule => ({
    name:rule.name, count:nodes(rule.selector).length, pass:!nodes(rule.selector).length
  }));
  const measurements = Object.fromEntries(measure.map(m => {
    const found = nodes(m.selector);
    return [m.name, {dom:found.length, visible:found.filter(visible).length,
      first_view:found.filter(inFrame).length, first_y:found.find(visible) ? Math.round(b(found.find(visible)).top) : null}];
  }));
  const primary = nodes(entry)[0], heading = document.querySelector('main h1, h1'), css = heading && style(heading);
  return {entry_y:primary ? Math.round(b(primary).top) : null, entry_ok:!!primary && reachable(primary),
    overflow:Math.max(document.body.scrollWidth, document.documentElement.scrollWidth)-innerWidth,
    footer_count:nodes('footer,[role=contentinfo]').filter(visible).length,
    h1:css && {size:parseFloat(css.fontSize), weight:parseFloat(css.fontWeight), tracking:css.letterSpacing},
    required, rejected, measurements};
}"""


def params(case, mode):
    return {"entry": case["entry"],
            "keep": [r for r in case["keep"] if mode in r.get("viewports", VIEWPORTS)],
            "drop": case.get("drop", []), "measure": case.get("measure", [])}


def passes(row):
    return (row["entry_ok"] and row["overflow"] <= 1 and not row["runtime_errors"] and
            all(x["pass"] for x in row["required"] + row["rejected"]))


def audit(browser, origin, case, mode, folder, negative):
    width, height = VIEWPORTS[mode]
    ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    try:
        page.goto(urljoin(origin.rstrip("/")+"/", case["path"]), wait_until="load")
        page.evaluate("document.fonts.ready.then(() => null)")
        page.evaluate("scrollTo(0,0)")
        if folder:
            folder.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=folder/f"{mode}.png", animations="disabled")
            if mode == "desktop":
                page.screenshot(path=folder/"full.png", full_page=True, animations="disabled")
        row = page.evaluate(MEASURE, params(case, mode))
        row["runtime_errors"] = errors[:]
        row["pass"] = passes(row)
        if folder and folder.name == "baseline" and case.get("baseline_probe"):
            probe = case["baseline_probe"]
            touched = page.locator(probe).count()
            css = page.add_style_tag(content=f"{probe} {{ display: none !important; }}")
            alternative = page.evaluate(MEASURE, params(case, mode))
            row["hide_probe"] = {"selector": probe, "nodes": touched,
                                 "entry_y": alternative["entry_y"],
                                 "measurements": alternative["measurements"]}
            css.evaluate("e => e.remove()")
        if negative and row["pass"]:
            selector = case.get("negative_control", case["entry"])
            page.locator(selector).evaluate_all("(nodes) => nodes.forEach(e => e.style.setProperty('display','none','important'))")
            broken = page.evaluate(MEASURE, params(case, mode))
            broken["runtime_errors"] = errors[:]
            row["hidden_required_detected"] = not passes(broken)
            row["pass"] &= row["hidden_required_detected"]
        return row
    finally:
        ctx.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--baseline")
    parser.add_argument("--candidate")
    parser.add_argument("--channel")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if not args.candidate and not args.baseline:
        parser.error("supply --candidate and/or --baseline")
    cases = json.loads(args.spec.read_text())["pages"]
    if not cases or len({c["id"] for c in cases}) != len(cases):
        parser.error("pages must be nonempty with unique ids")
    args.output.mkdir(parents=True, exist_ok=True)
    result = {"viewport": VIEWPORTS, "pages": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch(**({"channel": args.channel} if args.channel else {}))
        result["browser"] = browser.version
        for case in cases:
            entry = result["pages"][case["id"]] = {}
            for label, origin in [("baseline", args.baseline), ("candidate", args.candidate)]:
                if not origin:
                    continue
                entry[label] = {mode: audit(browser, origin, case, mode, args.output / case["id"] / label,
                                            label == "candidate" and args.self_check)
                                for mode in VIEWPORTS}
                print(case["id"], label, {mode: r["pass"] for mode, r in entry[label].items()}, flush=True)
        browser.close()
    (args.output/"browser-gate.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    return int(bool(args.candidate) and not all(r["pass"] for entry in result["pages"].values()
                                               for r in entry["candidate"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
