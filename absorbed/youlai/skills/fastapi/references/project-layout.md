# 项目布局

修改技术栈与目录结构时读取。以当前仓库配置为准。

---

## 技术栈

| 层 | 选型 | 说明 |
|---|------|------|
| Web 框架 | **FastAPI** 0.115+ | 异步原生、Pydantic v2 集成、自动 OpenAPI 文档 |
| ASGI 服务器 | **Uvicorn** 0.30+ | FastAPI 官方推荐 |
| ORM | **SQLAlchemy 2.0** + **asyncpg** | `Mapped` + `mapped_column` 声明式、完整 async 支持 |
| 数据验证 | **Pydantic v2** | Rust 核心、FastAPI 原生集成 |
| 数据库 | **PostgreSQL** 16+ | 生产级、asyncpg 异步驱动 |
| 缓存 | **Redis** 7.x | `redis[hiredis]` 异步客户端 |
| 认证 | **PyJWT** 2.x + **bcrypt** 4.x | JWT 签发/验签、密码哈希 |
| 日志 | **loguru** 0.7+ | 零配置、彩色输出、自动 rotate |
| 包管理 | **uv** | Rust 编写、10-100x pip 速度 |
| 代码质量 | **ruff** + **mypy** | Lint + 格式化 + 静态类型检查 |
| 测试 | **pytest** + **httpx** | httpx AsyncClient 直测 FastAPI |

## 目录结构

> 目录结构以社区标杆 [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) 为准。

```
app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口：挂载路由、中间件、异常处理器
│   ├── config.py               # Pydantic Settings
│   ├── database.py             # 异步引擎 + session + get_db
│   ├── redis.py                # Redis 连接池 + get_redis
│   ├── response.py             # Result[T] + ResultCode 统一响应
│   ├── exceptions.py           # BusinessException + 全局异常处理器
│   ├── enums.py                 # 全局枚举
│   ├── pagination.py           # PageQuery / PageResult
│   ├── constants.py            # 全局常量：安全前缀 / REDIS_ 前缀 / 系统级
│   ├── dependencies.py         # 全局依赖 get_current_user / require_perm
│   ├── middleware.py           # CORS + 请求日志 + 限流
│   ├── registry.py             # 导入全部域模型，触发 Base.metadata 注册（Base/Mixin 在 database.py）
│   ├── ai.rs                     # AI 辅助接口
│   ├── rate_limit.py             # 限流配置
│   ├── serializers.py            # 复用序列化器
│   ├── utils.py                  # 通用工具
│   ├── auth/                   # 认证域：router.py / schemas.py / service.py / token.py / utils.py
│   ├── captcha/                # 验证码：service.py / constants.py
│   ├── system/                 # 系统管理域
│   │   ├── user/  role/  menu/  dept/  dict/  log/  form/
│   │   │   └── 各含 router.py  schemas.py  service.py  models.py
│   │   │       （role/ 含 constants.py、data_permission.py；log/ 含 constants.py、operation_log.py）
│   │   ├── config/             # 仅 models.py + router.py（配置内联，无 schemas/service）
│   │   └── notice/             # 仅 models.py + router.py
│   └── tool/                   # 工具与集成域
│       └── file/  codegen/  wxma/  realtime/   # 文件 / 代码生成 / 微信小程序 / 服务端推送
├── alembic/                    # 数据库迁移
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml              # uv 依赖管理
├── .env.example
├── .gitignore
└── README.md
```

**设计原则**：
- 按业务域组织：每个域目录自包含 `router/schemas/models/service`（按需含 `constants/dependencies/exceptions`），域间通过显式模块名导入。
- `models/` 仅放 ORM 基类与全域注册，纯 ORM 不依赖任何业务层。
- 全局基础设施（config / database / redis / response / exceptions / pagination / constants / dependencies / middleware）平铺在 `app/` 根，被各域共享。
- 不设 `core/` `common/` `framework/` `modules/` 分层包。
