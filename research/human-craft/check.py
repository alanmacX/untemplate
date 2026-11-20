"""Replay both test tasks on desktop and mobile; create three-way phase comparisons."""
import argparse
import json
from pathlib import Path
import re
from PIL import Image, ImageOps, ImageDraw
from playwright.sync_api import expect,sync_playwright

MODES={"desktop":(1440,1000),"phone":(390,844)}
DEV=r"""() => {
const box=e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height].map(Math.round)};
const vis=e=>e.checkVisibility()&&e.getBoundingClientRect().width>1;
const typography=e=>{const s=getComputedStyle(e);return [s.fontFamily,s.fontSize,s.letterSpacing,s.fontWeight]};
const pick=(s)=>Array.from(document.querySelectorAll(s)).filter(vis).slice(0,7).map(e=>({text:e.innerText,box:box(e),type:typography(e)}));
return {heading:pick("h1"),firstAction:pick("label:has(input[type=radio]),button"),images:Array.from(document.querySelectorAll("main img")).filter(vis).map(e=>({box:box(e),fit:getComputedStyle(e).objectFit,src:e.getAttribute("src"),ok:e.naturalWidth>0})),bodyBackground:getComputedStyle(document.body).backgroundColor,overflow:document.documentElement.scrollWidth>innerWidth};
}"""

def pick(page,name):
   e=page.locator(f'input[type=radio][value="{name}" i]')
   assert e.count()==1
   label=e.evaluate("e=>!!e.closest('label') || !!(e.id&&document.querySelector('label[for='+CSS.escape(e.id)+']'))")
   if e.is_visible():
       e.check(timeout=2200)
   elif label:
       # Visually hidden native radio: click its real label and check the real state.
       if e.evaluate("e=>!!e.closest('label')"):
           e.locator("xpath=ancestor::label[1]").click(timeout=2200)
       else:
           page.locator('label[for="'+e.get_attribute('id')+'"]').click(timeout=2200)
   else:raise AssertionError("Control has no visible radio or label")
   expect(e).to_be_checked()
def seen(page,pat):
   expect(page.get_by_text(re.compile(pat,re.I)).filter(visible=True).first).to_be_visible(timeout=1800)
def tasks(page,case):
   if case=="film":
       for id,pat in (("C17",("三号自提格|3 号自提格","21:00")),("C24",("前台","16:00","划痕"))):
           pick(page,id)
           for p in pat:seen(page,p)
       seen(page,"19:00");seen(page,"18:00")
   else:
       action=page.get_by_role("button",name=re.compile("查看档案"))
       for id,info in (("Baldwin",("Ellen Isham Schutt","1909","POM00001363")),("Adirondack",("Deborah Griscom Passmore","1893","POM00001337"))):
           pick(page,id)
           if not page.get_by_text(info[2],exact=True).filter(visible=True).count():
               if action.filter(visible=True).count():action.filter(visible=True).first.click(timeout=1800)
           for i in info:seen(page,i)
       seen(page,"USDA")
       ims=page.locator('main img')
       assert ims.count()==2 and all(im.evaluate("e=>e.naturalWidth>0") for im in ims.all())
def contacts(s,case,mode,state,arms):
   lis=[ImageOps.contain(Image.open(s/f"{case}-{x}-{mode}-{state}.png").convert("RGB"),
                       (535 if mode=="desktop" else 355,780)) for x in arms]
   r=Image.new('RGB',(sum(i.width for i in lis)+12*(len(lis)-1),max(i.height for i in lis)+23),"#dedede")
   g=ImageDraw.Draw(r);x=0
   for i,a in zip(lis,arms):
       g.text((x+6,6),a,fill="black");r.paste(i,(x,23));x+=i.width+12
   r.save(s/f"{case}-{mode}-{state}-{arms}.jpg",quality=90)
def main():
   p=argparse.ArgumentParser();p.add_argument("pages",type=Path);p.add_argument("out",type=Path)
   args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
   results=[]
   with sync_playwright() as pw:
       b=pw.chromium.launch(channel="chrome")
       for f in sorted(args.pages.glob("*/index.html")):
           case,arm=f.parent.name.split("-")
           for mode,(w,h) in MODES.items():
               ctx=b.new_context(viewport={"width":w,"height":h},reduced_motion="reduce")
               ctx.route(re.compile(r"^https?://"),lambda r:r.abort())
               page=ctx.new_page();errs=[];page.on("pageerror",lambda e:errs.append(str(e)))
               page.goto(f.resolve().as_uri());page.evaluate("document.fonts.ready")
               key=f"{case}-{arm}-{mode}"
               record={"case":case,"arm":arm,"mode":mode,"opening":page.evaluate(DEV)}
               page.screenshot(path=args.out/f"{key}-first.png",full_page=False)
               try:
                   expect(page.get_by_role("heading",level=1)).to_have_count(1);tasks(page,case)
                   record["main_flow"]=True
               except Exception as e:
                   record.update(main_flow=False,error=str(e)[:320])
               record["runtime_errors"]=errs
               record["result"]=page.evaluate(DEV)
               page.screenshot(path=args.out/f"{key}-result.png",full_page=False)
               results.append(record);ctx.close();print(key,record["main_flow"],record.get("error",""),flush=True)
   (args.out/"audit.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
   for case in ("film","plates"):
       for mode in MODES:
           for state in ("first","result"):
               contacts(args.out,case,mode,state,"ABC")
               if (args.pages/f"{case}-D"/"index.html").exists():contacts(args.out,case,mode,state,"CD")
if __name__=="__main__":main()
