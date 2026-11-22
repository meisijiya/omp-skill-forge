# 数据与认证

修改模型、ORM、认证鉴权与数据库操作时读取。以当前仓库配置为准。

## 目录

- SeaORM Entity 规范
- 认证与鉴权
- 数据库操作规范

---

## SeaORM Entity 规范

### Entity 由 sea-orm-cli 自动生成

```bash
sea-orm-cli generate entity \
    --connection-string "postgres://postgres:123456@localhost:5432/app_admin" \
    --output-dir src/entity \
    --with-serde both
```

### Entity 示例

```rust
// src/entity/sys_user.rs
use sea_orm::entity::prelude::*;
use chrono::NaiveDateTime;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, serde::Serialize, serde::Deserialize)]
#[sea_orm(table_name = "sys_user")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i64,                          // bigint
    pub username: String,                 // varchar
    pub nickname: String,
    pub password: String,
    #[sea_orm(nullable)]
    pub dept_id: Option<i64>,
    pub mobile: String,
    pub email: String,
    pub status: i16,                      // smallint → i16
    #[sea_orm(column_name = "create_time")]
    pub create_time: Option<NaiveDateTime>,  // timestamp
    #[sea_orm(column_name = "update_time")]
    pub update_time: Option<NaiveDateTime>,
    #[sea_orm(column_name = "is_deleted")]
    pub is_deleted: i16,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::sys_user_role::Entity")]
    UserRole,
}

impl Related<super::sys_user_role::Entity> for Entity {
    fn to() -> RelationDef { Relation::UserRole.def() }
}

impl ActiveModelBehavior for ActiveModel {}
```

### PostgreSQL 类型映射

| PostgreSQL 类型 | Rust 类型 | 说明 |
|----------------|-----------|------|
| `bigint` | `i64` | 主键、外键 |
| `smallint` | `i16` | 状态、标识位 |
| `integer` | `i32` | 普通整数 |
| `varchar(n)` | `String` | 变长字符串 |
| `text` | `String` | 长文本 |
| `boolean` | `bool` | 布尔 |
| `timestamp` | `chrono::NaiveDateTime` | 时间 |
| `jsonb` | `serde_json::Value` | JSON |
| `uuid` | `uuid::Uuid` | UUID |

### 字段命名对照

| SQL 列名 | Entity 字段 | DTO 字段 | 说明 |
|----------|-------------|----------|------|
| `dept_id` | `dept_id` | `deptId` | 部门ID |
| `create_time` | `create_time` | `createTime` | 创建时间 |
| `is_deleted` | `is_deleted` | — | 逻辑删除（内部使用） |
| `parent_id` | `parent_id` | `parentId` | 父节点ID |

> **转换规则**：Entity → VO 时，`to_vo` 方法负责 snake_case → camelCase 转换。

### VO 转换模板

```rust
// src/modules/system/user/dto.rs
impl From<entity::sys_user::Model> for UserVO {
    fn from(m: entity::sys_user::Model) -> Self {
        UserVO {
            id: m.id,
            username: m.username,
            dept_id: m.dept_id,       // ← 手动映射（VO 用 #[serde(rename)]）
            create_time: m.create_time.map(|t| t.to_string()),
            // ...
        }
    }
}
```

## 认证与鉴权

### Token 模式

通过 `config.toml` 的 `security.session.type` 切换：

| 值 | 模式 | 实现 |
|----|------|------|
| `jwt`（默认） | JWT 自包含 Token | `JwtTokenManager` |
| `redis-token` | Redis 存储 Token | `RedisTokenManager` |

### 获取当前用户

```rust
use crate::modules::auth::extractor::current_user;

pub async fn get_current_user_info(req: Request) -> AppResult<Json<Result<UserVO>>> {
    let user = current_user(&req).ok_or_else(|| 
        AppError::Business(ResultCode::AccessTokenInvalid, None))?;
    Ok(Json(Result::success(user.into())))
}
```

### 权限校验

```rust
use crate::modules::auth::permission::require_perm;

// 精确权限（通过 route_layer 挂载中间件）
pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/api/v1/users", get(list_users)
            .route_layer(middleware::from_fn(require_perm("sys:user:query"))))
        .route("/api/v1/users", post(create_user)
            .route_layer(middleware::from_fn(require_perm("sys:user:create"))))
}
```

### 权限标识命名规范

```
模块:实体:操作
sys:user:create
sys:user:edit
sys:user:delete
sys:role:query
sys:menu:query
sys:dept:query
```

| 操作 | 说明 |
|------|------|
| `query` | 列表/查询 |
| `create` | 新增 |
| `edit` | 编辑 |
| `delete` | 删除 |
| `import` | 导入 |
| `export` | 导出 |
| `reset_pwd` | 重置密码 |

## 数据库操作规范

### SeaORM 查询

```rust
// ✅ 单条查询
let user = entity::sys_user::Entity::find_by_id(user_id)
    .filter(entity::sys_user::Column::IsDeleted.eq(0))
    .one(&self.db)
    .await?
    .ok_or_else(|| AppError::Business(ResultCode::AccountNotFound, Some("用户不存在".into())))?;

// ✅ 分页查询
let paginator = entity::sys_user::Entity::find()
    .filter(entity::sys_user::Column::IsDeleted.eq(0))
    .filter(entity::sys_user::Column::Status.eq(1))
    .filter(entity::sys_user::Column::Username.like(format!("%{keywords}%")))
    .order_by_desc(entity::sys_user::Column::CreateTime)
    .paginate(&self.db, page_size as usize);

let total = paginator.num_items().await?;
let users = paginator.fetch_page((page_num - 1) as usize).await?;
```

### 事务管理

```rust
// ✅ 显式事务（多步写操作）
use sea_orm::TransactionTrait;

self.db.transaction::<_, _, AppError>(|txn| {
    Box::pin(async move {
        entity::sys_user::ActiveModel { ... }.insert(txn).await?;
        entity::sys_user_role::ActiveModel { ... }.insert(txn).await?;
        Ok(())
    })
}).await?;
```

### 批量操作

```rust
// ✅ 批量删除（逻辑删除）
let id_list: Vec<i64> = ids.split(',').filter_map(|s| s.parse().ok()).collect();
entity::sys_user::Entity::update_many()
    .col_expr(entity::sys_user::Column::IsDeleted, Expr::value(1))
    .filter(entity::sys_user::Column::Id.is_in(id_list))
    .exec(&self.db)
    .await?;

// ✅ 批量插入
let models: Vec<entity::sys_config::ActiveModel> = batch.into_iter().map(Into::into).collect();
entity::sys_config::Entity::insert_many(models).exec(&self.db).await?;
```
