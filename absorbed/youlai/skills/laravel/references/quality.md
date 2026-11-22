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

- **PHPDoc 优先**：所有公共类、方法用 `/** ... */` 文档注释
- **自解释代码**：好的命名和结构是自解释的，注释描述"为什么"
- **中文优先**：用中文把问题说清楚；专有名词保留英文（`HTTP`、`JWT`、`Eloquent`）
- **同步更新**：代码修改时文档注释必须同步修改

### PHPDoc 格式

```php
/**
 * 用户分页列表
 * @param Request $request 含 pageNum / pageSize / keywords 等查询参数
 * @return JsonResponse 统一响应 { code, msg, data:{list,total} }
 * @throws BusinessException 参数校验失败 / 无权限
 */
public function index(Request $request): JsonResponse
```

### 各层注释要点

| 层 | 必须说明 |
| --- | --- |
| 控制器方法 | 功能、请求参数、返回值结构、可能异常 |
| Service 方法 | 业务语义、数据权限影响、事务范围 |
| Model | 表含义、`$table` / 时间字段 / 软删除策略 |
| Validate | 各 scene 的校验规则与中文报错 |

### TODO / FIXME 标记

| 标记 | 用途 | 格式 |
| --- | --- | --- |
| `TODO` | 待实现 | `// TODO(标记人, 日期, 说明)` |
| `FIXME` | 已知 bug | `// FIXME(标记人, 日期, 说明)` |

## 代码质量检查清单

### 通用检查

- [ ] 所有公共类/方法有 PHPDoc
- [ ] 响应经 `ApiResponse` 输出（`success`/`error`/`fail`），不手动 `response()->json`
- [ ] 数据经 `CaseConversion` 自动转驼峰，手工数组用 camelCase 键
- [ ] 配置通过 `.env` + `config/` 管理，不硬编码
- [ ] 敏感信息（密码、token）不写入日志、不进入响应
- [ ] `composer lint`（Laravel Pint）无风格问题

### 数据库相关

- [ ] Model 字段名 snake_case，与 MySQL 列名一致
- [ ] 所有查询携带 `is_deleted = 0`（或经软删除 trait）
- [ ] 多步写操作使用 `DB::transaction`
- [ ] `id` 用 `string` cast 避免 JS 精度问题
- [ ] 时间字段用 `create_time` / `update_time`（覆盖 Eloquent 默认）

### API 相关

- [ ] 路由 prefix 统一 `/api/v1/模块名`
- [ ] 固定路径端点注册在 `{id}` 路径参数之前
- [ ] 分页参数命名为 `pageNum` / `pageSize`
- [ ] 响应 JSON 键驼峰（`deptId`、`createTime`）
- [ ] HTTP 状态码恒为 200，业务码通过 body 的 `code` 传递
- [ ] 错误用 `ResultCode` 枚举，不硬编码字符串
- [ ] 敏感接口挂载 `jwt.admin` 中间件
- [ ] 多租户查询携带 `tenant_id` 隔离

### Service 层

- [ ] 控制器注入 Service（构造器），不直接写查询
- [ ] 数据不存在返回 `BusinessException(ACCOUNT_NOT_FOUND / NO_DATA_WAS_FOUND)`
- [ ] 批量删除前检查参数非空、保护超级管理员
- [ ] `format()` 统一把 Model 转为驼峰响应数组
- [ ] 写操作加 `#[LogAction]` 属性记录操作日志

## 常见反模式

| 反模式 | 问题 | 正确做法 |
| --- | --- | --- |
| 控制器里写 SQL/查询 | 违反分层 | 查询放到 Service |
| `response()->json([...])` 手写 | 格式不统一、无 traceId | 用 `ApiResponse::success/error` |
| 响应里手写 snake_case 键 | 前端解析失败 | 靠 `CaseConversion` 自动转，或手工用 camelCase |
| SQL 缺 `is_deleted = 0` | 查到已删除数据 | 所有查询加逻辑删除条件 / 用软删除 trait |
| 固定路径在 `{id}` 之后 | 路由被错误匹配 | 固定路径注册在前 |
| `code="A0210"` 硬编码字符串 | 易出错、难维护 | 用 `ResultCode::USER_PASSWORD_ERROR` |
| 密码明文存储 | 安全事故 | `password_hash()` / `Hash::make()` |
| 多租户漏加 `tenant_id` | 跨租户泄漏 | Service 查询携带租户隔离 |
| `dd()` / `dump()` 调试 | 生产泄露 | 用 Laravel 日志 `info()`/`debug()` |
| 验证写在控制器 | 复用差 | 用 `Validate` 类 + `validateScene()` |

## Docker 部署

```yaml
# docker-compose.yml（示意）
services:
  app:
    build: .
    ports: ["8000:8000"]
    depends_on: [mysql, redis]
    environment:
      DB_HOST: mysql
      DB_DATABASE: app_admin
      DB_USERNAME: root
      DB_PASSWORD: "123456"
      REDIS_HOST: redis
    command: php artisan serve --host=0.0.0.0 --port=8000

  sse:
    build: .
    command: php artisan sse:start --auth=admin start
    depends_on: [app]

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: app_admin
      MYSQL_ROOT_PASSWORD: "123456"
    volumes:
      - <数据库初始化脚本>:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
```

> 部署前执行：`composer install --no-dev` 导入 `database/schema.sql`，并配置 `.env` 的 `APP_KEY`、`DB_*`、`REDIS_*` 与 `SSE_LISTEN_URL_ADMIN`。
