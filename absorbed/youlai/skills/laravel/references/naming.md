# 命名规范

修改文件、类型、方法与变量的命名时读取。以当前仓库配置为准。

---

## 命名规范

### 文件与目录命名

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| 控制器目录 | `V1`（大写的 API 版本） | `app/Http/Controllers/V1/` |
| 控制器类 | 表名转 PascalCase + `Controller` | `SysUserController`、`SysRoleController` |
| Service 类 | 表名转 PascalCase + `Service` | `SysUserService`、`SysMenuService` |
| Validate 类 | 表名转 PascalCase + `Validate` | `SysUserValidate`、`SysRoleValidate` |
| Model 类 | 表名转 PascalCase（去前缀） | `SysUser`、`SysMenu`、`SysDept` |
| 模型目录 | 单数类名复数表名 | `sys_user` → `SysUser` |
| 配置文件 | 小写下划线 | `config/jwt.php`、`config/captcha.php` |
| 常量/枚举目录 | 见命名空间 | `app/Common/Enums/ResultCode.php` |

### 类型与成员命名

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| Model 类 | 表名去 `sys_` 前缀转 PascalCase | `SysUser`、`SysDictItem` |
| Service 类 | 模块名 + `Service` | `SysUserService` |
| Validate 类 | 模块名 + `Validate` | `SysUserValidate` |
| 控制器方法 | RESTful 标准动作 | `index`/`show`/`store`/`update`/`destroy` + 业务动作 |
| 业务方法 | 动词开头 snake_case | `paginate`/`create`/`assignRoles`/`restPassword` |
| 数据库字段 | snake_case | `dept_id`、`create_time`、`is_deleted` |
| JSON/API 字段 | camelCase（响应自动转换） | `deptId`、`createTime`、`roleIds` |
| 路由参数 | snake_case 或 kebab | `{id}`、`{name}` |

### 方法命名（Service 层）

| 操作 | 方法名 | 示例 |
| --- | --- | --- |
| 分页列表 | `paginate` | `paginate(array $filters, int $perPage)` |
| 单条详情 | `show` | `show(int $id): ?SysUser` |
| 创建 | `create` | `create(array $data): SysUser` |
| 更新 | `update` | `update(SysUser $model, array $data)` |
| 删除（批量） | `delete` | `delete(array $ids): int` |
| 状态变更 | `updateStatus` | 业务语义命名 |
| 重置密码 | `restPassword` | `restPassword(SysUser $user, array $data)` |
| 分配角色 | `assignRoles` | `assignRoles(SysUser $user, array $roleIds)` |
| 下拉选项 | `getOptions` | `getOptions(): array` |
| 用户信息 | `getUserInfo` | `getUserInfo(): array` |
| 数据格式化 | `format` | `format(SysUser $user): array` |

### 变量命名

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| 变量 | camelCase | `$userList`、`$roleCodes` |
| 常量 | SNAKE_CASE（类常量） | `PER_PAGE`、`STATUS_ENABLE` |
| 布尔变量 | `is_`/`has_` 前缀（PHP 属性） | `$isDeleted`、`$hasPerm` |
| 数据库字段 | snake_case | `dept_id`、`create_time` |
| JSON 键 | camelCase（响应层自动转换） | `deptId`、`createTime`、`pageSize` |

> **关键约定**：Model / Service 内部字段用 snake_case（对应 MySQL 列名）；响应输出经 `ApiResponse` 的 `CaseConversion` 自动转为 camelCase，前端收到的 JSON 键名为驼峰。无需手动 `toCamelCase`。
