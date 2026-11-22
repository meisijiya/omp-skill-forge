# 接口契约

修改路由、状态码、业务错误码与统一响应时读取。以当前仓库配置为准。

## 目录

- 路由与 API 规范
- HTTP 状态码与业务错误码
- 统一响应格式

---

## 路由与 API 规范

### 路由前缀

```python
router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])
```

| 模块 | 前缀 |
|------|------|
| 认证 | `/api/v1/auth` |
| 用户 | `/api/v1/users` |
| 角色 | `/api/v1/roles` |
| 菜单 | `/api/v1/menus` |
| 部门 | `/api/v1/depts` |
| 字典 | `/api/v1/dict` |
| 配置 | `/api/v1/configs` |
| 通知 | `/api/v1/notices` |
| 日志 | `/api/v1/logs` |
| 文件 | `/api/v1/files` |
| SSE | `/api/v1/sse` |

### 标准 CRUD 路径

| 操作 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 分页列表 | `GET` | `/api/v1/users` | Query 参数：`pageNum`/`pageSize`/`keywords`/... |
| 详情 | `GET` | `/api/v1/users/{user_id}` | 路径参数 `user_id: int` |
| 新增 | `POST` | `/api/v1/users` | Body: `UserCreate` |
| 更新 | `PUT` | `/api/v1/users/{user_id}` | Body: `UserUpdate` |
| 批量删除 | `DELETE` | `/api/v1/users/{ids}` | `ids` 逗号分隔 |
| 修改状态 | `PATCH` | `/api/v1/users/status` | Body: `UserStatusForm` |
| 重置密码 | `PATCH` | `/api/v1/users/password` | Body: `UserPasswordForm` |
| 导出 | `GET` | `/api/v1/users/export` | 返回 StreamingResponse xlsx |
| 导入 | `POST` | `/api/v1/users/import` | UploadFile xlsx |
| 导入模板 | `GET` | `/api/v1/users/template` | 下载模板 xlsx |
| 下拉选项 | `GET` | `/api/v1/roles/options` | 返回 `[{value, label}]` |

### 路由注册顺序（重要！）

**固定路径端点必须定义在路径参数端点之前**，否则 `/{user_id}` 会先被匹配：

```python
# ✅ 正确顺序
@router.get("")                    # GET /api/v1/users
@router.get("/template")           # 固定路径 —— 必须在 /{user_id} 前
@router.get("/export")             # 固定路径
@router.post("/import")            # 固定路径
@router.patch("/status")           # 固定路径
@router.patch("/password")         # 固定路径

@router.post("")                   # POST /api/v1/users
@router.get("/{user_id}")          # 路径参数 —— 最后注册
@router.put("/{user_id}")          # 路径参数
@router.delete("/{ids}")           # 路径参数
```

### Router 函数模板

```python
# router.py — 完整模板

import io
import logging
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook

from app.database import get_db
from app.dependencies import require_perm
from app.response import Result
from app.user.schemas import UserCreate, UserQuery, UserUpdate, UserVO
from app.user.service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.get("", summary="用户分页列表",
    dependencies=[Depends(require_perm("sys:user:list"))])
async def get_user_page(
    pageNum: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keywords: str | None = Query(default=None),
    status: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """分页查询用户列表。

    - **pageNum**: 当前页码
    - **pageSize**: 每页条数（1-100）
    - **keywords**: 搜索关键词（用户名/昵称/手机号）
    - **status**: 状态筛选
    """
    query = UserQuery(pageNum=pageNum, pageSize=pageSize,
                      keywords=keywords, status=status)
    result = await UserService(db).get_page(query)
    return Result(data=result)

@router.get("/{user_id}", summary="用户详情",
    dependencies=[Depends(require_perm("sys:user:detail"))])
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """根据 ID 获取用户详情。"""
    vo = await UserService(db).get_by_id(user_id)
    return Result(data=vo)

@router.post("", summary="创建用户",
    dependencies=[Depends(require_perm("sys:user:create"))])
async def create_user(form: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建新用户，自动分配角色。"""
    vo = await UserService(db).create(form)
    return Result(data=vo)

@router.put("/{user_id}", summary="更新用户",
    dependencies=[Depends(require_perm("sys:user:edit"))])
async def update_user(user_id: int, form: UserUpdate,
                      db: AsyncSession = Depends(get_db)):
    """更新用户信息及角色。"""
    form.id = user_id
    vo = await UserService(db).update(form)
    return Result(data=vo)

@router.delete("/{ids}", summary="删除用户",
    dependencies=[Depends(require_perm("sys:user:delete"))])
async def delete_users(ids: str, db: AsyncSession = Depends(get_db)):
    """批量逻辑删除用户。"""
    count = await UserService(db).delete(ids)
    return Result(data=count, msg=f"成功删除 {count} 条记录")
```

## HTTP 状态码与业务错误码

### 设计理念：双轨制（HTTP 语义 + 业务码）

> **背景**：社区存在两派争论——"统一返回 200，用 body 的 code 区分" vs "用正确的 HTTP 状态码"。本规范采用 **RFC 9457 Problem Details** 思路 + 兼容 参考实现/vue3-element-admin 前端拦截器的**双轨制方案**。

| 方案 | 代表 | 缺陷 |
|------|------|------|
| 统一 200 | 部分国内项目、GraphQL | 违背 HTTP 语义；网关/监控无法识别错误；API 工具误判成功 |
| 纯 HTTP 状态码 | RFC 9457、Zuplo 最佳实践 | 无法表达细粒度业务错误（如"用户名不存在" vs "密码错误"都是 401） |
| **双轨制（本项目）** | FastAPI 项目 | — |

**双轨制原则**：

```
HTTP 状态码 → 大类划分（2xx 成功 / 4xx 客户端错误 / 5xx 服务端错误）
业务错误码  → 细粒度分类（A0230 Token 过期 / A0402 密码错误 / B0003 数据不存在）
```

- **HTTP 状态码**：协议层，用于网关/监控/API 工具识别请求成败
- **业务错误码**：应用层，用于前端精确判断业务逻辑
- **两者共存**：每个错误响应同时携带正确的 HTTP 状态码和 body 中的 `code` 字段

### HTTP 状态码使用规范

| HTTP 状态 | 含义 | 使用场景 | body 中的 code 示例 |
|-----------|------|----------|---------------------|
| `200` | 成功 | 业务操作成功 | `00000` |
| `400` | 客户端请求错误 | 请求格式错误、参数缺失 | `A0400` |
| `401` | 未认证 | Token 无效/过期、未登录 | `A0230`、`A0231` |
| `403` | 无权限 | 已认证但无操作权限 | `A0301` |
| `404` | 资源不存在 | 查询的数据不存在 | `B0003` |
| `409` | 冲突 | 唯一键冲突、状态冲突 | `B0002` |
| `422` | 参数校验失败 | Pydantic 校验失败 | `A0400` |
| `500` | 服务器内部错误 | 未捕获异常、系统错误 | `B0001` |

> **为什么不用 4xx 表示所有业务错误？**
> HTTP 状态码应反映**协议层**的成败。"密码错误"是业务校验失败而非请求格式错误，用 400 会与参数格式错误混淆。本项目将"密码错误"归为 401（认证失败），"用户名不存在"归为 404（资源不存在），"唯一键冲突"归为 409（冲突）——选择语义最匹配的状态码。

### 业务错误码（ResultCode）

```python
from enum import Enum

class ResultCode(str, Enum):
    """业务错误码 — 与 HTTP 状态码配合使用。

    首位编码：
      0 - 成功
      A - 用户端错误（4xx）
      B - 系统端错误（5xx）
      C - 第三方服务错误（5xx）
    """

    # ── 成功 ──
    SUCCESS = "00000"                    # → HTTP 200

    # ── 认证/授权类（4xx）──
    TOKEN_INVALID = "A0230"              # → HTTP 401 访问令牌无效或过期
    TOKEN_REFRESH_FAIL = "A0231"         # → HTTP 401 刷新令牌无效或过期
    ACCESS_DENIED = "A0301"              # → HTTP 403 权限不足

    # ── 参数/校验类（4xx）──
    PARAM_VALID_FAIL = "A0400"           # → HTTP 422 参数校验失败
    USERNAME_NOT_FOUND = "A0401"         # → HTTP 404 用户名不存在
    BAD_CREDENTIALS = "A0402"            # → HTTP 401 密码错误
    USER_DISABLED = "A0403"             # → HTTP 403 用户被禁用
    CAPTCHA_ERROR = "A0404"             # → HTTP 400 验证码错误

    # ── 业务异常 ──
    SYSTEM_ERROR = "B0001"              # → HTTP 500 系统执行异常（全局兜底）
    DUPLICATE_KEY = "B0002"              # → HTTP 409 数据重复
    DATA_NOT_FOUND = "B0003"             # → HTTP 404 数据不存在
    OPERATE_DENIED = "B0004"             # → HTTP 403 操作不允许

    @property
    def http_status(self) -> int:
        """业务错误码 → 对应的 HTTP 状态码。"""
        mapping = {
            "00000": 200,
            "A0230": 401, "A0231": 401,
            "A0301": 403, "A0403": 403, "B0004": 403,
            "A0400": 422,
            "A0401": 404, "B0003": 404,
            "A0402": 401,
            "A0404": 400,
            "B0002": 409,
            "B0001": 500,
        }
        return mapping.get(self.value, 500)
```

### BusinessException 与全局异常处理器

```python
# app/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.response import ResultCode

class BusinessException(Exception):
    """业务异常 — 携带业务错误码和 HTTP 状态码。"""

    def __init__(self, code: ResultCode = ResultCode.SYSTEM_ERROR, msg: str = "系统异常"):
        self.code = code
        self.msg = msg
        self.http_status = code.http_status  # ← 自动映射 HTTP 状态码
        super().__init__(msg)

async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """业务异常处理 — 返回语义化 HTTP 状态码 + body 中的 code。"""
    return JSONResponse(
        status_code=exc.http_status,            # ← HTTP 401/403/404/409/500...
        content={"code": exc.code.value, "msg": exc.msg, "data": None},
    )

async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """参数校验异常 — HTTP 422 + body code A0400。"""
    return JSONResponse(
        status_code=422,
        content={"code": ResultCode.PARAM_VALID_FAIL.value, "msg": str(exc), "data": None},
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局兜底 — HTTP 500 + body code B0001。"""
    return JSONResponse(
        status_code=500,
        content={"code": ResultCode.SYSTEM_ERROR.value, "msg": "系统执行异常", "data": None},
    )
```

### 业务异常抛出示例

```python
# ✅ 认证失败 → HTTP 401
raise BusinessException(code=ResultCode.TOKEN_INVALID, msg="访问令牌无效或过期")
raise BusinessException(code=ResultCode.BAD_CREDENTIALS, msg="密码错误")

# ✅ 权限不足 → HTTP 403
raise BusinessException(code=ResultCode.ACCESS_DENIED, msg="权限不足")

# ✅ 数据不存在 → HTTP 404
raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="用户不存在")
raise BusinessException(code=ResultCode.USERNAME_NOT_FOUND, msg="用户名不存在")

# ✅ 唯一键冲突 → HTTP 409
raise BusinessException(code=ResultCode.DUPLICATE_KEY, msg="用户名已存在")

# ✅ 操作不允许 → HTTP 403
raise BusinessException(code=ResultCode.OPERATE_DENIED, msg="存在子菜单，无法删除")

# ✅ 系统异常 → HTTP 500（由全局异常处理器兜底，通常不手动抛出）
```

### 与前端 axios 拦截器的兼容性

vue3-element-admin 的 axios 拦截器**同时处理两个分支**，天然兼容双轨制：

```typescript
// vue3-element-admin/src/utils/request.ts（已验证）
http.interceptors.response.use(
  (response) => {
    // HTTP 2xx 进入此分支
    const { code, data, msg } = response.data;
    if (code === "00000") return data;        // 业务成功
    ElMessage.error(msg);                      // 业务错误（HTTP 200 但 code 非 00000）
    return Promise.reject(new Error(msg));
  },
  (error) => {
    // HTTP 4xx/5xx 进入此分支
    const { code, msg } = error.response.data;
    if (code === "A0230") { /* Token 过期 → 自动刷新 */ }
    if (code === "A0231") { /* Refresh 失败 → 跳转登录 */ }
    if (code === "A0301") { /* 权限不足 → 刷新权限 */ }
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);
```

> **关键**：前端无论进入哪个分支，都从 `response.data.code` 读取业务码。双轨制方案前端**无需任何改动**。

### 错误码设计规范

| 首位 | 含义 | HTTP 大类 | 范围 |
|------|------|-----------|------|
| `0` | 成功 | 2xx | `00000` |
| `A` | 用户端错误 | 4xx | `A0001-A0999` |
| `B` | 系统端错误 | 5xx | `B0001-B0999` |
| `C` | 第三方服务错误 | 5xx | `C0001-C0999` |

**第二位子分类**（A 类）：

| 第二位 | 子类 | 示例 |
|--------|------|------|
| `0` | 通用 | `A0001` 未知错误 |
| `2` | 认证/Token | `A0230` Token 过期、`A0231` Refresh 失效 |
| `3` | 授权/权限 | `A0301` 权限不足 |
| `4` | 参数校验 | `A0400` 校验失败、`A0401` 用户不存在、`A0402` 密码错误 |
| `5` | 租户 | `A0250` 需要选择租户 |

**新增错误码流程**：

1. 在 `ResultCode` 枚举中添加新值
2. 在 `http_status` property 的 mapping 中添加映射
3. 更新本规范的 5.3 节表格

## 统一响应格式

### Result 结构

```json
{
    "code": "00000",
    "msg": "成功",
    "data": { … }
}
```

```python
from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class Result(BaseModel, Generic[T]):
    code: str = Field(default="00000", description="业务状态码")
    msg: str = Field(default="成功", description="提示信息")
    data: T | None = Field(default=None, description="响应数据")
```

### PageResult 结构

```json
{
    "code": "00000",
    "msg": "成功",
    "data": {
        "list": [ … ],
        "total": 100,
        "pageNum": 1,
        "pageSize": 10
    }
}
```

```python
class PageResult(BaseModel):
    list: list = Field(default_factory=list)
    total: int = Field(default=0)
    pageNum: int = Field(default=1)
    pageSize: int = Field(default=10)
```

### 分页查询参数

```python
class PageQuery(BaseModel):
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
```

> **前端约定**：分页参数命名为 `pageNum` / `pageSize`（camelCase），兼容 vue3-element-admin 的 TablePage 组件。

### 返回示例

```python
# 成功返回
return Result(data=user_vo)

# 成功返回（自定义消息）
return Result(data=count, msg=f"成功删除 {count} 条记录")

# 成功返回（无数据）
return Result(data=None)

# 错误返回
return Result(code=ResultCode.CAPTCHA_ERROR, msg="验证码错误", data=None)
```
