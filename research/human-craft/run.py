"""Compare reasoning inputs while building from the same brief, materials and functional test."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import re
import subprocess,tempfile

D=Path(__file__).resolve().parent
CASES=json.loads((D/"cases.json").read_text())
V12=(D/"v12-entry.md").read_text()
BASE="""只做一个中文单页，从过渡首屏到使用结果。纯 HTML/CSS/JS，无依赖和网络请求，不调用工具。已有真实资料与素材都能用。保留准确内容、不编造业务规则。显示可访问的独立主标题，实际任务和结果得能走通。移动端宽度 390px。可引用指定本地路径，不做额外素材。返回一个完整 HTML，允许小于 15KB。"""
TRACE="""先把你当成给具体材料做一个小工具或一本小出版物的人。只做一件可检验的事：用真实文字或原图，排出被人实际拿来辨认、对照或操作的最小单元及一次状态变化，先放它在画面上。做两种粗排，指出哪一处比例或组织因这个项目而必须这样，并说清两种方案各自的牺牲；选一份。把真正有用的原材料、在移动端的位置或阅读关系、变化前后同时可见的内容完整交接。设计此处时先别补主页壳。只要简短结构草稿和关系，不写成品，不列风格形容词。"""
PRESERVE="""照这个已定设计判断做小页面：把下方草稿中最关键的材料、第一眼读序和状态关系体现在页面上，检查桌面和手机看得见。先用这个实际单元做主画面，再填必要的主标题、导航和说明。可按端适配，但不要在上方另垫一层泛用介绍或加给空槽的文字。最终构图由这批材料决定。"""

def model(prompt, assets):
 with tempfile.TemporaryDirectory(prefix="human-craft-") as temp:
  cmd=["codex","exec","--ignore-user-config","--skip-git-repo-check","--ephemeral","--sandbox","read-only","-C",temp,"-m","gpt-6.2-sol","-c",'model_reasoning_effort="medium"',"--json"]
  for a in assets:cmd.extend(("-i",str(a.resolve())))
  child=subprocess.run(cmd+["-"],encoding="utf-8",capture_output=True,input=prompt,timeout=220)
  if child.returncode: raise RuntimeError(child.returncode)
  js=[json.loads(x) for x in child.stdout.splitlines() if x.startswith("{")]
  final=[j["item"]["text"] for j in js if j["type"]=="item.completed" and j["item"]["type"]=="agent_message"]
  return final[-1]

def run(out,c,arm):
 dest=out/f"{c['id']}-{arm}";dest.mkdir(parents=True,exist_ok=True)
 facts=f"简报：{c['brief']}\n资料："+'\n'.join(c["facts"])+f"\n操作要求：{c['accept']}"
 ref="\n真人作品观察：\n"+c["refs"] if arm!="A" else ""
 assets=[out/"assets"/p for p in ("baldwin.jpg","adirondack.jpg")] if c["id"]=="plates" else []
 assert all(i.exists() for i in assets)
 trace=""
 if arm=="C":
  plan=model(f"{facts}{ref}\n{TRACE}",assets)
  (dest/"working-unit.md").write_text(plan+"\n")
  trace=f"\n{PRESERVE}\n粗排交接：\n{plan}"
 if arm=="D":
  plan=(out/f"{c['id']}-C"/"working-unit.md").read_text()
  trace=f"\n{PRESERVE}\n粗排交接：\n{plan}\n这次只做原交接里没有选中的另一稿。使用它实际安排内容的关系；去掉对已选稿的引用和混合。不漏任务。"
 text=f"{BASE}\n{V12}\n{facts}{ref}{trace}\n只回完整 HTML。"
 raw=model(text,assets)
 m=re.search(r"<!doctype\s+html\b.*?</html\s*>",raw,re.I|re.S)
 if not m: raise ValueError("No HTML for "+dest.name)
 (dest/"index.html").write_text(m.group(0)+"\n")
 return dest.name

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("out",type=Path)
 p.add_argument("--jobs",type=int,default=6)
 p.add_argument("--alternate",action="store_true",help="Later probe: build the discarded concept from the frozen C handoff")
 a=p.parse_args()
 with ThreadPoolExecutor(max_workers=a.jobs) as ex:
  jobs=[ex.submit(run,a.out,c,arm) for arm in ("D" if a.alternate else "ABC") for c in CASES]
  for f in as_completed(jobs): print(f.result(),flush=True)
