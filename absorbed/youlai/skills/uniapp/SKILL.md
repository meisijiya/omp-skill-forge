---
name: forge-uniapp
description: 用于 uni-app Vue 3 项目页面、接口、会话与跨端逻辑的开发、重构和审查。适用于 TypeScript、Wot UI、UnoCSS 工程；nvue 与 uni-app x 需另核对其平台规则。
---

# uni-app 开发规范

先读取 `package.json`、锁文件、Vite 配置及相关源码，确认目标平台，再按任务读取下表。依赖版本以项目为准；Wot v1/v2、uni-app 与 uni-app x 的 API 不混用。

命名、注释格式与样式分工是项目约定，框架机制以对应版本的官方文档为准。普通功能复用现有目录和封装，不为减少几行代码增加层次或依赖。

## 按需读取

| 任务                          | 规范                                             |
| ----------------------------- | ------------------------------------------------ |
| 文件、变量、函数、Store、事件 | [命名](references/naming.md)                     |
| 请求与响应类型、API 边界      | [类型与接口](references/types-api.md)            |
| 注释、TSDoc、TODO、编译指令   | [注释](references/comments.md)                   |
| UnoCSS、BEM、SCSS、主题       | [样式](references/styles.md)                     |
| 目录、分包、页面配置、布局    | [页面与布局](references/pages-layout.md)         |
| 会话续期、登录失效、WebSocket | [会话与实时连接](references/session-realtime.md) |
| 表单、分页、缓存、验收        | [质量检查](references/quality.md)                |

## 改动边界

- 查询类型统一 `UserQuery`，分页基础类型用 `PageQuery`；不要同时维护 `UserQueryParams`、`UserPageQuery` 等同义命名。
- 业务函数、方法、类、接口、类型和枚举使用展开的多行 JSDoc；简短字段说明可单行，局部实现原因用 `//`。不写重复名称或类型的注释。
- 保留 `#ifdef/#ifndef/#endif` 等编译指令，不能作为普通注释删除。
- 改动覆盖必要的调用处、类型、示例和文档；不顺带重写无关业务、第三方或生成文件。
- 按改动风险选择类型检查、行为测试与目标平台验证；仅更新规范时检查结构、链接和内容一致性。
