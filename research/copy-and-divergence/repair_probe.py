"""Apply reviewed, exact copy cuts to frozen fixtures; preserve each major flow."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
from playwright.sync_api import sync_playwright,expect

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"creative-pilot"
S=importlib.util.spec_from_file_location("prior_browser",OLD/"browser_check.py")
prior=importlib.util.module_from_spec(S);S.loader.exec_module(prior)

CASES=[
    ("radio-C", [('        <p>先选收音机的现象，看看需要怎么检查。</p>\n','')],
     ['先选收音机的现象，看看需要怎么检查。','完全没声音']),
    ("books-C", [('      <p>点书名，查看领取时间、地点和走法。</p>\n','')],
     ['点书名，查看领取时间、地点和走法。','选一本绘本']),
    ("lab-loan-B", [
      ('        <p class="kicker">Tool loans</p>\n',''),
      ('<h1>What are you<br>working on?</h1>','<h1 id="tasks-title">What do you need a tool for?</h1>'),
      ('        <h2 class="section-label" id="tasks-title">Choose a task</h2>\n',''),
      ('<h2 class="section-label" id="terms-title">Loan terms</h2>\n        <p class="duration">Three days</p>', '<h2 class="duration" id="terms-title">Three-day loans</h2>')],
     ['Choose a task','Three-day loans']),
    ("orchard-V", [
      ('            <p class="label">Orchard map</p>\n',''),
      ('Friday’s harvest note: The north rows are still too muddy after rain.','Friday’s harvest note: Still too muddy after rain.')],
     ['Orchard map','Friday’s harvest note: Still too muddy after rain.']),
]

def apply(src, operations):
    for target,new in operations:
        assert src.count(target)==1,target
        src=src.replace(target,new,1)
    return src

def main():
    p=argparse.ArgumentParser()
    p.add_argument("pages",type=Path)
    p.add_argument("out",type=Path)
    a=p.parse_args()
    (a.out/"assets").mkdir(parents=True,exist_ok=True)
    shutil.copyfile(OLD/"fixtures/assets/basket.jpg",a.out/"assets/basket.jpg")
    report=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(channel="chrome")
        for name,changes,(forbidden,required) in CASES:
            synthetic=name.endswith("-C")
            src=a.pages/f"{name}.html" if synthetic else OLD/"fixtures"/name/"index.html"
            original=src.read_text()
            dest=a.out/name/"index.html";dest.parent.mkdir(exist_ok=True)
            original_copy=dest.with_name("before.html");original_copy.write_text(original)
            dest.write_text(apply(original,changes))
            case,arm=name.rsplit("-",1)
            for view,(w,h) in VIEW.items():
                ctx=b.new_context(viewport={"width":w,"height":h})
                ctx.route(re.compile(r"https?://"),lambda r:r.abort())
                page=ctx.new_page()
                page.goto(original_copy.resolve().as_uri())
                expect(page.get_by_text(forbidden,exact=True).filter(visible=True)).to_have_count(1)
                page.screenshot(path=a.out/f"{name}-{view}-before.png")
                page.goto(dest.resolve().as_uri())
                expect(page.get_by_text(forbidden,exact=True)).to_have_count(0)
                expect(page.get_by_text(required,exact=True).filter(visible=True).first).to_be_visible()
                expect(page.get_by_role("heading",level=1)).to_have_count(1)
                assert page.evaluate(r"Array.from(document.querySelectorAll('[aria-labelledby]')).every(e=>e.getAttribute('aria-labelledby').split(/\s+/).every(id=>document.getElementById(id)))")
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
                page.screenshot(path=a.out/f"{name}-{view}-after.png")
                if synthetic:flow(page,CASES_NEW[case])
                else:prior.exercise(page,case,arm)
                page.screenshot(path=a.out/f"{name}-{view}-result.png")
                ctx.close()
                report.append({"page":name,"view":view,"removed":forbidden,"retained":required,"flow":"pass"})
    (a.out/"repair.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(f"{len(report)} deletion and functional checks passed.")

from audit_browser import flow, VIEW, CASES as CASES_NEW
if __name__=="__main__":main()
