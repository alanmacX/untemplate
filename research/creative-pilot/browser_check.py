"""Replay the four frozen prototypes and capture paired screenshots."""
import argparse
import json
from pathlib import Path
import re
from itertools import product

from PIL import Image, ImageOps
from playwright.sync_api import expect, sync_playwright

CASES = ("lab-loan", "orchard")
VIEWS = {"desktop": {"width": 1440, "height": 1000}, "phone": {"width": 390, "height": 844}}


def exercise(page, case, arm):
    if case == "lab-loan":
        if arm == "A":
            expect(page.get_by_role("button", name="Request an iron")).to_be_disabled()
            page.get_by_role("button", name=re.compile("Saturday")).click()
            page.get_by_role("button", name="Request an iron").click()
            button = page.get_by_role("button", name="Confirm pickup")
        else:
            page.locator("summary").filter(has_text="Measure voltage").click()
            expect(page.get_by_text("Supervised bench only")).to_be_visible()
            expect(page.locator("summary").filter(has_text="Measure voltage").locator("..").get_by_role("button")).to_have_count(0)
            page.locator("summary").filter(has_text="Solder something").click()
            page.get_by_role("radio", name=re.compile("Saturday")).check()
            button = page.get_by_role("button", name="Request an iron")
        before = page.get_by_text("Pickup confirmed", exact=True)
        if button.is_enabled():
            button.click()
        expect(before).to_be_hidden()
        page.get_by_role("checkbox").check()
        button.click()
        expect(before).to_be_visible()
        detail = {"A":"#confirmed-details","B":"#confirmed-pickup","V":"#confirmation-details"}[arm]
        expect(page.locator(detail)).to_contain_text(re.compile("Saturday"))
    else:
        if arm == "A":
            page.get_by_role("link", name=re.compile("shop only", re.I)).click()
            expect(page.locator("#orchard-map")).to_be_visible()
            page.get_by_role("button", name="Reserve picking").click()
            button = page.get_by_role("button", name="Confirm picking time")
        else:
            if arm == "B":
                page.get_by_role("link", name=re.compile("shop route", re.I)).click()
                expect(page.locator("#shop-route")).to_contain_text("No booking needed.")
            else:
                page.get_by_role("link", name=re.compile("shop visit", re.I)).click()
                expect(page.locator("#shop")).to_contain_text(re.compile("no (booking|reservation)", re.I))
            page.get_by_role("button", name=re.compile("Ashmeads")).click()
            expect(page.locator("#picking-title")).to_contain_text("Ashmeads")
            page.get_by_role("button", name=re.compile("Russets")).click()
            expect(page.locator("#picking-title")).to_contain_text("Russets")
            button = page.get_by_role("button", name="Reserve picking")
        page.get_by_role("radio", name=re.compile("14:00")).check()
        button.click()
        expect(page.get_by_text(re.compile("Reservation confirmed"))).to_be_visible()
        confirmation={"A":"#confirmation","B":"#confirmation-title","V":"#confirmed-title"}[arm]
        expect(page.locator(confirmation)).to_contain_text("14:00")
        if arm == "B":
            expect(page.locator("#confirmed-row")).to_contain_text("Russets")
        if arm == "V":
            expect(page.locator("#confirmed-details")).to_contain_text("Russets")


def contact(path, case, view, state, arms):
    files = [path/f"{case}-{arm}-{view}-{state}.png" for arm in arms]
    pics = [Image.open(f).convert("RGB") for f in files]
    limit = 690 if view == "desktop" else 390
    pics = [ImageOps.contain(im, (limit,840)) for im in pics]
    width = sum(p.width for p in pics)+16
    canvas = Image.new("RGB",(width,max(p.height for p in pics)), "#c4c4c4")
    canvas.paste(pics[0],(0,0));canvas.paste(pics[1],(pics[0].width+16,0))
    canvas.save(path/f"{case}-{view}-{state}-{''.join(arms)}.jpg", quality=89)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pages",type=Path)
    ap.add_argument("out",type=Path)
    ap.add_argument("--visual",action="store_true",help="Include the matched V builds")
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel="chrome",headless=True)
        for case, arm, (view,size) in product(CASES,("A","B","V") if args.visual else ("A","B"),VIEWS.items()):
            ctx=browser.new_context(viewport=size,device_scale_factor=1,reduced_motion="reduce")
            ctx.route(re.compile(r"https?://"), lambda r:r.abort())
            page=ctx.new_page()
            err=[]; page.on("pageerror",lambda e:err.append(str(e)))
            page.goto((args.pages/f"{case}-{arm}"/"index.html").resolve().as_uri())
            key=f"{case}-{arm}-{view}"
            expect(page.get_by_role("heading",level=1)).to_have_count(1)
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            if case=="orchard":
                assert page.evaluate("Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)")
            coords=None
            if arm in ("B","V"):
                target="main summary" if case=="lab-loan" else "button.row-button"
                coords=page.locator(target).evaluate_all("es=>es.map(e=>Math.round(e.getBoundingClientRect().top))")
                assert len(coords)==(3 if case=="lab-loan" else 2)
            title_height=page.locator("h1").evaluate("e=>Math.round(e.getBoundingClientRect().height)")
            page.screenshot(path=args.out/f"{key}-first.png",animations="disabled")
            exercise(page,case,arm)
            page.screenshot(path=args.out/f"{key}-result.png",animations="disabled")
            assert not err, err
            results.append({"case":case,"arm":arm,"view":view,"main_flow":"pass","page_errors":err,
                            "opening_control_top_px":coords,"title_height_px":title_height})
            ctx.close()
            print(key,"passed",flush=True)
        browser.close()
    for case,view,state in product(CASES,VIEWS,("first","result")):
        contact(args.out,case,view,state,("A","B"))
        if args.visual:
            contact(args.out,case,view,state,("B","V"))
    (args.out/"checks.json").write_text(json.dumps(results,indent=2)+"\n")


if __name__=="__main__":
    main()
