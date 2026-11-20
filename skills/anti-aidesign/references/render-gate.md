# 用浏览器检查具体承诺

适用于整页改造或跨页面对照。脚本要用 Python、Playwright 和 Chromium；可以指定已安装的 Chrome。使用本地站点或在授权范围内测试的站点。没有自动化时，用浏览器按同样的语义做手测，不把截图当交互通过。

配置示例：
```json
{"pages":[{"id":"sample","path":"booking/","entry":"#select-date",
  "keep":[{"name":"确认前有缴费条件","selector":"#fee-terms","text":"到院后缴费","first_view":true}],
  "drop":[{"name":"重复服务名的尾栏","selector":".redundant-footer"}],
  "measure":[{"name":"可比较的日期","selector":"#dates button"}],
  "negative_control":"#fee-terms"}]}
```

`path` 相对本地根地址；`entry` 选首要任务的真实操作目标，浏览器检查可见、未禁用且点击点未被遮住。`keep` 规则的 `min` 默认为 1，可选 `viewports`（`desktop` 和 `mobile`）和 `first_view`。选择器指向实际的可见字段或控件，不指向自报的状态或证据标记。`drop` 查 DOM，总数必须为零；把旧元素隐藏仍失败。`measure` 记录位置、数量和首屏可见数。`baseline_probe` 可提供一个原版元素选择器，只在冻结的原版临时隐藏它，再记坐标判断「只拿掉装饰」能否解决问题。若要验证脚本会发现回归，用 `--self-check` 暂时隐藏一处该保留的元素。脚本同时记录水平溢出和运行时错误。

```sh
python scripts/render_gate.py checks.json out --channel chrome \
  --baseline http://127.0.0.1:8000/original/ \
  --candidate http://127.0.0.1:8000/revised/ --self-check
```

只传 `--candidate` 也可检查最终版本。候选有失败会返回非零。比较 `browser-gate.json` 与实际原图，不能拿 DOM 标记推测审美。另用主流程测试确认证据，例如点击时段后人数或余号实际改变、刷新后能回查，或者听到样例录音并能跳到指定进度。两套页面用同样的记录、浏览器、视口与状态，置信度更高。不要把实测数据阈值复制到其他产品。

对[删除检查](copy-gate.md)判定的眉题或重复解释，用确切 DOM 选择器加进 `drop`；对被合并的独立信息加一条 `keep`。结果状态另点开检查；伪元素、SVG 中的文字和更换语言后的重复另查实际画面。


## 选稿阶段同样用实际页面

主方向还没决定时，让两张小样用同一份记录，在相同桌面和手机尺寸都能走到主要结果。用主要任务和事实先筛选，再按截图比较对象是否更好找、结果是否留在可理解的位置、环境与素材是否真的改变了可见布局。截图记首屏和关键状态即可。只改变皮肤的候选回到实物或任务关系重新起稿。最终成品检查选定关系和主要结果还在。
