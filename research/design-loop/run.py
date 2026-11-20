"""Two briefs: an expressive new piece and a redesign with working invariants."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import argparse,importlib.util,json,re,shutil
from playwright.sync_api import sync_playwright
from PIL import Image

HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("craft",HERE.parent/"human-craft"/"run.py")
base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
V13=(HERE/"v13-entry.md").read_text()
CASES=json.loads((HERE/"cases.json").read_text())
COMMON="""实现这个 brief，中文单页，桌面和手机都能看。单个 HTML 内置 CSS 和 JS，除给定的本地素材外无需依赖或网络。不调用工具。保住用户正文和事实。交付完整 HTML，可在前面给最多三行外部设计笔记，不把笔记预埋到产品。"""
NEW="""规划前做一次设计判断：想象人从哪一刻进入，什么能让人第一眼停下、什么余味留在最后。先把素材按一种有观点的关系排在画面里（例如哪个成为主角、哪里压低或停住；自行选）。用实际字、图、色、空间和节奏做出这个关系；别先选站点壳或形容词套餐。对于已有页，从现有画面指出一个应当留下的强项和一个像自动套上的关系；只改影响感受的部分，既有内容和功能保留。对于只用于观看的页面，别为测试或看起来完整自造功能，画面和阅读本身可以成立。明确哪些可见判断以小样来检验。无须解释推理过程；如写笔记，只写可核对的取舍。"""
REVIEW="""这两张是你刚生成的小样的实拍浏览器截图（桌面、手机）。先从图上找一个你没得到想要效果的可见关系：例如第一眼被哪件东西抢走，视线断在哪，哪段该慢却读得很赶，或作品身份被外框夺走。指出屏幕上的证据，再做一到两处实际调整，保住画面已经成立的部分和原 brief、内容及功能。无需增加文字、功能或全面换皮。允许保留已经合适的部分。回复最多三行可核对的改动说明，再给完整 HTML。"""

def snapshot(out,html,tag):
    paths=[]
    with sync_playwright() as pw:
        b=pw.chromium.launch(channel="chrome")
        for view,w,h in (("desktop",1440,1000),("phone",390,844)):
            p=b.new_page(viewport={"width":w,"height":h},reduced_motion="reduce")
            p.route(re.compile(r"https?://"),lambda r:r.abort());p.goto(html.resolve().as_uri())
            p.evaluate("document.fonts.ready")
            dst=out/f"{tag}-{view}.png";p.screenshot(path=dst,animations="disabled");paths.append(dst);p.close()
        b.close()
    return paths

def build(out,c,arm,origin):
    d=out/f'{c["id"]}-{arm}';d.mkdir(exist_ok=True)
    material=""
    photos=[]
    if "source" in c:
        src=origin/"index.html"
        material="\n现有 HTML：\n"+src.read_text()
        photos.extend([out/"plates-original-desktop.png",out/"plates-original-phone.png"])
    prompt=f'{COMMON}\n用户简报：{c["brief"]}\n必要原文：'+json.dumps(c["copy"],ensure_ascii=False)+material
    if arm=="A":prompt+=f"\n这是可用的设计 skill：\n{V13}"
    else:prompt+=f"\n这是可用的设计 skill：\n{V13}\n本次按以下判断补充：\n{NEW}"
    txt=base.model(prompt,photos)
    path=write(d,txt)
    snapshot(out,path,f'{c["id"]}-{arm}')
    print("built",c["id"],arm,flush=True)
    if arm=="B":
        feedback(out,c)

def feedback(out,c):
    cid=c["id"]
    cdir=out/f'{cid}-C';cdir.mkdir(exist_ok=True)
    before=out/f'{cid}-B'/"index.html"
    imgs=[]
    for view in ("desktop","phone"):
        png=out/f'{cid}-B-{view}.png'
        jpg=png.with_suffix('.jpg')
        with Image.open(png) as src:
            im=src.convert("RGB");im.thumbnail((1050,860));im.save(jpg,quality=88)
        imgs.append(jpg)
    text=base.model(f'{COMMON}\n{REVIEW}\n用户简报：{c["brief"]}\n必要原文：'+json.dumps(c["copy"],ensure_ascii=False)+"\n本轮小样 HTML：\n"+before.read_text(),imgs)
    p=write(cdir,text);snapshot(out,p,f'{cid}-C')
    print("render feedback",cid,flush=True)

def write(d,txt):
    m=re.search(r"<!doctype\s+html\b.*?</html\s*>",txt,re.I|re.S)
    if not m:raise ValueError("missing HTML "+str(d))
    out=d/"index.html";out.write_text(m[0]+"\n")
    notes=re.sub(r'\s*```[a-zA-Z0-9-]*\s*$', '',txt[:m.start()]).strip()
    if notes:(d/"notes.md").write_text(notes+"\n")
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("out",type=Path)
    p.add_argument("--feedback-only",choices=[c["id"] for c in CASES]);a=p.parse_args()
    outset=a.out
    if a.feedback_only:
        feedback(outset,next(c for c in CASES if c["id"]==a.feedback_only));raise SystemExit(0)
    (outset/"assets").mkdir(parents=True,exist_ok=True)
    for f in (HERE.parent/"human-craft/evidence/pages/assets").glob("*.jpg"):
        shutil.copyfile(f,outset/"assets"/f.name)
    origin=outset/"plates-original";origin.mkdir(exist_ok=True)
    shutil.copyfile(HERE.parent/"human-craft/evidence/pages/plates-A/index.html",origin/"index.html")
    snapshot(outset,origin/"index.html","plates-original")
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(build,outset,c,arm,origin) for c in CASES for arm in "AB"]):f.result()
