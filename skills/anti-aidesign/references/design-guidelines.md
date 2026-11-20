# 设计指南选用表

按任务挑依据。官方规范里的界面图可以作为观察对象；整页设计仍要打开与用户任务相近的实际区域，记录看到了什么。表里的取舍是可迁移的做法，品牌视觉、平台组件和技术阈值按项目决定。

| 用在哪 | 看哪一段 | 拿走什么／怎么检验 |
| --- | --- | --- |
| 标题、表单、操作文案 | [Microsoft Fluent 2：Content design](https://fluent2.microsoft.design/content-design/)的标题提纲和直接用词；[Atlassian：Typography](https://atlassian.design/foundations/typography)的语义标题；[GOV.UK：Labels, legends and headings](https://design-system.service.gov.uk/get-started/labels-legends-headings/)里的问题同时作为标题和表单分组名。 | 只读主标题应知道各段在做什么。适当用原生 label、fieldset 和 legend 保留表单关系；重复字视觉上藏起来后仍可能被读出，删减时一并检查可访问名称。 |
| 数据工作台与品牌展示 | [IBM Carbon：Productive and expressive type](https://www.carbondesignsystem.com/building-blocks/foundations/typography/style-strategies)的两种排版情境；[Apple：Typography](https://developer.apple.com/design/human-interface-guidelines/typography)的字号、字重、对比和文字放大。 | 高频比较让正文、字段和操作对齐；探索型页面可通过图像与大标题拉开节奏。把标题样式、正文样式和字段样式分别成组；用正常比例和放大后读一次关键字段。Apple 的平台 pt 尺寸不直接套到 Web。 |
| 名单＋详情、工作台＋辅助区、内容流 | [Google Android／Material 3：Common layouts](https://developer.android.com/design/ui/mobile/guides/layout-and-content/common-layouts)的 list–detail、feed、support pane 图；[GitHub Primer：Layout](https://primer.style/product/getting-started/foundations/layout/)的 full、split 和 interstitial 页面。 | 比较时可保留桌面两栏；手机可顺序进详情并返回原选择。辅助设置可以按需打开；浏览型集合可以网格呈现。按内容关系选布局，缩窄窗口实际点一遍。 |
| 有明确动作的管理页 | [Shopify：App layout](https://shopify.dev/docs/apps/design/layout)的区块标题和主操作；[Apple：Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)里关于熟悉模式与简洁取舍的做法。 | 给当前任务的主操作一个明确位置，对照同级动作的视觉权重。优先把业务内容或可操作区域带进首屏。 |
| 品牌取材与手机可读性 | [IBM：Photography](https://www.ibm.com/design/language/photography/overview/)按用途选图；[Figma：品牌视觉改版](https://www.figma.com/blog/figma-on-figma-evolving-our-visual-language/)把选区节点做成识别符号；[W3C WAI：Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)说明手机重排和二维内容的边界。 | 让素材为具体对象提供辨识、证据或上下文。窄屏不靠隐藏交互或关键字段适配；主操作和正文仍可读可用。 |

对比一组页面时，先看彩色完整页面和手机视口，比较素材、强调方式和页面如何结束；需要判断相似性究竟来自配色还是结构时，再看灰度。相近业务保留熟悉的交互；若视觉关系跨任务可以整套互换，回到内容找原因。素材和页尾的取舍见[视觉决策](visual-decisions.md)。
