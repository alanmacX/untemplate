"""Generate independent briefs and renderable pages; all inputs here are synthetic."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import re

HERE=Path(__file__).resolve().parent
RUN_SPEC=importlib.util.spec_from_file_location("reference_runner",HERE.parent/"creative-pilot"/"run.py")
base=importlib.util.module_from_spec(RUN_SPEC);RUN_SPEC.loader.exec_module(base)
CASES=json.loads((HERE/"cases.json").read_text())
V11=(HERE/"v11-entry.md").read_text()
COPY="""开写前列出页面要真正提供的信息和操作。标题直接给实际对象或任务；主区或分区的标题上方没有预留标签槽。不得生成没有独立信息的眉题、重复副标题、标题译文、标签或口号，包括英文、缩写、视觉装饰、自绘或 CSS 伪元素文字。每句短文案都能说出删掉后人会失去什么事实、状态、操作提示或必要辨认；说不出就直接从 HTML 删除并收掉空容器。必要状态、时间、单位、操作标签、确有信息的栏目名留在对应对象旁。完成交付前按这条看整屏，与主要操作后的状态。"""
SIZES=(428393,518401,926017)
ANALOGIES=(
 "学校门口的值班员见到两拨来人时，先让他们按要去的入口分流，再分别核对纸条。",
 "修鞋的师傅先把东西和能当面判断的磨损一起摊开，不能判断的事留到检查后再说。",
 "剧场后台把所有人共用的换场表留在原处，只在受影响的一行贴上改动和下一步。",
)
MODEL="gpt-6.2-sol"

def project(c):
 return f"""需求：{c["brief"]}
实际资料：
"""+"\n".join("- "+x for x in c['facts'])+f'\n验收：{c["must"]}'

def run(args,c,arm,s=None):
 mode=args.mode
 p=project(c)
 if mode=="pages":
  method={"A":"","B":V11,"C":V11+"\n\n"+COPY}[arm]
  msg=f"""把这个需求做成一个视觉完整、桌面手机都可用的完整单页。含内联 CSS 和 JS，无第三方依赖、外网请求或工具调用。使用中文。资料属演示；不要补新的运营数据。执行实际交互，结果在页面上可见。首个可操作入口和提交文案保留验收中的名字，保证浏览器按它能重放；放结果的方式由你定。只输出从 <!DOCTYPE html> 到 </html>。\n\n{p}"""
  if method:msg+="\n\n设计说明（同样用于最终实现）：\n"+method
 elif mode=="routes":
  method=("本次探索种子："+str(s)+"。从这个随机种子切入，选一个有意义的方向。")
  fact=None
  if arm in ("drawn","analogy"):
   rng=random.Random(f'{c["id"]}:{SIZES}')
   facts=list(c["facts"]);rng.shuffle(facts)
   fact=facts[SIZES.index(s)]
   method+="\n先从种子抽中的这一条事实发问："+fact+"。让它实际改变一个首屏决定；仍完成原任务。"
  if arm=="analogy":
   cue=list(ANALOGIES);random.Random(f'cue:{c["id"]}:{SIZES}').shuffle(cue)
   cue=cue[SIZES.index(s)]
   method+="\n另外，想一次这个具体的场外做法："+cue+" 只考虑它安排信息或操作的关系是否能解决抽中事实里的问题。若合适，用它改变画面；不合适时照原事实推敲。保留原业务规则，只借关系。"
  msg=f"""独立给下面简报开一个方向。先想人怎么用，最后写出可画成屏幕的方案。只回 JSON，字段 premise（项目事实如何导向方案）、opening（桌面和手机先看到什么）、action（用户能辨认并真正做的第一步）、result（结果在哪、跟什么一起看）。每字段一句实际描述。不要列多案、写风格标签冒充观察、调用工具或编造事实。\n\n{p}\n\n{method}"""
 else: raise RuntimeError(mode)
 name=c["id"]+"-"+arm+(f"-{s}" if s else "")
 f=args.out/(name+(".html" if mode=="pages" else ".json"))
 f.parent.mkdir(parents=True,exist_ok=True)
 if f.exists(): return
 for i in range(2):
  raw,_=base.codex(msg,MODEL,effort="medium")
  if mode=="pages":
   value=re.search(r"<!doctype\s+html\b.*?</html\s*>",raw,re.I|re.S)
   if value:f.write_text(value.group(0)+"\n");break
  else:
   try:
    val=json.JSONDecoder().raw_decode(raw[raw.index("{"):])[0]
    assert all(val.get(k) for k in ('premise','opening','action','result'))
    f.write_text(json.dumps({"case":c["id"],"arm":arm,"seed":s,"focus":fact,"cue":cue if arm=="analogy" else None,"route":val},ensure_ascii=False,indent=2)+"\n");break
   except (ValueError,AssertionError):pass
 else: raise RuntimeError(name)
 print(mode,name,f.stat().st_size,flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("mode",choices=("pages","routes"))
 p.add_argument("out",type=Path)
 p.add_argument("--jobs",default=6,type=int)
 p.add_argument("--analogy",action="store_true",help="Run the later, exploratory cue-allocation arm")
 a=p.parse_args()
 reqs=[(c,x,None) for c in CASES for x in ("A","B","C")] if a.mode=="pages" else [(c,x,s) for c in CASES for s in SIZES for x in (("analogy",) if a.analogy else ("number","drawn"))]
 with ThreadPoolExecutor(max_workers=a.jobs) as ex:
  for f in [ex.submit(run,a,*rq) for rq in reqs]: f.result()

if __name__=="__main__": main()
