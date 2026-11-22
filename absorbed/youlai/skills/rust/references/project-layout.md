# 项目布局

修改技术栈与目录结构时读取。以当前仓库配置为准。

## 目录

- 技术栈
- 目录结构

---

## 技术栈

| 层 | 选型 | 说明 |
|---|------|------|
| 异步运行时 | **tokio** 1.x | Rust 异步事实标准 |
| Web 框架 | **axum** 0.8+ | Tokio 官方，Tower 中间件生态 |
| ORM | **sea-orm** 1.1+ | ActiveRecord + 查询构建器，对标 MyBatis-Plus |
| 迁移工具 | **sea-orm-migration** 1.1+ | SeaORM 内置 |
| 数据验证 | **validator** 0.18+ | `#[validate]` 派生，对标 Bean Validation |
| 数据库 | **PostgreSQL** 16+ | 本项目脚本 `sql/schema.sql`（PG 版；各后端各用自己的脚本，禁止跨项目引用） |
| 数据库驱动 | **sqlx-postgres** 0.8+ | SeaORM 底层，异步原生 |
| 缓存 | **Redis** 7.x | `redis` crate 异步客户端 |
| 本地缓存 | **moka** 0.12+ | 高性能并发缓存 |
| 序列化 | **serde + serde_json** 1.x | Rust 序列化事实标准 |
| 配置管理 | **figment** 0.10+ | 多源合并（TOML + ENV） |
| 日志 | **tracing + tracing-subscriber** 0.1+ | 结构化日志、span 链路追踪 |
| API 文档 | **utoipa + utoipa-swagger-ui** 5.x / 8.x | 宏派生 OpenAPI |
| 认证 | **jsonwebtoken** 9.x + **bcrypt** 0.16+ | JWT 签发/验签、密码哈希 |
| 限流 | **tower-governor** 0.4+ | Tower 兼容 |
| Excel | **calamine**(读) + **rust_xlsxwriter**(写) | 纯 Rust |
| 对象存储 | **aws-sdk-s3** 1.x | MinIO/S3 兼容 |
| 邮件 | **lettre** 0.11+ | 异步 SMTP |
| 任务调度 | **tokio-cron-scheduler** 0.13+ | 进程内 cron |
| 包管理 | **cargo** | Rust 官方 |
| 代码质量 | **clippy + rustfmt** | 官方 linter + 格式化 |
| 测试 | **#[test] + reqwest + testcontainers** | testcontainers 起真实依赖 |

> **不含多租户**：Rust 项目 不实现多租户，数据库为 PostgreSQL。

## 目录结构

```
Rust 项目/
├── src/
│   ├── main.rs                       # 程序入口：装配路由/中间件/状态/优雅关停
│   ├── lib.rs                        # 库入口（供集成测试）
│   ├── app.rs                        # 应用装配：中间件、路由挂载、异常处理
│   ├── config.rs                     # figment 读取 config.toml + .env，强类型 Settings
│   ├── constants.rs                  # SecurityConstants / RedisConstants
│   ├── result_code.rs                # ResultCode 枚举
│   ├── response.rs                   # Result<T> + PageResult<T> + PageData<T>
│   ├── error.rs                      # AppError + AppResult<T>
│   ├── pagination.rs                 # PageQuery / PageData
│   ├── state.rs                      # AppState（db / redis / token manager）
│   ├── rate_limit.rs                 # 限流（tower-governor）
│   ├── openapi.rs                    # utoipa OpenAPI + Swagger UI
│   ├── util.rs                       # 通用工具
│   ├── ai.rs                         # AI 辅助能力
│   ├── core/                         # 跨域能力（不依赖 modules/）
│   │   └── data_scope.rs             # 数据权限
│   ├── entity/                       # SeaORM Entity（sea-orm-cli 生成）
│   │   ├── mod.rs
│   │   ├── sys_user.rs
│   │   ├── sys_role.rs
│   │   └── ...
│   └── modules/                      # 业务模块
│       ├── auth/                     # 认证：token / extractor / permission / service
│       ├── system/                   # 系统管理
│       │   ├── user/                 # 用户
│       │   ├── role/                 # 角色
│       │   ├── menu/                 # 菜单
│       │   ├── dept/                 # 部门
│       │   ├── dict/                 # 字典
│       │   ├── config/               # 配置
│       │   ├── notice/               # 通知
│       │   └── log/                  # 日志
│       ├── form/                     # 动态表单
│       ├── file/                     # 文件
│       ├── codegen/                  # 代码生成
│       └── realtime/                 # 实时推送
├── config/                           # 配置文件
│   ├── config.toml
│   ├── config-dev.toml
│   └── config-prod.toml
├── Cargo.toml
├── rust-toolchain.toml
└── README.md
```

**每个业务模块（如 user）内部结构**：

```
src/modules/system/user/
├── mod.rs        # 路由注册 routes() + handler 函数
├── dto.rs        # 请求/响应 DTO（UserCreate / UserUpdate / UserVO / UserQuery）
└── service.rs    # UserService 业务逻辑
```

**设计原则**：
- `entity/` 是纯 SeaORM Entity，由 `sea-orm-cli` 自动生成，不依赖任何业务层
- 共用类型（响应、错误、业务码、分页、状态、配置）平铺在 `src/` 根，不另建 `common/`、`framework/` 之类的分层包
- `core/` 放跨域能力（如数据权限），不依赖 `modules/`
- `modules/` 是业务层，依赖 `src/` 根的共用类型与 `entity/`
