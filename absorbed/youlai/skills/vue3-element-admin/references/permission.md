# 权限控制

权限控制用于界面可见性，不替代后端鉴权。权限标识和角色名称以服务端契约为准。

## `v-hasPerm`

```vue
<!-- 单个权限 -->
<el-button v-hasPerm="'sys:user:create'">新增</el-button>

<!-- 多个权限，满足任意一个即可 -->
<el-button v-hasPerm="['sys:user:create', 'sys:user:update']">操作</el-button>

<!-- 通配权限必须作为字符串表达式传入 -->
<el-button v-hasPerm="'*:*:*'">不限权限</el-button>
```

不要写 `v-hasPerm="*:*:*"`；这不是合法的 Vue 表达式。

指令复用 `@/utils/permission` 的 `hasPerm()`：

- 用户角色包含 `ROOT` 时直接放行。
- 所需权限包含 `*:*:*` 时直接放行。
- 数组权限采用“满足任意一个”的语义。
- 无权限时元素会从 DOM 移除。

脚本逻辑直接调用相同实现：

```typescript
import { hasPerm } from "@/utils/permission";

const canEdit = hasPerm("sys:user:update");
```

角色可见性使用已有 `v-hasRole`，不要用角色名冒充权限字符串。

## 权限命名

沿用后端的 `模块:资源:操作` 格式，例如：

- `sys:user:list`
- `sys:user:create`
- `sys:user:update`
- `sys:user:delete`
- `sys:role:assign`

不要仅为追求统一而重命名现有权限；它们是前后端契约。

## 配置驱动 CRUD

设置 `permissionPrefix: "sys:user"` 后，`CrudTable` 会把内置操作拼接为完整权限：

| 按钮               | 操作                           | 结果                     |
| ------------------ | ------------------------------ | ------------------------ |
| 新增 / 编辑 / 删除 | `create` / `update` / `delete` | `sys:user:create` 等     |
| 查看               | `update`                       | 当前复用编辑回填接口权限 |
| 导入 / 导出        | `import` / `export`            | `sys:user:import` 等     |
| 搜索               | `list`                         | `sys:user:list`          |
| 刷新 / 列设置      | `*:*:*`                        | 不限制                   |

自定义动作的 `permission` 可填写相对后缀或完整权限。完整权限直接使用，允许跨模块；相对后缀配合 `permissionPrefix` 拼接。权限数组使用任一满足语义。需要校验时应明确配置，不依赖缺少前缀时的相对字符串。

内置查看默认复用 `update`，不是自动生成 `read`。只读账号需要独立权限时，可显式覆盖 `view` 的 `permission`，并同步详情接口授权。跨模块按钮同样要有匹配的后端接口权限，前端配置不能改变服务端授权规则。

`visible` 控制显示，`disabled` 控制暂不可用；两者不能代替接口授权。自定义按钮插槽应绑定组件解析的 disabled/loading，并调用 action.run()，以复用执行前检查和异步占用。
