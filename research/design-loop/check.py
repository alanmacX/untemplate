"""Render and validate expressive text and preserved redesign invariants."""
import argparse,importlib.util,json,re
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from playwright.sync_api import sync_playwright,expect

HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("prior",HERE.parent/"human-craft/check.py")
p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
CASES={x["id"]:x for x in json.loads((HERE/"cases.json").read_text())}
VIEW={"desktop":(1440,1000),"phone":(390,844),"narrow":(320,760)}
PROBE=r"""() => {
const rect=e=>{const r=e.getBoundingClientRect();return [r.x,r.y+window.scrollY,r.width,r.height].map(Math.round)};
const visible=e=>{const r=e.getBoundingClientRect();return e.checkVisibility({checkVisibilityCSS:true,checkOpacity:true})&&r.width>0&&r.height>0};
const info=e=>({text:e.innerText.trim().replace(/\s+/g,' '),rect:rect(e),size:getComputedStyle(e).fontSize});
return {heading:Array.from(document.querySelectorAll('h1')).filter(visible).map(info),
  paragraphs:Array.from(document.querySelectorAll('main p, main h2')).filter(visible).map(info).slice(0,18),
  images:Array.from(document.querySelectorAll('main img')).filter(visible).map(e=>({src:e.getAttribute('src'),rect:rect(e),loaded:e.complete&&e.naturalWidth>0})),
  interactive:Array.from(document.querySelectorAll('button,input,select,a[href],[role=button]')).filter(visible).map(info),
  fullHeight:document.documentElement.scrollHeight,background:getComputedStyle(document.body).backgroundColor,
  overflow:document.documentElement.scrollWidth>innerWidth}; }"""

def check_tide(page,c):
   els=[]
   for t in c["copy"]:
       x=page.get_by_text(t,exact=True).filter(visible=True)
       expect(x).to_have_count(1)
       els.append(x)
   begins=[];lines=[]
   for e in els:
       e.scroll_into_view_if_needed()
       expect(e).to_be_visible()
       assert e.evaluate("e=>e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})"), "Text is visually hidden"
       begins.append(e.evaluate("(e)=>Math.round(e.getBoundingClientRect().y+window.scrollY)"))
       lines.append(e.evaluate(r"""e=>{
         const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const m=new Map();
         while(w.nextNode()){
           const n=w.currentNode;
           for(let i=0;i<n.length;i++){
             const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);const b=r.getBoundingClientRect();
             if(b.width>0){const y=Math.round(b.y);m.set(y,(m.get(y)||'')+n.data[i])}
           }
         }
         return Array.from(m.entries()).sort((a,b)=>a[0]-b[0]).map(x=>x[1].trim()).filter(Boolean);
       }"""))
   assert begins==sorted(begins), begins
   return {"line_y":begins,"rendered_lines":lines}

def concat(out,case,view,state,arms):
   im=[ImageOps.contain(Image.open(out/f'{case}-{a}-{view}-{state}.png').convert("RGB"),
                        (510 if view=="desktop" else 340,750)) for a in arms]
   canvas=Image.new("RGB",(sum(i.width for i in im)+10*(len(im)-1),22+max(i.height for i in im)),"#dedede")
   g=ImageDraw.Draw(canvas);left=0
   for a,i in zip(arms,im):
       g.text((left+6,5),a,fill="black");canvas.paste(i,(left,22))
       left+=i.width+10
   canvas.save(out/f"{case}-{view}-{state}-{'-'.join(arms)}.jpg",quality=90)

def main():
   ap=argparse.ArgumentParser();ap.add_argument("pages",type=Path);ap.add_argument("out",type=Path);a=ap.parse_args()
   a.out.mkdir(parents=True,exist_ok=True);out=[]
   with sync_playwright() as pw:
       b=pw.chromium.launch(channel="chrome")
       for f in sorted(a.pages.glob("*/index.html")):
           case,arm=f.parent.name.split("-")
           for view,(w,h) in VIEW.items():
               c=b.new_context(viewport={"width":w,"height":h},reduced_motion="reduce")
               c.route(re.compile(r"https?://"),lambda r:r.abort())
               t=c.new_page();errors=[];t.on("pageerror",lambda e:errors.append(str(e)))
               t.goto(f.resolve().as_uri());t.evaluate("document.fonts.ready")
               name=f"{case}-{arm}-{view}"
               row={"case":case,"arm":arm,"view":view,"first":t.evaluate(PROBE)}
               t.screenshot(path=a.out/f"{name}-first.png")
               try:
                   assert not row["first"]["overflow"]
                   assert t.locator("html").get_attribute("lang").startswith("zh")
                   if case=="plates":
                       ims=row["first"]["images"]
                       assert len(ims)==2 and all(i["loaded"] and i["rect"][1]<h for i in ims)
                       first,second=(i["rect"] for i in ims)
                       assert max(first[1],second[1])<min(first[1]+first[3],second[1]+second[3]), "Images do not share a reading band"
                       row["both_fully_in_first"]=max(i["rect"][1]+i["rect"][3] for i in ims)<=h
                       p.tasks(t,case)
                   else:row.update(check_tide(t,CASES[case]))
                   assert not errors
                   row["pass"]=True
               except Exception as e:row.update({"pass":False,"error":str(e)[:280]})
               t.screenshot(path=a.out/f"{name}-end.png")
               out.append(row);c.close()
               print(name,row["pass"],row.get("error",""),flush=True)
       b.close()
   (a.out/"audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
   for case in ("plates","tide"):
       for view in ("phone","desktop"):
           for how in ("first","end"):
               concat(a.out,case,view,how,["original","C"] if case=="plates" else ["A","B","C"])
               if case=="plates":concat(a.out,case,view,how,["B","C"])
if __name__=="__main__":main()
