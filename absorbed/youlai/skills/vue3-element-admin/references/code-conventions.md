# 代码约定

这些是本项目的一致性选择。现有稳定契约需要迁移时同步修改调用方，不把个人排版偏好称为行业唯一标准。

## 命名与目录

| 对象             | 约定                                    | 示例                                      |
| ---------------- | --------------------------------------- | ----------------------------------------- |
| 组件文件         | PascalCase                              | `UserEditor.vue`                          |
| 路由页面         | 领域目录下 `index.vue` 或有含义的页面名 | `system/user/index.vue`                   |
| 工具与普通模块   | kebab-case                              | `token-refresh.ts`                        |
| Composable       | `use` + camelCase                       | `usePageTable.ts`                         |
| 变量和函数       | camelCase；集合用复数                   | `selectedUserIds`、`loadUsers`            |
| 布尔值           | 表达判断或能力                          | `isSaving`、`hasSelection`、`canEdit`     |
| 易混单位         | 单位进入名称                            | `timeoutSeconds`、`sizeBytes`             |
| 查询与分页       | `XxxQuery`、`PageQuery`                 | `UserQuery extends PageQuery`             |
| 列表、详情、表单 | `XxxItem`、`XxxDetail`、`XxxForm`       | `UserItem`、`UserForm`                    |
| 事件适配         | 局部 `handleXxx`                        | `handleRowAction`                         |
| 公开动作         | 动词表达用途，不绑定点击方式            | `openEdit`、`search`、`refresh`           |
| 指定值与反转     | 分别使用 `set` 与 `toggle`              | `setThemeMode(mode)`、`toggleThemeMode()` |

`Query` 已表达查询条件，不再叠加 `Params`。只有分页查询继承 `PageQuery`；菜单树、下拉选项等查询不为了统一而携带页码。局部参数可命名 `query`，Axios 的配置键仍是 `params`。

领域 API 放 `src/api`，状态放 `src/stores`，可复用有状态逻辑放 `src/composables`，纯工具放 `src/utils`。实时功能沿用 `api/realtime`、`utils/realtime` 和 `useRealtime`，不另建平行的 `services` 目录。按职责与复用拆分，不设文件行数或目录层数指标。

## API 与类型

- 同一 API 家族沿用 `getPage`、`getOptions`、`getFormData`、`create`、`update`、`deleteByIds`，以真实接口能力为准。
- 编辑回填使用 Form，独立只读详情使用 Detail；两者同形时可以复用，不为后缀多造一份类型。
- 复用 `@/api/common` 的 `PageQuery`、`PageResult`、`OptionItem`。普通成功响应已经返回业务数据；下载保持下载响应契约。
- 类型反映 JSON 实际形态：大整数 ID 通常为字符串，日期为字符串；不把 JSON 日期声明为 `Date`。
- 字段可选性来自接口和表单生命周期，不用全可选、`any` 或断言掩盖不匹配。外部未知数据使用 `unknown` 并校验。
- `sortField` 映射公开查询属性，不能填写数据库列。远程排序使用 `sort=createTime,desc`；多字段重复传 `sort`，保持优先级。

## 状态与异步

- 列表请求交给 `usePageTable`；选中行交给 `useTableSelection`。弹窗目标和写入状态由页面或领域 Composable 持有。
- 搜索回到第一页，刷新保留当前页；列表 loading 不承载保存或详情请求。请求参数使用快照；切换目标、关闭或卸载后，旧响应失效。
- 提交锁在异步校验前设置，在 `finally` 释放。保存成功与列表刷新失败分别反馈，不能因刷新失败重复写入。
- 确认框取消正常结束；真正的请求错误不能用空 `catch` 隐藏。需要吞掉 Promise 的事件入口要明确处理失败。
- 新 Store 使用 Setup Store；组件外复用 `useXxxStoreHook()` 或显式传 Pinia。一个状态只设一个所有者，不复制同一服务端数据到多个 Store。
- 卸载、退出和目标切换时清理监听、定时器、临时 URL 与连接；保留迟到回调的失效检查。

## Vue、样式与注释

使用 `<script setup lang="ts">`，SFC 块按 `template` → `script` → `style` 排列。

优先复用 `page-container`、`page-search`、`page-content`、`page-toolbar` 和主题变量。一次性布局可用 UnoCSS；重复布局提取公共类或组件。有状态、嵌套、媒体查询和第三方覆盖时用语义类与 scoped SCSS。同一属性只在一处维护，不为清理代码添加装饰性界面。

方法和类型的声明文档展开多行；字段简短说明可单行。API 方法也遵守此约定，不因对象外层已有说明而省略。文件头只说明不明显的共享职责，不重复文件名。具体示例见注释参考。
