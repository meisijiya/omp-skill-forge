---
name: forge-vue3-element-admin
description: 用于 Vue 3 + Element Plus 管理后台的开发、重构与代码审查，涵盖页面、API、CRUD、路由权限及会话。适用于采用该技术栈及其约定的项目。
---

# Vue 3 + Element Plus 管理后台开发

读取目标源码、相邻实现与项目配置，按任务查阅以下规范。重构时同步调用、生成模板和使用文档。

## 按任务读取

| 任务                                  | 参考                                                 |
| ------------------------------------- | ---------------------------------------------------- |
| 命名、目录、类型、状态、样式          | [代码约定](references/code-conventions.md)           |
| 新增 API、分页列表或表单              | [新增 API 与页面](references/new-page-guide.md)      |
| 配置驱动增删改查与自定义插槽          | [CRUD](references/crud-development.md)               |
| 注释新增、精简或审查                  | [注释](references/comments.md)                       |
| 登录、续期、退出或 WebSocket          | [会话与实时连接](references/session-and-realtime.md) |
| 静态路由与动态菜单                    | [路由菜单](references/router-menu.md)                |
| 按钮权限与跨模块动作                  | [权限](references/permission.md)                     |
| 标签页与 keep-alive                   | [页面缓存](references/page-caching.md)               |
| 语言包与语言切换                      | [国际化](references/i18n.md)                         |
| 设置、环境变量与存储键                | [项目配置](references/project-config.md)             |
| Upload、Dict、TableSelect、IconSelect | [项目组件](references/components.md)                 |

## 验证

- 代码：类型检查、修改文件的 lint 与相关测试；影响构建时验证构建。
- 文档：格式、链接和示例。交付说明实际验证结果与未覆盖范围。
