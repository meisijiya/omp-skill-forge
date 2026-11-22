# 新增模块

修改新增业务模块的完整步骤时读取。以当前仓库配置为准。

## 目录

- 添加新模块 — 完整教程

---

## 添加新模块 — 完整教程

以添加 **"数据字典项"** 模块为例，展示从零到完整的步骤。

### Step 1: 检查 ORM 模型

确认 `app/system/dict/models.py` 中已有对应的 ORM 模型。若无，创建：

```python
# app/system/dict/models.py
class SysDictItem(Base, BaseIdMixin):
    __tablename__ = "sys_dict_item"
    dict_code: Mapped[str | None] = mapped_column(String(50))
    value: Mapped[str | None] = mapped_column(String(50))
    label: Mapped[str | None] = mapped_column(String(100))
    tag_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer, default=1)
    sort: Mapped[int] = mapped_column(Integer, default=0)
```

### Step 2: 创建模块目录

```bash
mkdir app/dict_item
```

### Step 3: 创建 `schemas.py`

```python
# app/dict_item/schemas.py
"""字典项 Schemas。"""
from pydantic import BaseModel, Field

class DictItemCreate(BaseModel):
    """创建字典项表单。"""
    dictCode: str = Field(..., max_length=50, description="关联字典编码")
    value: str = Field(..., max_length=50, description="字典项值")
    label: str = Field(..., max_length=100, description="字典项标签")
    tagType: str | None = Field(default=None, max_length=50, description="标签类型")
    status: int = Field(default=1, description="状态 1-正常 0-禁用")
    sort: int = Field(default=0, description="排序")

class DictItemUpdate(DictItemCreate):
    """更新字典项表单。"""
    id: int = Field(..., description="字典项ID")

class DictItemVO(BaseModel):
    """字典项视图对象。"""
    id: int | None = None
    dictCode: str = ""
    value: str = ""
    label: str = ""
    tagType: str | None = None
    status: int = 1
    sort: int = 0
    model_config = {"from_attributes": True}

class DictItemQuery(BaseModel):
    """字典项查询参数。"""
    dictCode: str = Field(..., description="字典编码")
```

### Step 4: 创建 `service.py`

```python
# app/dict_item/service.py
"""字典项服务。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BusinessException
from app.response import ResultCode
from app.dict.models import SysDictItem
from app.dict_item.schemas import (
    DictItemCreate, DictItemUpdate, DictItemVO, DictItemQuery,
)

class DictItemService:
    """字典项管理服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_items(self, dict_code: str) -> list[DictItemVO]:
        """根据字典编码查询字典项列表。"""
        rows = await self.db.execute(
            select(SysDictItem)
            .where(SysDictItem.dict_code == dict_code)
            .order_by(SysDictItem.sort.asc())
        )
        items = rows.scalars().all()
        return [DictItemVO.model_validate(it, from_attributes=True) for it in items]

    async def get_by_id(self, item_id: int) -> DictItemVO:
        """根据 ID 查询字典项。"""
        obj = await self.db.get(SysDictItem, item_id)
        if obj is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="字典项不存在")
        return DictItemVO.model_validate(obj, from_attributes=True)

    async def create(self, form: DictItemCreate) -> DictItemVO:
        """创建字典项。"""
        obj = SysDictItem(**form.model_dump())
        self.db.add(obj)
        await self.db.flush()
        return DictItemVO.model_validate(obj, from_attributes=True)

    async def update(self, form: DictItemUpdate) -> DictItemVO:
        """更新字典项。"""
        obj = await self.db.get(SysDictItem, form.id)
        if obj is None:
            raise BusinessException(code=ResultCode.DATA_NOT_FOUND, msg="字典项不存在")
        for key, val in form.model_dump(exclude={"id"}).items():
            setattr(obj, key, val)
        await self.db.flush()
        return DictItemVO.model_validate(obj, from_attributes=True)

    async def delete(self, ids: str) -> int:
        """批量删除字典项。"""
        id_list = [int(x) for x in ids.split(",") if x.strip()]
        for iid in id_list:
            obj = await self.db.get(SysDictItem, iid)
            if obj:
                await self.db.delete(obj)
        await self.db.flush()
        return len(id_list)
```

### Step 5: 创建 `router.py`

```python
# app/dict_item/router.py
"""字典项路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_perm
from app.response import Result
from app.dict_item.schemas import (
    DictItemCreate, DictItemUpdate,
)
from app.dict_item.service import DictItemService

router = APIRouter(prefix="/api/v1/dict/items", tags=["字典管理"])

@router.get("/{dict_code}", summary="字典项列表")
async def get_dict_items(dict_code: str, db: AsyncSession = Depends(get_db)):
    items = await DictItemService(db).get_items(dict_code)
    return Result(data=items)

@router.get("/{item_id}/detail", summary="字典项详情")
async def get_dict_item(item_id: int, db: AsyncSession = Depends(get_db)):
    vo = await DictItemService(db).get_by_id(item_id)
    return Result(data=vo)

@router.post("", summary="创建字典项",
    dependencies=[Depends(require_perm("sys:dict:create"))])
async def create_dict_item(form: DictItemCreate,
    db: AsyncSession = Depends(get_db)):
    vo = await DictItemService(db).create(form)
    return Result(data=vo)

@router.put("/{item_id}", summary="更新字典项",
    dependencies=[Depends(require_perm("sys:dict:edit"))])
async def update_dict_item(item_id: int, form: DictItemUpdate,
    db: AsyncSession = Depends(get_db)):
    form.id = item_id
    vo = await DictItemService(db).update(form)
    return Result(data=vo)

@router.delete("/{ids}", summary="删除字典项",
    dependencies=[Depends(require_perm("sys:dict:delete"))])
async def delete_dict_items(ids: str, db: AsyncSession = Depends(get_db)):
    count = await DictItemService(db).delete(ids)
    return Result(data=count)
```

### Step 6: 创建 `__init__.py`

```python
# app/dict_item/__init__.py
```

### Step 7: 在 `main.py` 注册路由

```python
# app/main.py — create_app() 函数中追加
from app.dict_item.router import router as dict_item_router
app.include_router(dict_item_router)
```

### Step 8: 验证

```bash
# 启动服务
fastapi dev app/main.py

# 访问 Swagger 确认路由已注册
open http://localhost:8000/api/v1/swagger-ui.html
```

### 模块文件清单

```
app/dict_item/
├── __init__.py
├── schemas.py       # ← 第一步创建
├── service.py       # ← 第二步创建
└── router.py        # ← 第三步创建
```

### 扩展：单文件模块（简单 CRUD）

对于日志管理等简单模块，可将 schemas + service + router 合并为一个文件：

```python
# app/system/log/router.py
# ┌── schemas ──┐
class LogQuery(BaseModel): ...
class LogVO(BaseModel): ...

# ┌── service ──┐
class LogService: ...
    async def get_page(self, query): ...

# ┌── router ──┐
router = APIRouter(prefix="/api/v1/logs", tags=["日志管理"])

@router.get("", ...)
async def get_logs(...): ...
```

> **选择标准**：单个实体 < 5 个接口 → 单文件模块；> 5 个接口或有复杂查询 → 拆分为 schemas + service + router。
