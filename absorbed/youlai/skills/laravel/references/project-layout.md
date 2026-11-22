# 项目布局

修改技术栈与目录结构时读取。以当前仓库配置为准。

---

## 技术栈

| 层 | 选型 | 说明 |
| --- | --- | --- |
| 运行环境 | **PHP 8.3+** | PHP 8 属性注解、枚举、只读属性 |
| Web 框架 | **Laravel 13** | 路由、容器、中间件、队列 |
| ORM | **Eloquent** | ActiveRecord 风格，对标 MyBatis-Plus |
| 认证 | **tymon/jwt-auth** | JWT 自包含 Token，guard 名 `admin` |
| 缓存 | **Redis 7.x** | `cache()` / `Cache::` + Redis 驱动 |
| 数据库 | **MySQL 8.0+** | 本项目脚本 `database/schema.sql`（多租户版） |
| 验证码 | **gregwar/captcha** | 图形验证码 base64 输出 |
| 密码哈希 | **password_hash** | `PASSWORD_DEFAULT`（bcrypt） |
| 接口文档 | **Swagger / OpenAPI** | `/api/docs` 或 Knife4j 风格 |
| 代码生成 | **模板 + stub** | `templates/` 下 `.stub`/`.tpl` 生成前后端 CRUD |
| 实时通信 | **SSE** | `php artisan sse:start` 独立常驻进程 |
| 测试 | **PHPUnit** | `phpunit.xml` + `tests/` |
| 包管理 | **Composer** | `composer.json` |
| 前端构建 | **Vite** | `vite.config.js` |
| 代码质量 | **Pint** | Laravel 官方代码风格 |

> **含多租户**：Laravel 项目 实现多租户（`tenant_id` 字段 + `sys_tenant` 表 + 切换租户接口），新增模块需在查询中携带 `tenant_id` 隔离条件。

## 目录结构

```
Laravel 项目/
├── app/
│   ├── Attributes/                # 自定义属性类（如 LogAction）
│   ├── Common/                    # 通用工具/枚举/常量
│   │   ├── Enums/                 # ResultCode 业务码枚举
│   │   ├── Constants/             # RedisKey 等常量
│   │   └── Interfaces/            # IResultCode 接口
│   ├── Exceptions/                # BusinessException 业务异常
│   ├── Extensions/                # 框架扩展
│   ├── Http/
│   │   ├── Controllers/           # 控制器
│   │   │   ├── Controller.php     # 抽象基类（ApiResponse + validateScene）
│   │   │   └── V1/                # API v1 版本控制器
│   │   │       ├── AuthController.php
│   │   │       └── SysUserController.php
│   │   ├── Middleware/            # jwt.admin / permission / 限流等中间件
│   │   └── Validates/             # 表单验证类（按模块划分）
│   ├── Models/                    # Eloquent 模型（继承 Base）
│   │   ├── Base.php               # 基础模型（状态/删除常量、时间字段）
│   │   └── SysUser.php
│   ├── Services/                  # 业务逻辑层（继承 BaseService）
│   │   ├── BaseService.php        # 基础服务（LoggableService）
│   │   └── SysUserService.php
│   ├── Pagination/                # 分页相关
│   ├── Providers/                 # 服务提供者
│   ├── Events/                    # 领域事件
│   ├── Scope/                     # 查询作用域
│   ├── Traits/                    # 可复用 Trait（ApiResponse 等）
│   └── Utils/                     # 工具类（VerifyCode / LogContext）
├── bootstrap/                     # 框架启动（app.php 注册中间件别名）
├── config/                        # 配置文件
├── database/                      # 迁移 / 工厂 / 填充 / SQL
│   └── schema.sql    # 系统数据库脚本（多租户版）
├── public/                        # 入口目录（index.php）
├── resources/                     # 视图 / 语言包 / 前端资源
├── routes/                        # 路由定义（api.php / web.php / console.php）
├── storage/                       # 运行时存储
├── templates/                     # 代码生成模板（.stub / .tpl）
├── tests/                         # PHPUnit 测试
├── artisan                        # Laravel 命令行入口
├── composer.json
└── .env                           # 环境配置
```

**分层与依赖关系**：

- `Models/` 是纯 Eloquent 模型，依赖 `Base`
- `Services/` 是业务层，依赖 `Models/` 与 `Validates/`
- `Http/Controllers/V1/` 是接口层，依赖 `Services/` 与 `Validates/`，通过 `validateScene()` 复用验证器
- `Common/` 是常量/枚举/接口，被所有层共享
- `Traits/ApiResponse.php` 提供统一响应，被 `Controller` 与 `BaseService` 共用
