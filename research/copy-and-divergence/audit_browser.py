"""Read rendered copy, exercise the synthetic briefs, and record actual H1 fonts."""
import argparse,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from PIL import Image,ImageOps

HERE=Path(__file__).resolve().parent
CASES={x["id"]:x for x in json.loads((HERE/"cases.json").read_text())}
VIEW={"desktop":(1440,1000),"phone":(390,844)}
NODES=r"""() => {
 const visible=e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0&&e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});
 const items=Array.from(document.querySelectorAll('body *')).filter(e=>!e.matches('script,style,noscript,svg, [aria-hidden=true]')&&visible(e));
 const clean=t=>t.replace(/\s+/g,' ').trim();
 const out=[];
 for(const e of items){
   const text=clean(Array.from(e.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join(' '));
   const s=getComputedStyle(e);
   const pseudo=['::before','::after'].map(n=>getComputedStyle(e,n).content).filter(c=>!['none','normal','""',"''"].includes(c));
   if(!text&&!pseudo.length) continue;
   const rect=e.getBoundingClientRect();
   out.push({tag:e.tagName.toLowerCase(),class:e.getAttribute('class'),id:e.id||null,
           text, pseudo,x:Math.round(rect.left),y:Math.round(rect.top+window.scrollY),size:parseFloat(s.fontSize)});
 }
 return out;
}"""
def has(page,pattern):
    expect(page.get_by_text(re.compile(pattern)).filter(visible=True).first).to_be_visible(timeout=2200)
def first_named(page,text):
    return page.get_by_role("button",name=re.compile(re.escape(text))).filter(visible=True).first
def flow(page,c):
    a,b,r=c["action"]; named=True
    if c["id"]=="trail":
        result=page.locator("#route-result")
        assert not result.is_visible() or not result.inner_text().strip(), "result already present"
        radio=page.get_by_role("radio",name=re.compile(a)).filter(visible=True).first
        if radio.count():radio.check(timeout=2000)
        submission=first_named(page,a)
        if not submission.count():submission=first_named(page,"查看可达结果")
        submission.click(timeout=2000)
        expect(result).to_be_visible(timeout=2200)
        expect(result).to_contain_text("西口");expect(result).to_contain_text("桥北")
        expect(page.get_by_role("button",name=re.compile("封闭|临河台阶"))).to_have_count(0)
        return True
    expect(page.get_by_text(r,exact=True).filter(visible=True)).to_have_count(0)
    loc=first_named(page,a)
    if not loc.count():
        loc=page.get_by_text(a,exact=True).filter(visible=True).first
    loc.click(timeout=2000)
    if c["id"]=="books":
        has(page,"北门");has(page,"自提架");has(page,r"10:00\s*[-–—至]\s*12:00")
    if b: first_named(page,b).click(timeout=2000)
    has(page,r)
    has(page,a)
    return named

def font(page):
    page.evaluate("document.fonts.ready")
    h=page.locator("h1").first
    if not h.count():return None
    style=h.evaluate("e=>({family:getComputedStyle(e).fontFamily,size:getComputedStyle(e).fontSize,weight:getComputedStyle(e).fontWeight,spacing:getComputedStyle(e).letterSpacing})")
    c=page.context.new_cdp_session(page)
    c.send("DOM.enable");c.send("CSS.enable")
    doc=c.send("DOM.getDocument")["root"]["nodeId"]
    h1=c.send("DOM.querySelector",{"nodeId":doc,"selector":"h1"})["nodeId"]
    return {**style,"actual":[r["familyName"] for r in c.send("CSS.getPlatformFontsForNode",{"nodeId":h1})["fonts"]],"lang":page.locator("html").get_attribute("lang")}
def render(browser,f,mode,dim,out):
    w,h=dim
    c=browser.new_context(viewport={"width":w,"height":h},reduced_motion="reduce")
    c.route(re.compile(r"https?://"),lambda r:r.abort())
    p=c.new_page()
    errors=[];p.on("pageerror",lambda e:errors.append(str(e)))
    p.goto(f.resolve().as_uri())
    p.evaluate("document.fonts.ready")
    key=f.stem+"-"+mode
    a={"page":f.stem,"mode":mode,"opening":p.evaluate(NODES),"type":font(p),
       "horizontal_overflow":p.evaluate("document.documentElement.scrollWidth>innerWidth")}
    p.screenshot(path=out/(key+"-first.png"))
    try:
        a["exact_named_flow"]=flow(p,CASES[f.stem.split("-")[0]])
        a["task_replay"]=True
    except Exception as e:
        a.update(task_replay=False,exact_named_flow=False,replay_error=str(e)[:300])
    a["runtime_errors"]=errors;a["result"]=p.evaluate(NODES)
    p.screenshot(path=out/(key+"-result.png"))
    c.close()
    return a

def compare(out,case,mode,state):
    pics=[ImageOps.contain(Image.open(out/f"{case}-{arm}-{mode}-{state}.png").convert("RGB"),(500 if mode=="desktop" else 340,780)) for arm in "ABC"]
    canvas=Image.new("RGB",(sum(im.width for im in pics)+20,max(im.height for im in pics)),"#a7a7a7")
    x=0
    for im in pics:canvas.paste(im,(x,0));x+=im.width+10
    canvas.save(out/f"{case}-{mode}-{state}-ABC.jpg",quality=88)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("pages",type=Path)
    p.add_argument("out",type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        b=pw.chromium.launch(channel="chrome")
        rows=[render(b,f,mode,dim,a.out) for f in sorted(a.pages.glob("*.html")) for mode,dim in VIEW.items()]
    (a.out/"audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n")
    for x in rows:print(x["page"],x["mode"],x["task_replay"],x["exact_named_flow"],x["type"],flush=True)
    for c in CASES:
        for v in VIEW:
            for s in ("first","result"):
                compare(a.out,c,v,s)
if __name__=="__main__":main()
