# 新增 API 与页面

先读同领域 API、相邻页面和后端契约。本文说明接入方式，不要求复制整套脚手架。

## 选择页面模式

| 场景                           | 选择                                                   |
| ------------------------------ | ------------------------------------------------------ |
| 普通分页、自定义表单、权限分配 | 复用 `usePageTable`、`useTableSelection`，交互留在页面 |
| 标准增删改查，希望减少页面代码 | 使用 `CrudPage`，按需配置字段、权限和插槽              |
| 仪表盘、详情、设置             | 直接组合 API、状态和组件                               |

维护页面沿用现有模式；用户要求重新封装时再统一迁移。两种列表方案供使用者选择，不把普通管理页强制迁入 CRUD。

## 类型与 API

较完整的业务 API 使用 `index.ts` + `types.ts`。小模块可以保留单文件，不为目录齐整增加空壳。

```typescript
import type { PageQuery } from "@/api/common";

/**
 * 用户列表查询条件。
 */
export interface UserQuery extends PageQuery {
  keywords?: string;
  status?: number;
}
```

分页、排序直接复用公共类型。非分页查询不继承 `PageQuery`；其他字段按真实请求声明。

```typescript
import type { PageResult } from "@/api/common";
import request from "@/utils/request";
import type { UserItem, UserQuery } from "./types";

const USER_BASE_URL = "/api/v1/users";

const UserAPI = {
  /**
   * 获取用户分页列表。
   */
  getPage(query: UserQuery) {
    return request<unknown, PageResult<UserItem>>({
      url: USER_BASE_URL,
      method: "get",
      params: query,
    });
  },
};

export default UserAPI;
export * from "./types";
```

这是方法接入片段，`UserItem` 等业务类型复用当前模块。新增 API 前核对真实 URL、请求和响应，不从示例推断接口存在。

- 普通业务成功响应已经解包，调用方直接使用 `list`、`total` 等业务字段。
- API 自身返回结构不同，可以在 `request` 回调或 CRUD 的 `fetchData` 中适配，不要求所有后端都返回相同字段名。
- 编辑回填使用 `getFormData`；不以缺字段的列表行代替完整表单。
- 更新目标取已打开的用户 ID；请求体中的 `id` 不决定目标。
- 导出复用当前下载工具，保留响应头和二进制错误处理。

## 分页列表

以下为页面脚本片段，完整页面复用当前的用户或角色管理实现：

```typescript
const queryFormRef = ref<FormInstance>();

const {
  loading,
  list,
  total,
  params,
  fetchData,
  handleQuery,
  handleResetQuery,
} = usePageTable<UserItem, UserQuery>({
  initialParams: { pageNum: 1, pageSize: 10, keywords: "" },
  request: UserAPI.getPage,
  onBeforeReset: () => queryFormRef.value?.resetFields(),
});

const { selectedIds, hasSelection, handleSelectionChange } =
  useTableSelection<UserItem>();
```

- `handleQuery()` 回到第一页；`fetchData()` 保留当前页；`handleResetQuery()` 恢复初值并请求。
- `usePageTable` 持有列表 loading，并隔离过期列表响应；页面不能借用它表示保存、删除或详情加载。
- 事件入口处理 Promise 失败；搜索失败不能继续执行写入，取消确认不能显示删除成功。
- `selectedIds` 为 `(string | number)[]`；按实际 API 序列化，不能强转绕过检查。

## 表单与布局

打开弹窗时重置旧数据和校验状态；详情加载、提交各用独立状态。切换编辑目标、关闭和卸载使旧详情请求失效。加载失败时阻止保存，提交锁覆盖异步校验与完整请求。

```vue
<template>
  <div class="page-container">
    <el-card class="page-search" shadow="never">搜索区域</el-card>
    <el-card class="page-content" shadow="never">列表区域</el-card>
  </div>
</template>

<script setup lang="ts"></script>
```

布局示意不包含业务代码。沿用全局页面样式；无样式时省略空 `style` 块，不重复添加已有的高度、flex 和间距。

完整配置驱动页面见 CRUD 参考。仅在复用或职责边界明确时拆私有组件与配置，不按行数拆文件。
