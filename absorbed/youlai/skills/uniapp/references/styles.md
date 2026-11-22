# UnoCSS 与 BEM

## 样式归属

| 场景                         | 项目约定                       |
| ---------------------------- | ------------------------------ |
| 页面外层排版、网格、区域间距 | UnoCSS                         |
| 业务组件内部布局与外观       | BEM + scoped SCSS              |
| 组件选中、禁用等变体         | BEM modifier，由 `:class` 控制 |
| 跨页复用的纯布局组合         | UnoCSS shortcut                |
| 运行时测量尺寸、进度         | style / CSS 变量               |

- 同一节点的同一属性只维护一处；已有 BEM 类的内部样式不再叠加原子类。
- 使用方可控制组件外部间距与占位，组件内不重复定义这些属性。
- 滚动区留白优先放内层内容容器；若直接设置 `scroll-view` 的 padding，核对盒模型、滚动宽度和末端留白，避免溢出或裁切。
- 多组条件颜色、圆角、阴影改用语义 modifier；组件私有组合留在 SCSS。
- 只为实际复用的布局建立 shortcut；含结构和行为的复用提取组件，不因缩短模板新增编译插件。
- 动态原子类使用完整类名映射、safelist 或 CSS 变量，不运行时拼接类名。

依据：[UnoCSS shortcuts](https://unocss.dev/config/shortcuts)、[提取规则](https://unocss.dev/guide/extracting)。

## BEM

| 对象     | 格式                          |
| -------- | ----------------------------- |
| 组件块   | `user-card`                   |
| 内部元素 | `user-card__avatar`           |
| 块变体   | `user-card--selected`         |
| 元素变体 | `user-card__action--disabled` |

- 使用小写和连字符；名称表达职责或状态，不写死颜色、尺寸。
- modifier 与基础类同时使用；不使用 `block__a__b` 或 `block--state__element`。
- Element 表达归属，不照抄 DOM 层级；独立复用部分成为新 Block。
- SCSS 用 `&__element`、`&--modifier` 展开；避免深层后代选择器，以类选择器为主。

依据：[GetBEM](https://getbem.com/faq/)。

## 主题与跨端

- 业务颜色来自 CSS 语义变量；UnoCSS 语义类须有规则或 theme 映射。
- 字号、间距、圆角优先复用项目主题或已有阶梯；不将 iOS 的 pt、CSS px 与 rpx 直接视为通用等价关系。
- 图标大小与点击区域分别设置，结合文字和场景确定；数字 `size` 的单位以安装组件版本为准，不能固定假设 `1px = 2rpx`。
- 同一语义选用同一图标；图标名以安装版本的 `wd-icon` 清单为准，不凭记忆书写。
- Wot 外观按 props、主题变量、custom-class/style、内部选择器的顺序处理。
- 设计比例尺寸沿用 rpx；系统几何 API 返回的 px 保持同单位计算。图标尺寸与点击区域分开设置。
- 主色及其浅深色、前景文字同步；深色模式覆盖弹层和反馈，原生导航单独同步。
- `:deep`、伪元素、样式隔离按目标平台核对；不默认全局 shared 或用 `!important` 压制冲突。
- z-index 按内容、固定控件、遮罩、弹层统一管理，并检查堆叠上下文。

依据：[uni-app 样式](https://uniapp.dcloud.net.cn/tutorial/syntax-css.html)、[Vue SFC CSS](https://vuejs.org/api/sfc-css-features.html)。
