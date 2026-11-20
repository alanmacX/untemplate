from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)

def fonts(page):
    js=page.context.new_cdp_session(page)
    js.send("DOM.enable");js.send("CSS.enable")
    doc=js.send("DOM.getDocument")["root"]["nodeId"]
    result={}
    for selector in ("h1","p","time","button"):
        node=js.send("DOM.querySelector",{"nodeId":doc,"selector":selector})["nodeId"]
        result[selector]=[(r["familyName"],r["glyphCount"]) for r in js.send("CSS.getPlatformFontsForNode",{"nodeId":node})["fonts"]]
    return result

with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chrome")
    rows=[]
    for width in (390,320):
        page=b.new_page(viewport={"width":width,"height":520})
        for style in ("legacy","hei","song"):
            page.goto((HERE/"specimen.html").as_uri()+"#"+style)
            page.reload()
            page.evaluate("document.fonts.ready")
            face=fonts(page)
            height=page.locator("h1").evaluate("e=>Math.round(e.getBoundingClientRect().height)")
            rows.append({"width":width,"style":style,"glyphs":face,"height":height,"horizontal_overflow":page.evaluate("document.documentElement.scrollWidth>innerWidth")})
            page.screenshot(path=OUT/f"{style}-{width}.png")
        page.close()
    b.close()
(OUT/"specimen-fonts.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
