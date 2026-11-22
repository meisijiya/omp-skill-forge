# 交付质量

修改注释、检查清单、反模式与部署时读取。以当前仓库配置为准。

## 目录

- 注释规范
- 代码质量检查清单
- 常见反模式
- Docker 部署

---

## 注释规范

### 总则

- **doc comment 优先**：所有公共项用 `///` 文档注释
- **自解释代码**：好的命名和结构是自解释的，注释描述"为什么"
- **中文优先**：用中文把问题说清楚；专有名词保留英文（如 `HTTP`、`async`）
- **同步更新**：代码修改时 doc comment 必须同步修改

### doc comment 格式

```rust
/// 分页查询用户列表。
///
/// 根据关键词模糊搜索用户名/昵称/手机号，支持状态筛选。
///
/// # 参数
/// - `query`: 分页查询参数（pageNum / pageSize / keywords / status）
///
/// # 返回
/// 分页结果，包含 list 和 total。
///
/// # 错误
/// - `AppError::Business(UserRequestParameterError)`: pageSize 超过 100
pub async fn get_page(&self, query: UserQuery) -> AppResult<PageData<UserVO>> {
    ...
}
```

### 各层注释要点

| 层 | 必须说明 |
|----|---------|
| 模块（`mod.rs` 顶部） | 文件职责 |
| Service struct | 职责、依赖 |
| 公共方法 | 功能、参数、返回值、错误 |
| Handler | 配合 `#[utoipa::path]` 注解 API 文档 |

### TODO / FIXME 标记规范

| 标记 | 用途 | 格式 |
|------|------|------|
| `TODO` | 待实现 | `// TODO(标记人, 日期, 说明)` |
| `FIXME` | 已知 bug | `// FIXME(标记人, 日期, 说明)` |

## 代码质量检查清单

### 通用检查

- [ ] 所有公共项有 `///` doc comment
- [ ] 用 `serde` 的 `#[derive(Serialize, Deserialize)]` 而非手动实现
- [ ] DTO 用 `#[serde(rename_all = "camelCase")]` 保证 JSON 驼峰
- [ ] import 按标准库 → 第三方 → 内部顺序排列（用 `cargo fmt` 自动处理）
- [ ] 无 `println!()` 调试代码，统一用 `tracing::info!`/`debug!`
- [ ] 日志不输出密码、密钥等敏感信息
- [ ] 配置通过 `figment` + `config.toml` + `.env` 管理，不硬编码
- [ ] 所有 `async fn` 内部使用 `await`
- [ ] `cargo clippy -- -D warnings` 无警告

### 数据库相关

- [ ] Entity 字段名使用 `snake_case`，与 PostgreSQL 列名一致
- [ ] 所有查询加上 `is_deleted == 0` 过滤
- [ ] 使用 SeaORM 的 `find()` / `filter()` 而非裸 SQL（复杂联表除外）
- [ ] 多步写操作使用 `transaction()`
- [ ] `smallint` 映射 `i16`，`bigint` 映射 `i64`

### API 相关

- [ ] 路由 prefix 统一 `/api/v1/模块名`
- [ ] 固定路径端点定义在路径参数端点之前
- [ ] 分页参数命名为 `pageNum` / `pageSize`
- [ ] JSON 字段使用 camelCase（`deptId`、`createTime`）
- [ ] 统一返回 `Result<T>` / `PageResult<T>` 包装
- [ ] HTTP 状态码恒为 200，业务码通过 body 的 `code` 传递
- [ ] 错误返回使用 `ResultCode` 枚举，不硬编码字符串
- [ ] 敏感接口添加 `require_perm("xxx")` 权限中间件
- [ ] 每个 handler 添加 `#[utoipa::path]` 注解

### Service 层

- [ ] Service 构造函数接受 `&DatabaseConnection`
- [ ] 数据不存在时返回 `AppError::Business(ResultCode::AccountNotFound/...)`
- [ ] 批量操作前检查参数非空
- [ ] `to_vo` / `from` 等转换方法用 `impl From<Model> for XxxVO`

## 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| `println!("debug")` | 无日志级别、无时间戳 | `tracing::info!()` / `tracing::debug!()` |
| 硬编码配置 | 不便运维 | 用 `figment` + `config.toml` + `.env` |
| `unwrap()` 在生产代码 | panic 风险 | 用 `?` + `AppError` 处理 |
| SQL 查询缺 `is_deleted = 0` | 查到已删除数据 | 所有查询加逻辑删除条件 |
| 固定路径在 `/:id` 之后 | axum 路由冲突 | 固定路径注册在前 |
| `code="A0230"` 硬编码字符串 | 易出错 | 用 `ResultCode::AccessTokenInvalid.code()` |
| 未加 `#[serde(rename)]` | JSON 字段非驼峰 | DTO 用 `#[serde(rename_all = "camelCase")]` |
| 所有错误 `unwrap_or_default()` | 隐藏错误 | 用 `?` 传播，由全局异常处理 |
| `sea-orm` features 用 `sqlx-mysql` | 连不上 PostgreSQL | 用 `sqlx-postgres` |
| Entity 手写 | 易与表结构脱节 | 用 `sea-orm-cli generate entity` 自动生成 |

## Docker 部署

```yaml
# docker/docker-compose.yml
services:
  api:
    build: ..
    ports: ["8000:8000"]
    depends_on: [postgres, redis, minio]
    environment:
      APP_DATABASE__URL: postgres://postgres:123456@postgres:5432/app_admin
      APP_REDIS__URL: redis://redis:6379/0
      APP_MINIO__ENDPOINT: http://minio:9000

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app_admin
      POSTGRES_PASSWORD: "123456"
    ports: ["5432:5432"]
    volumes:
      - pg_data:/var/lib/postgresql/data
      - <数据库初始化脚本>:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio
    ports: ["9000:9000", "9001:9001"]
    command: server /data --console-address ":9001"
    volumes: ["minio_data:/data"]

volumes:
  pg_data:
  minio_data:
```
