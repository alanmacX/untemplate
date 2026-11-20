# 案例和依据

## Ember：对齐、层级、业务含义

用户提供的 `rednote-1.MP4`（约 10 秒，无音轨）演示同一财务概览的重排：

- 约 00:01–00:03，参考线量间距，主区标题和卡片共用左边线。借它的检查动作，用实际画面找漂移；具体像素值按项目尺寸系统决定。
- 约 00:03–00:07，减去大面积紫光，用明暗和边框表达表面；侧栏 emoji 换为统一图标，套餐彩点留下，普通计数回归文字。最终图表仍带彩色曲线和微光，颜色继续承担数据区分。
- 约 00:07–00:09，`Welcome back, Damir!` 换成 `October 2026`；`+12%!!` 换成 `+12% vs last month`。照片、插画和图表格式按业务任务单独判断，保留真实值和数据语义。

可迁移的做法：如果 Ember 的日常任务是追账，让「7 张逾期发票」直接打开可操作的列表，优先显示逾期最久的记录；如果任务是月度复盘，优先显示收入趋势、周期和对照。用同样的记录验两种结构：能否找到应处理的发票，或回答收入变化多少、和何时相比。这个延伸是设计示例。

## 找参考时看哪一段

| 任务 | 看哪里 |
| --- | --- |
| 密集工作台 | [Linear 改版](https://linear.app/now/behind-the-latest-design-refresh)有侧栏、标签栏和边框的前后图：辅助区域能退后，信息密度可以保留。[Ant Design 数据列表](https://ant.design/docs/spec/data-list-cn/)按用户的阅读方式比较表格、列表和卡片。 |
| 品牌页、作品展示 | [Figma 品牌改版](https://www.figma.com/blog/figma-on-figma-evolving-our-visual-language/)把产品选区节点放大成可识别的品牌图形；[OpenAI 前端设计指南](https://developers.openai.com/blog/designing-delightful-frontends-with-gpt-5-4)提供首屏聚焦和素材选择的例子。参考具体视觉关系，不把某一种首屏构图套给所有页面。 |
| 数据和异常状态 | [Grafana 仪表盘指南](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)从页面要回答的问题出发；[英国政府图表指南](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/)有线尾标签和缺数断点示例；[IBM Carbon 空状态](https://v10.carbondesignsystem.com/patterns/empty-states-pattern/)和 [GOV.UK 错误提示](https://design-system.service.gov.uk/components/error-message/)可参考文案和恢复动作；[W3C 中文排版需求](https://www.w3.org/TR/clreq/)可查数字与单位的断行细节。 |

## 研究对应的检查动作

- [One Tool, One Taste?](https://arxiv.org/abs/2609.38183)观察到一组 Lovable 宣传站在居中首屏、暖色／蓝色强调和字体上集中。检查同一份内容的布局草图是否真正不同，尤其是主模块和扫读顺序。
- [Design Theater](https://arxiv.org/abs/2607.22928)的五工具样本中，布局比颜色更趋同，有些设计解释没有落实到产物。打开实际页面操作，按界面呈现的结果验收。
- [网站第一印象研究](https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/)发现，视觉复杂度低且符合观众对网站类型预期的截图得到更高审美评价。把熟悉感用在约定俗成的交互上，给本产品的内容和品牌留下表达空间。
