# 新增模块

修改新增业务模块的完整步骤时读取。以当前仓库配置为准。

## 目录

- 添加新模块 — 完整教程

---

## 添加新模块 — 完整教程

以添加 **"字典项"** 模块为例，展示从零到完整的步骤。

### Step 1: 生成 Entity

确认 `src/entity/sys_dict_item.rs` 已由 `sea-orm-cli generate entity` 生成。若无，重新执行生成命令。

### Step 2: 创建模块目录

```bash
mkdir src/modules/system/dict_item
```

### Step 3: 创建 `dto.rs`

```rust
// src/modules/system/dict_item/dto.rs
use serde::{Deserialize, Serialize};
use validator::Validate;

#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase")]
pub struct DictItemCreate {
    #[validate(length(min = 1, max = 50))]
    pub dict_code: String,
    #[validate(length(min = 1, max = 50))]
    pub value: String,
    #[validate(length(min = 1, max = 100))]
    pub label: String,
    pub tag_type: Option<String>,
    pub status: Option<i16>,
    pub sort: Option<i16>,
}

#[derive(Debug, Deserialize, Validate)]
#[serde(rename_all = "camelCase")]
pub struct DictItemUpdate {
    pub id: i64,
    #[validate(length(min = 1, max = 50))]
    pub dict_code: String,
    pub value: String,
    pub label: String,
    pub tag_type: Option<String>,
    pub status: Option<i16>,
    pub sort: Option<i16>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DictItemVO {
    pub id: i64,
    pub dict_code: String,
    pub value: String,
    pub label: String,
    pub tag_type: Option<String>,
    pub status: i16,
    pub sort: i16,
}

impl From<entity::sys_dict_item::Model> for DictItemVO {
    fn from(m: entity::sys_dict_item::Model) -> Self {
        Self {
            id: m.id,
            dict_code: m.dict_code,
            value: m.value,
            label: m.label,
            tag_type: m.tag_type,
            status: m.status.unwrap_or(1),
            sort: m.sort.unwrap_or(0),
        }
    }
}
```

### Step 4: 创建 `service.rs`

```rust
// src/modules/system/dict_item/service.rs
use sea_orm::*;
use crate::state::AppState;
use crate::error::{AppError, AppResult};
use crate::result_code::ResultCode;
use crate::modules::system::dict_item::dto::*;

pub struct UserService<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> UserService<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self { Self { db } }

    pub async fn list_by_dict_code(&self, dict_code: &str) -> AppResult<Vec<DictItemVO>> {
        let items = entity::sys_dict_item::Entity::find()
            .filter(entity::sys_dict_item::Column::DictCode.eq(dict_code))
            .filter(entity::sys_dict_item::Column::IsDeleted.eq(0))
            .order_by_asc(entity::sys_dict_item::Column::Sort)
            .all(self.db).await?;
        Ok(items.into_iter().map(Into::into).collect())
    }

    pub async fn create(&self, form: DictItemCreate) -> AppResult<DictItemVO> {
        let active = entity::sys_dict_item::ActiveModel {
            dict_code: sea_orm::Set(form.dict_code),
            value: sea_orm::Set(form.value),
            label: sea_orm::Set(form.label),
            tag_type: sea_orm::Set(form.tag_type),
            status: sea_orm::Set(form.status.unwrap_or(1)),
            sort: sea_orm::Set(form.sort.unwrap_or(0)),
            ..Default::default()
        };
        let model = active.insert(self.db).await?;
        Ok(model.into())
    }

    pub async fn delete(&self, ids: &str) -> AppResult<u64> {
        let id_list: Vec<i64> = ids.split(',').filter_map(|s| s.parse().ok()).collect();
        let res = entity::sys_dict_item::Entity::update_many()
            .col_expr(entity::sys_dict_item::Column::IsDeleted, Expr::value(1))
            .filter(entity::sys_dict_item::Column::Id.is_in(id_list))
            .exec(self.db).await?;
        Ok(res.rows_affected)
    }
}
```

### Step 5: 创建 `mod.rs`（路由）

```rust
// src/modules/system/dict_item/mod.rs
pub mod dto;
pub mod service;

use axum::{extract::{Path, State}, routing::get, Json, Router};
use crate::state::AppState;
use crate::response::Result;
use crate::modules::system::dict_item::dto::*;
use crate::modules::system::dict_item::service::DictItemService;

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/api/v1/dict-items", get(list_dict_items).post(create_dict_item))
        .route("/api/v1/dict-items/:id", axum::routing::put(update_dict_item))
        .route("/api/v1/dict-items/:ids", axum::routing::delete(delete_dict_items))
}

pub async fn list_dict_items(
    State(state): State<AppState>,
) -> AppResult<Json<Result<Vec<DictItemVO>>>> { /* ... */ }

pub async fn create_dict_item(
    State(state): State<AppState>,
    Json(form): Json<DictItemCreate>,
) -> AppResult<Json<Result<DictItemVO>>> { /* ... */ }
```

### Step 6: 在 `main.rs` 注册路由

```rust
// src/main.rs
let app = Router::new()
    .merge(modules::auth::routes())
    .merge(modules::system::dict_item::routes())  // ← 新增
    // ...
    .with_state(state);
```

### Step 7: 验证

```bash
cargo watch -x 'run'
# 访问 http://localhost:8000/swagger-ui 确认路由已注册
```
