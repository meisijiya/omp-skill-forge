# 命名规范

修改文件、类型、方法与变量的命名时读取。以当前仓库配置为准。

---

## 命名规范

### 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块目录 | 小写单数名词 | `user/`, `role/`, `menu/` |
| Schema 文件 | `schemas.py` | `app/system/user/schemas.py` |
| Service 文件 | `service.py` | `app/auth/service.py` |
| Router 文件 | `router.py` | `app/system/role/router.py` |
| 配置文件 | `config.py` | `app/config.py` |
| 模型文件 | 按域拆分 | `app/system/user/models.py` |
| 常量文件 | `constants.py` | `app/constants.py`（全局）/ `app/system/user/constants.py`（域） |
| 枚举文件 | `enums.py` / `constants.py` | `app/enums.py`（全局）/ `app/system/role/constants.py`（域枚举） |
| 测试文件 | `test_<模块>.py` | `tests/auth/test_auth.py` |

### 类命名

| 类型 | 规范 | 示例 |
|------|------|------|
| ORM 模型 | `Sys` + PascalCase | `SysUser`, `SysRole`, `SysMenu`, `SysDept` |
| Pydantic Schema | 功能 + 后缀 | `UserCreate`, `UserUpdate`, `UserVO`, `UserQuery` |
| Service 类 | 模块名 + `Service` | `UserService`, `AuthService`, `RoleService` |
| Config 类 | `Settings` | `Settings`（单例） |
| Enum 类 | 功能名 + `Enum` | `StatusEnum`, `DataScopeEnum` |
| Exception | `BusinessException` | 统一使用 `BusinessException` |

**Schema 后缀规范**：

| 后缀 | 用途 | 示例 |
|------|------|------|
| `Create` | 创建表单 | `UserCreate`, `RoleCreate` |
| `Update` | 更新表单 | `UserUpdate`, `MenuUpdate` |
| `VO` | 视图对象（返回） | `UserVO`, `RoleVO`, `DictVO` |
| `Query` | 分页查询参数 | `UserQuery`, `RoleQuery`, `LogQuery` |
| `Form` | 特定操作表单 | `UserPasswordForm`, `RoleMenuForm` |
| `Result` | 响应结果 | `LoginResult`, `ExcelResultVO` |

### 方法命名

| 操作 | 方法名 | 示例 |
|------|--------|------|
| 分页查询 | `get_page` | `async def get_page(self, query: UserQuery) -> PageResult` |
| 单条查询 | `get_by_id` | `async def get_by_id(self, id: int) -> UserVO` |
| 树形查询 | `get_tree` | `async def get_tree(self, keywords: str) -> list[MenuVO]` |
| 下拉选项 | `get_options` | `async def get_options(self) -> list[dict]` |
| 创建 | `create` | `async def create(self, form: UserCreate) -> UserVO` |
| 更新 | `update` | `async def update(self, form: UserUpdate) -> UserVO` |
| 删除（批量） | `delete` | `async def delete(self, ids: str) -> int` |
| 状态变更 | `update_status` | `async def update_status(self, id: int, status: int) -> None` |
| 导入 | `import_<资源>` | `async def import_users(self, data: list) -> dict` |
| 导出 | `export_<资源>` | `async def export_users(self, query) -> list[dict]` |

### 变量命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_list`, `role_codes` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE`, `ROOT_ROLE_CODE` |
| 私有方法 | `_` 前缀 | `def _to_vo(self, m: SysUser) -> UserVO` |
| 布尔变量 | `is_`/`has_` 前缀 | `is_root`, `is_deleted`, `has_perm` |
| 数据库字段 | snake_case | `dept_id`, `create_time` |
| JSON/API 字段 | camelCase | `deptId`, `createTime`, `pageSize` |

> **关键约定**：ORM 模型字段用 snake_case（对应 PostgreSQL 列名），Schema/API 字段用 camelCase（对应前端 JSON 键名）。

### import 排序

```python
# 1. 标准库
import io
import logging

# 2. 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

# 3. 项目内部（按层排序）
from app.database import get_db
from app.constants import ROOT_ROLE_CODE
from app.pagination import PageResult
from app.dependencies import require_perm
from app.exceptions import BusinessException
from app.response import Result, ResultCode
from app.user.models import SysUser
from app.user.schemas import UserCreate, UserVO
```
