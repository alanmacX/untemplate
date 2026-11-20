"""Record browser-resolved type and narrow-screen clipping; no visual quality score."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    p=argparse.ArgumentParser()
    p.add_argument("pages",type=Path)
    p.add_argument("out",type=Path)
    args=p.parse_args()
    rows=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(channel="chrome")
        for file in sorted(args.pages.glob("*/index.html")):
            for width,height in ((1440,1000),(390,844),(320,844)):
                t=b.new_page(viewport={"width":width,"height":height})
                try:
                    t.goto(file.resolve().as_uri())
                    t.evaluate("document.fonts.ready")
                    c=t.context.new_cdp_session(t)
                    c.send("DOM.enable"); c.send("CSS.enable")
                    doc=c.send("DOM.getDocument")["root"]["nodeId"]
                    targets=[]
                    for selector in ("h1","main p","main button"):
                        el=t.locator(selector).filter(visible=True).first
                        if not el.count():
                            continue
                        desc=el.evaluate("""e => {
                          const s=getComputedStyle(e), r=e.getBoundingClientRect();
                          const q=document.createRange();q.selectNodeContents(e);
                          return {text:e.textContent.trim().replace(/\\s+/g,' '), family:s.fontFamily,
                           size:parseFloat(s.fontSize), weight:s.fontWeight, line_height:s.lineHeight,
                           letter_spacing:s.letterSpacing,
                           content_fits:Array.from(q.getClientRects()).every(x=>x.left>=-0.5&&x.right<=innerWidth+.5),
                           top:Math.round(r.top), bottom:Math.round(r.bottom)};
                        }""")
                        el.evaluate("e=>e.setAttribute('data-untype-audit','1')")
                        node=c.send("DOM.querySelector",{"nodeId":doc,"selector":"[data-untype-audit]"})["nodeId"]
                        desc["font_faces"]=[{"family":f["familyName"],"glyphs":f["glyphCount"]} for f in
                              c.send("CSS.getPlatformFontsForNode",{"nodeId":node})["fonts"]]
                        el.evaluate("e=>e.removeAttribute('data-untype-audit')")
                        targets.append({"selector":selector, **desc})
                    overflow=t.evaluate("document.documentElement.scrollWidth>innerWidth")
                    t.add_style_tag(content="""
                      * { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; }
                      p { margin-block-end: 2em !important; }
                    """)
                    stress=t.evaluate("document.documentElement.scrollWidth>innerWidth")
                    rows.append({"page":file.parent.name,"width":width,
                                 "horizontal_overflow":overflow,"spacing_stress_overflow":stress,
                                 "targets":targets})
                finally:
                    t.close()
        b.close()
    args.out.write_text(json.dumps(rows,indent=2)+"\n")


if __name__=="__main__":
    main()
