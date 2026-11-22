# 交付质量

修改注释、检查清单、反模式与部署时读取。以当前仓库配置为准。

## 目录

- 注释规范
- 代码质量检查清单
- 常见反模式
- 单模块文件
- Docker 部署

---

## 注释规范

> **来源**：PEP 257 (Docstring Conventions) + Google Style Docstrings。

### 总则

- **docstring 优先**：所有公共模块、类、函数必须有 docstring
- **自解释代码**：好的命名和结构是自解释的，注释描述"为什么"而非"如何做"
- **中文优先**：与其用半吊子英文，不如用中文把问题说清楚；专有名词保留英文（如 `HTTP`、`async`）
- **同步更新**：代码修改时 docstring 必须同步修改

### docstring 格式（Google 风格）

```python
async def get_user_page(
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keywords: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PageResult:
    """分页查询用户列表。

    根据关键词模糊搜索用户名/昵称/手机号，支持状态筛选。

    Args:
        pageNum: 当前页码，从 1 开始。
        pageSize: 每页条数，1-100。
        keywords: 搜索关键词（用户名/昵称/手机号），为空时查全部。
        db: 异步数据库会话。

    Returns:
        分页结果，包含 list 和 total。

    Raises:
        BusinessException: 当 pageSize 超过 100 时（通常由 Pydantic 校验拦截）。
    """
    ...
```

### 各层注释要点

| 层 | 必须说明 | 示例 |
|----|---------|------|
| 模块（文件头） | 文件职责 | `"""字典项路由。"""` |
| 类 | 职责、关键依赖 | `"""字典项管理服务，依赖 AsyncSession。"""` |
| 公共方法 | 功能、参数、返回值、异常 | 见 11.2 |
| 私有方法（`_` 前缀） | 简要说明即可 | `"""ORM 模型 → 视图对象。"""` |

### 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| `def get_user(id): pass` 无 docstring | 公共方法无文档 | 补充 docstring |
| `"""获取用户"""` 参数无说明 | 缺少 Args/Returns | 补充完整 Args/Returns/Raises |
| docstring 与代码不一致 | 误导维护者 | 代码改动时同步更新 |
| 注释掉的代码块保留 | 历史代码可从 Git 查阅 | 直接删除 |
| `# TODO fix this` | 无标记人、无时间 | `# TODO(zhangsan, 2025/06/01, 下版本修复)` |

### TODO / FIXME 标记规范

| 标记 | 用途 | 格式 | 示例 |
|------|------|------|------|
| `TODO` | 待实现 | `TODO(标记人, 日期, [说明])` | `TODO(zhangsan, 2025/06/01, 扩展邮箱验证码)` |
| `FIXME` | 已知 bug | `FIXME(标记人, 日期, [说明])` | `FIXME(lisi, 2025/06/15, 并发场景偶发死锁)` |

## 代码质量检查清单

### 通用检查

- [ ] 所有公共类、方法有 docstring
- [ ] 用 `Pydantic v2` 的 `model_dump()` 而非 `dict()`
- [ ] 用 `model_validate(obj, from_attributes=True)` 做 ORM → Schema 转换
- [ ] 所有 `.py` 文件有 `# -*- coding: utf-8 -*-` 或 UTF-8 编码
- [ ] import 按标准库 → 第三方 → 内部顺序排列
- [ ] 无未使用的 import
- [ ] 无 `print()` 调试代码，统一用 `logger`
- [ ] 日志不输出密码、密钥等敏感信息
- [ ] 配置通过 `Settings` + `.env` 管理，不硬编码
- [ ] 所有 `async def` 函数内部使用 `await`

### 数据库相关

- [ ] ORM 模型字段名使用 `snake_case`，与数据库列名一致
- [ ] 所有查询加上 `is_deleted == 0` 过滤（如模型有 `SoftDeleteMixin`）
- [ ] 使用 `select` 而非 `Model.query`（SQLAlchemy 2.0+ 风格）
- [ ] 大量数据操作使用 `flush()` 而非频繁 `commit()`
- [ ] `ScalarResult.scalar_one_or_none()` 而非 `first()`（区分 None vs 第一条）

### API 相关

- [ ] 路由 prefix 统一 `"/api/v1/模块名"`
- [ ] 固定路径端点定义在路径参数端点之前
- [ ] 分页参数命名为 `pageNum` / `pageSize`
- [ ] JSON 字段使用 camelCase（`deptId`、`createTime`）
- [ ] 统一返回 `Result[T]` 包装（body 含 `code`/`msg`/`data`）
- [ ] **HTTP 状态码语义化**：成功 200 / 认证失败 401 / 权限不足 403 / 不存在 404 / 冲突 409 / 校验 422 / 系统错误 500
- [ ] 业务错误码与 HTTP 状态码双轨配合（见接口契约）
- [ ] `ResultCode.http_status` property 映射正确
- [ ] 错误返回使用 `ResultCode` 枚举，不硬编码字符串
- [ ] 敏感接口添加 `dependencies=[Depends(require_perm(...))]`
- [ ] tree_path 在 `add + flush` 之后再设置（拿到自增 id）

### Service 层

- [ ] Service 构造函数接受 `db: AsyncSession`
- [ ] 数据不存在时抛出 `BusinessException(code=ResultCode.DATA_NOT_FOUND)`
- [ ] 唯一键冲突时抛出 `BusinessException(code=ResultCode.DUPLICATE_KEY)`
- [ ] 操作不允许时抛出 `BusinessException(code=ResultCode.OPERATE_DENIED)`
- [ ] 批量操作前检查参数非空
- [ ] `_to_vo` / `_to_tree` 等私有方法前缀 `_`

## 常见反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| `print("debug")` | 无日志级别、无时间戳 | `logger.info()` / `logger.debug()` |
| `result.scalars().first()` | 不区分 None vs 第一条 | `result.scalar_one_or_none()` |
| `model.dict()` | Pydantic v2 已废弃 | `model.model_dump()` |
| 硬编码配置 | 不便运维 | 用 `Settings` + `.env` |
| `db.execute()` 后不 `await` | 异步未执行 | `await self.db.execute(...)` |
| `flush` 前取 `obj.id` | 自增 id 尚未生成 | 先 `flush()` 再取 `id` |
| SQL 查询缺 `is_deleted = 0` | 查到已删除数据 | 所有查询加逻辑删除条件 |
| 固定路径在 `/{id}` 之后 | 先被路径参数拦截 | 固定路径注册在前 |
| 重复 import 同一模块 | 不必要 | 合并为单条 import |
| `try/except` 捕获所有异常后 pass | 隐藏错误 | 只捕获已知异常，记录日志 |
| **所有错误统一返回 HTTP 200** | 网关/监控无法识别错误；违背 HTTP 语义 | HTTP 状态码语义化 + body 中 `code` 双轨制（Part 5） |
| **业务错误硬编码 HTTP 状态码** | 如 `JSONResponse(status_code=401)` 散落各处 | 用 `ResultCode.http_status` property 统一映射 |
| **字符串硬编码业务码** | 如 `code="A0230"` | 用 `ResultCode.TOKEN_INVALID.value` 枚举 |

## 单模块文件

对于 `config`、`notice`、`log` 等简单模块，可将 schemas + service + router 合并到单个 `router.py` 文件中，减少文件碎片化。

## Docker 部署

```yaml
# docker/docker-compose.yml
services:
  api:
    build: ..
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:123456@postgres:5432/app_admin
      REDIS_URL: redis://redis:6379/0
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app_admin
      POSTGRES_PASSWORD: 123456
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

```bash
# 启动
docker-compose -f docker/docker-compose.yml up -d
```
