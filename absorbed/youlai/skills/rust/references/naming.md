# 命名规范

修改文件、类型、方法与变量的命名时读取。以当前仓库配置为准。

---

## 命名规范

### 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块目录 | 小写下划线（snake_case）名词 | `user/`, `dict/`, `dict_item/` |
| 模块入口 | `mod.rs` | `src/modules/system/user/mod.rs` |
| DTO 文件 | `dto.rs` | `src/modules/system/user/dto.rs` |
| Service 文件 | `service.rs` | `src/modules/auth/service.rs` |
| Entity 文件 | 表名 | `src/entity/sys_user.rs` |
| 配置文件 | `config.rs` | `src/config.rs` |
| 常量文件 | `constants.rs` | `src/constants.rs` |
| 枚举文件 | `enums.rs` | `src/result_code.rs` |
| 测试文件 | 与被测模块同名的测试模块 | `src/modules/system/user/mod.rs` 内的 `#[cfg(test)]` |

### 类型命名

| 类型 | 规范 | 示例 |
|------|------|------|
| SeaORM Entity | 表名转 PascalCase | `SysUser`, `SysRole`, `SysMenu` |
| DTO 结构体 | 功能 + 后缀 | `UserCreate`, `UserUpdate`, `UserVO`, `UserQuery` |
| Service 结构体 | 模块名 + `Service` | `UserService`, `AuthService`, `RoleService` |
| 配置结构体 | `Settings` / `XxxConfig` | `Settings`, `SecurityConfig`, `DatabaseConfig` |
| 枚举 | 功能名（无 Enum 后缀） | `ResultCode`, `Status`(i16 别名) |
| 错误类型 | `AppError` | 统一使用 `AppError` |
| Trait | 能力名 | `TokenManager`, `TenantQuery`(无) |
| Handler 函数 | snake_case 动词 | `list_users`, `create_user`, `get_user_form` |

**DTO 后缀规范**：

| 后缀 | 用途 | 示例 |
|------|------|------|
| `Create` | 创建表单 | `UserCreate`, `RoleCreate` |
| `Update` | 更新表单 | `UserUpdate`, `MenuUpdate` |
| `VO` | 视图对象（返回） | `UserVO`, `RoleVO`, `DictVO` |
| `Query` | 分页查询参数 | `UserQuery`, `RoleQuery`, `LogQuery` |
| `Form` | 特定操作表单 | `UserPasswordForm`, `RoleMenuForm` |
| `Result` | 响应结果 | `LoginResult`, `ExcelResult` |

### 方法命名

| 操作 | 方法名 | 示例 |
|------|--------|------|
| 分页查询 | `get_page` | `pub async fn get_page(&self, query: UserQuery) -> AppResult<PageData<UserVO>>` |
| 单条查询 | `get_by_id` | `pub async fn get_by_id(&self, id: i64) -> AppResult<UserVO>` |
| 树形查询 | `get_tree` | `pub async fn get_tree(&self, keywords: &str) -> AppResult<Vec<MenuVO>>` |
| 下拉选项 | `get_options` | `pub async fn get_options(&self) -> AppResult<Vec<OptionVO>>` |
| 创建 | `create` | `pub async fn create(&self, form: UserCreate) -> AppResult<UserVO>` |
| 更新 | `update` | `pub async fn update(&self, form: UserUpdate) -> AppResult<UserVO>` |
| 删除（批量） | `delete` | `pub async fn delete(&self, ids: &str) -> AppResult<u64>` |
| 状态变更 | `update_status` | `pub async fn update_status(&self, id: i64, status: i16)` |
| 导入 | `import_<资源>` | `pub async fn import_users(&self, bytes: Vec<u8>) -> AppResult<ExcelResult>` |
| 导出 | `export_<资源>` | `pub async fn export_users(&self, query: UserQuery) -> AppResult<Vec<u8>>` |

### 变量命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_list`, `role_codes` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE`, `ROOT_ROLE_CODE` |
| 私有方法/字段 | 无特殊前缀（Rust 用可见性控制） | `fn to_vo(...)` |
| 布尔变量 | `is_`/`has_` 前缀 | `is_root`, `is_deleted`, `has_perm` |
| 数据库字段 | snake_case | `dept_id`, `create_time` |
| JSON/API 字段 | camelCase（serde rename） | `deptId`, `createTime`, `pageSize` |

> **关键约定**：Entity 字段用 snake_case（对应 PostgreSQL 列名），DTO/API 字段用 camelCase（对应前端 JSON 键名），通过 `#[serde(rename_all = "camelCase")]` 或 `#[serde(rename = "camelCase")]` 转换。
