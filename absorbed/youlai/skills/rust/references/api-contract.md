# 接口契约

修改路由、状态码、业务错误码与统一响应时读取。以当前仓库配置为准。

## 目录

- 路由与 API 规范
- HTTP 状态码与业务错误码
- 统一响应格式

---

## 路由与 API 规范

### 路由前缀

```rust
// src/modules/system/user/mod.rs
use axum::Router;
pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/api/v1/users", get(list_users).post(create_user))
        // ...
}
```

| 模块 | 前缀 |
|------|------|
| 认证 | `/api/v1/auth` |
| 用户 | `/api/v1/users` |
| 角色 | `/api/v1/roles` |
| 菜单 | `/api/v1/menus` |
| 部门 | `/api/v1/depts` |
| 字典 | `/api/v1/dicts`、`/api/v1/dict-items` |
| 配置 | `/api/v1/configs` |
| 通知 | `/api/v1/notices` |
| 日志 | `/api/v1/logs` |
| 文件 | `/api/v1/files` |
| SSE | `/api/v1/sse` |
| 代码生成 | `/api/v1/gen` |

### 标准 CRUD 路径

| 操作 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 分页列表 | `GET` | `/api/v1/users` | Query 参数：`pageNum`/`pageSize`/`keywords`/... |
| 表单数据 | `GET` | `/api/v1/users/:id/form` | 路径参数 `id: i64` |
| 新增 | `POST` | `/api/v1/users` | Body: `UserCreate` |
| 更新 | `PUT` | `/api/v1/users/:id` | Body: `UserUpdate` |
| 批量删除 | `DELETE` | `/api/v1/users/:ids` | `ids` 逗号分隔 |
| 修改状态 | `PATCH` | `/api/v1/users/:id/status` | Body: `UserStatusForm` |
| 重置密码 | `PUT` | `/api/v1/users/:id/password/reset` | |
| 导出 | `GET` | `/api/v1/users/export` | 返回 xlsx 字节流 |
| 导入 | `POST` | `/api/v1/users/import` | multipart xlsx |
| 导入模板 | `GET` | `/api/v1/users/template` | 下载模板 xlsx |
| 下拉选项 | `GET` | `/api/v1/roles/options` | 返回 `[{value, label}]` |

### 路由注册顺序（重要！）

**固定路径端点必须定义在路径参数端点之前**，否则 axum 路由会冲突报错或被错误匹配：

```rust
// ✅ 正确顺序（axum 需显式注册每条路由）
Router::new()
    .route("/api/v1/users", get(list_users))           // 固定
    .route("/api/v1/users/template", get(download_template))  // 固定 —— 在 /:id 前
    .route("/api/v1/users/export", get(export_users))  // 固定
    .route("/api/v1/users/import", post(import_users)) // 固定
    .route("/api/v1/users/options", get(list_user_options))   // 固定
    .route("/api/v1/users/me", get(get_current_user))  // 固定
    .route("/api/v1/users/:id/form", get(get_user_form))      // 路径参数
    .route("/api/v1/users/:id", put(update_user))      // 路径参数
    .route("/api/v1/users/:ids", delete(delete_users)) // 路径参数
```

### Handler 函数模板

```rust
// src/modules/system/user/mod.rs — 完整模板
use axum::{
    extract::{Path, Query, State},
    routing::{get, post, put, delete, patch},
    Json, Router,
};
use validator::Validate;
use crate::state::AppState;
use crate::modules::auth::{extractor::current_user, permission::require_perm};
use crate::response::{Result, PageResult};
use crate::modules::system::user::dto::{UserCreate, UserUpdate, UserQuery};
use crate::modules::system::user::service::UserService;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/api/v1/users", get(list_users).post(create_user))
        .route("/api/v1/users/:id/form", get(get_user_form))
        .route("/api/v1/users/:id", put(update_user))
        .route("/api/v1/users/:ids", delete(delete_users))
}

/// 分页查询用户列表
#[utoipa::path(
    get, path = "/api/v1/users",
    tag = "用户管理",
    params(
        ("pageNum" = i64, Query, description = "当前页码"),
        ("pageSize" = i64, Query, description = "每页条数"),
        ("keywords" = Option<String>, Query, description = "搜索关键词"),
    ),
    responses((status = 200, body = PageResult<UserVO>))
)]
pub async fn list_users(
    State(state): State<AppState>,
    Query(query): Query<UserQuery>,
) -> AppResult<Json<PageResult<UserVO>>> {
    let page = UserService::new(&state.db).get_page(query).await?;
    Ok(Json(PageResult::success(page.list, page.total)))
}

/// 创建用户
#[utoipa::path(
    post, path = "/api/v1/users",
    tag = "用户管理",
    request_body = UserCreate,
    responses((status = 200, body = Result<UserVO>))
)]
pub async fn create_user(
    State(state): State<AppState>,
    Json(form): Json<UserCreate>,
) -> AppResult<Json<Result<UserVO>>> {
    form.validate()?;  // validator 校验
    let vo = UserService::new(&state.db).create(form).await?;
    Ok(Json(Result::success(vo)))
}
```

## HTTP 状态码与业务错误码

### 设计理念

对齐 PostgreSQL 参考实现：**HTTP 状态码恒为 200**，业务状态码通过 body 的 `code` 字段传递。前端 axios 拦截器统一从 `response.data.code` 读取业务码。

### 业务错误码（ResultCode）

完整枚举见 `项目设计文档` 第 3.4 节。核心码段：

| 错误码 | 含义 | 说明 |
|--------|------|------|
| `00000` | 成功 | 正常返回 |
| `A0210` | 用户名或密码错误 | 登录失败 |
| `A0230` | 访问令牌无效或过期 | 触发前端 token 刷新 |
| `A0231` | 刷新令牌无效或过期 | 跳转登录页 |
| `A0301` | 访问未授权 | 权限不足 |
| `A0400` | 参数校验失败 | validator 校验不通过 |
| `B0001` | 系统执行出错 | 全局兜底 |

首位编码规则：
- `0` 成功（`00000`）
- `A` 用户端错误（认证/权限/参数）
- `B` 系统端错误
- `C` 第三方服务错误

### AppError 与全局异常处理

```rust
// src/error.rs
use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use crate::result_code::ResultCode;
use crate::response::Result;

#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("{1:?}")]
    Business(ResultCode, Option<String>),
    #[error("参数校验失败: {0}")]
    Validation(String),
    #[error("数据库错误: {0}")]
    Database(String),
    #[error(transparent)]
    Other(#[from] anyhow::Error),
}

// validator::ValidationErrors → AppError
impl From<validator::ValidationErrors> for AppError {
    fn from(e: validator::ValidationErrors) -> Self {
        AppError::Validation(e.to_string())
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        // 关键：业务错误统一返回 HTTP 200，code 通过 body 传递
        let result: Result<()> = match self {
            AppError::Business(code, msg) => Result::failed(code, msg),
            AppError::Validation(msg) => Result::failed(ResultCode::UserRequestParameterError, Some(msg)),
            AppError::Database(msg) => {
                tracing::error!("数据库错误: {msg}");
                Result::failed(ResultCode::DatabaseExecutionError, None)
            }
            AppError::Other(e) => {
                tracing::error!("系统异常: {e:#}");
                Result::failed(ResultCode::SystemError, None)
            }
        };
        (StatusCode::OK, Json(result)).into_response()
    }
}

pub type AppResult<T> = std::result::Result<T, AppError>;
```

### 业务异常抛出示例

```rust
// ✅ 认证失败
return Err(AppError::Business(ResultCode::UserPasswordError, None));
return Err(AppError::Business(ResultCode::AccessTokenInvalid, None));

// ✅ 权限不足
return Err(AppError::Business(ResultCode::AccessUnauthorized, Some("权限不足".into())));

// ✅ 数据不存在
return Err(AppError::Business(ResultCode::AccountNotFound, Some("用户不存在".into())));

// ✅ 参数校验（handler 中调用 form.validate()?）
form.validate()?;  // 自动转 AppError::Validation
```

## 统一响应格式

### Result 结构

```json
{
    "code": "00000",
    "msg": "成功",
    "data": { … }
}
```

```rust
// src/response.rs
use serde::{Serialize, Deserialize};
use crate::result_code::ResultCode;

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Result<T> {
    pub code: String,
    pub msg: String,
    pub data: Option<T>,
}

impl<T> Result<T> {
    pub fn success(data: T) -> Self { /* code=00000 */ }
    pub fn success_empty() -> Self { /* data=None */ }
    pub fn failed(code: ResultCode, msg: Option<String>) -> Self { /* ... */ }
}
```

### PageResult 结构

```json
{
    "code": "00000",
    "msg": "成功",
    "data": {
        "list": [ … ],
        "total": 100
    }
}
```

```rust
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PageResult<T> {
    pub code: String,
    pub msg: String,
    pub data: PageData<T>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PageData<T> {
    pub list: Vec<T>,
    pub total: u64,
}
```

### 分页查询参数

```rust
// src/pagination.rs
use serde::Deserialize;

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PageQuery {
    #[serde(default = "default_page_num")]
    pub page_num: i64,
    #[serde(default = "default_page_size")]
    pub page_size: i64,
}

fn default_page_num() -> i64 { 1 }
fn default_page_size() -> i64 { 10 }
```

> **前端约定**：分页参数命名为 `pageNum` / `pageSize`（camelCase），兼容 vue3-element-admin 的 TablePage 组件。
