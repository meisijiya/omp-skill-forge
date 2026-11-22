# 配置驱动 CRUD

维护配置驱动页面时，先核对 `src/components/Crud/types.ts`、`CrudPage`、三个子组件和 `useCrudPage.ts`。示例需要与真实类型、事件和返回值一致。

## 常用入口

普通 CRUD 页面使用 `CrudPage`，传入 `tableConfig`，按需配置 `searchConfig`、`formConfig` 和详情加载回调 `loadFormData`。组件自动连接搜索、重置、筛选、刷新、新增、编辑、查看和保存后刷新，页面不再逐项声明 refs 或转发这些事件。

插槽按归属加 `table-`、`search-`、`form-` 前缀，再使用子组件的槽名，例如 `table-cell-status`、`form-label-username`。自定义按钮仍通过动作的 `onClick` 返回 Promise。

复杂布局继续组合 `CrudSearch`、`CrudTable`、`CrudForm` 和 `useCrudPage`，不为使用单入口而限制原有插槽和布局。

## 公开契约

| 入口        | 契约                                                                 |
| ----------- | -------------------------------------------------------------------- |
| CrudPage    | `tableConfig`，按需提供 `searchConfig`、`formConfig`、`loadFormData` |
| CrudSearch  | `searchConfig: CrudSearchConfig`，字段配置为 fields                  |
| CrudTable   | `tableConfig: CrudTableConfig<TQuery, TItem>`                        |
| CrudForm    | `formConfig: CrudFormConfig<TForm>`                                  |
| useCrudPage | 默认导出，提供 searchRef、tableRef、formRef                          |

列表配置使用完整且明确的名称：

- `permissionPrefix`：拼接内置按钮权限。
- `fetchData`：接收查询，返回 PageResult 或数组；其他接口结构在此转换，不要求后端改名。
- `columns`：列配置；操作列使用 `cellType: "actions"`。
- `toolbarActions`：左侧业务操作；`tableTools`：右侧工具。
- `rowKey`：稳定主键属性，默认 id。
- `updateField`：即时编辑；`deleteByIds`：删除主键集合。
- `paginationKeys`：需要适配其他接口时配置 `{ page, size }`，默认 pageNum/pageSize。

内置操作为 create、edit、view、delete、import、export；工具为 refresh、columns、search。业务字段、原生控件属性和后端权限值不随通用配置改名。

## 动作与事件

`openCreate`、`openEdit`、`openView`、`search`、`resetSearch`、`refresh`、`exportFile`、`toggleSearch`、`applyFilters` 是可直接调用的公开动作。页面根据行操作分发时，可以定义局部 `handleRowAction({ key, row })`。

局部 `handleXxx` 表达事件适配；公开动作表达实际用途，不把鼠标点击写进可复用方法名。这是本项目约定，不是行业唯一命名。

- 搜索事件为 search、reset。
- 表格事件为 create、toggle-search、toolbar-action、row-action、filter-change。
- 表单成功保存后发出 saved；保存后刷新不重新提交表单。
- Vue 事件不等待监听器的 Promise。需要按钮等待完整流程时，使用返回 Promise 的 `onClick`，不能把 emit 当作可等待回调。

表格实例提供 `loadData`、`refresh`、`exportFile`、`getSelection`、`getFilters`、`clearFilters`、`getExportQuery`。直接调用请求方法时处理 Promise 拒绝；界面已经展示的查询失败不应再次触发写入。

## 共用表单与插槽

同一实体的新增、编辑、查看共用一个表单，通过 `mode: "create" | "edit" | "view"` 表达差异。页面复杂时再拆配置和私有组件，不机械创建目录或两份重复字段。

- `fields` 声明字段；label、visible、readonly、required 可以读取 `{ mode, id, model }`。
- `submitForm(data, context)` 返回完整请求 Promise；更新路径使用 context.id。
- 编辑与查看加载完整详情，不以缺字段的列表行代替。
- 字段初始化使用 `onInit`，异步回调返回实际 Promise。
- 自定义控件绑定槽内 attrs，保留查看和请求期间的禁用状态。
- `cell-{prop}` 替换单元格，`header-{columnKey 或 prop}` 替换表头。
- `row-action-{key}`、`toolbar-action-{key}` 接收解析后的 action；绑定 disabled/loading 并调用 action.run()。
- 表单控件槽默认 prop，标签槽为 `label-{prop}`。

动作使用 `key`、`label`、`permission`、`buttonProps`、`visible`、`disabled`、`onClick`；字段的原生控件属性仍放 attrs。完整权限允许跨模块，权限数组沿用 hasPerm 的任一满足语义，后端继续校验接口权限。

## 查询和文件处理

- 每行提供稳定的 string/number 主键。sortField 仅映射公开 API 属性，不填数据库列。
- `sortable: true` 保留原生本地排序；`sortable: "custom"` 连接远程排序，协议为 `sort=createTime,desc`。
- 刷新、翻页、筛选与导出沿用已应用条件，不读取未提交搜索草稿。
- input/switch 即时编辑需要 updateField；复杂行事务由业务实现。
- importFile 接收 File，importRows 接收浏览器解析的行；exportFile 返回文件响应，fetchExportRows 返回全部匹配行。
- 两种回调同时存在时指定 importMode/exportMode=file|rows；没有全量回调时不能用普通分页结果充当全量。
- 部分导入保留统计和错误，清除原文件，不能提示全部成功或自动重放。

## 验证

TS CRUD 生成模板使用 `CrudPage`，字典槽按所属组件添加前缀；详情加载读取与 `tableConfig.rowKey` 一致的主键，不再生成重复 refs 和事件转发。

公共契约调整需同步演示、公开文档及 `代码生成模板`，不连带改动 TableSelect 或独立 JS 版本。运行类型、受影响文件的格式和 lint、CRUD 行为及生成模板检查。新增或修改方法、类型的文档按注释参考展开多行，保留异步与资源约束。
