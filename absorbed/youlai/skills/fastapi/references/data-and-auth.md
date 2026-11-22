# 数据与认证

修改模型、ORM、认证鉴权与数据库操作时读取。以当前仓库配置为准。

## 目录

- ORM 模型规范
- 认证与鉴权
- 数据库操作规范

---

## ORM 模型规范

### 基类 Mixin

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, Integer, func

class Base(DeclarativeBase):
    """ORM 声明式基类。"""
    pass

class TimestampMixin:
    """自动管理 create_time / update_time。"""
    create_time: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

class SoftDeleteMixin:
    """逻辑删除标识。"""
    is_deleted: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="逻辑删除 0-未删除 1-已删除"
    )

class BaseIdMixin:
    """自增主键 ID。"""
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
```

### ORM 模型示例

```python
class SysUser(Base, BaseIdMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sys_user"

    username: Mapped[str] = mapped_column(String(64), unique=True, comment="用户名")
    nickname: Mapped[str] = mapped_column(String(64), comment="昵称")
    password: Mapped[str] = mapped_column(String(100), comment="密码")
    dept_id: Mapped[int | None] = mapped_column(BigInteger, comment="部门ID")
    mobile: Mapped[str | None] = mapped_column(String(20), comment="手机号")
    email: Mapped[str | None] = mapped_column(String(100), comment="邮箱")
    status: Mapped[int] = mapped_column(Integer, default=1, server_default="1",
                                         comment="状态 1-启用 0-禁用")
```

### 字段命名对照

| SQL 列名 | ORM 字段 | Schema 字段 | 说明 |
|----------|----------|-------------|------|
| `dept_id` | `dept_id` | `deptId` | 部门ID |
| `create_time` | `create_time` | `createTime` | 创建时间 |
| `is_deleted` | `is_deleted` | — | 逻辑删除（内部使用） |
| `parent_id` | `parent_id` | `parentId` | 父节点ID |

> **转换规则**：ORM → VO 时，`to_vo` 或 `_to_vo` 方法负责 snake_case → camelCase 转换。

### VO 转换模板

```python
@staticmethod
def _to_vo(m: SysUser) -> UserVO:
    """ORM 模型 → 视图对象（snake_case → camelCase）。"""
    return UserVO(
        id=m.id,
        username=m.username,
        deptId=m.dept_id,       # ← 手动映射
        createTime=str(m.create_time) if m.create_time else None,
        # ...
    )
```

## 认证与鉴权

### Token 模式

通过 `SESSION_TYPE` 环境变量切换：

| 值 | 模式 | TokenManager |
|----|------|--------------|
| `jwt`（默认） | JWT 自包含 Token | `JwtTokenManager` |
| `redis-token` | Redis 存储 Token | `RedisTokenManager` |

### 获取当前用户

```python
from app.dependencies import get_current_user

@router.get("/me")
async def my_info(user: SysUserDetails = Depends(get_current_user)):
    return Result(data={"userId": user.userId, "username": user.username})
```

### 权限校验

```python
from app.dependencies import require_perm

# 精确权限
@router.post("", dependencies=[Depends(require_perm("sys:user:create"))])
async def create_user(form: UserCreate, db: AsyncSession = Depends(get_db)):
    ...

# 登录即可（不检查权限）
@router.get("/options", dependencies=[Depends(require_perm())])
async def get_options(db: AsyncSession = Depends(get_db)):
    ...
```

### 权限标识命名规范

```
模块:实体:操作
sys:user:create
sys:user:edit
sys:user:delete
sys:role:list
sys:menu:list
sys:dept:list
```

| 操作 | 说明 |
|------|------|
| `list` | 列表/查询 |
| `detail` | 详情 |
| `create` | 新增 |
| `edit` | 编辑 |
| `delete` | 删除 |
| `import` | 导入 |
| `export` | 导出 |
| `reset-pwd` | 重置密码 |
| `assign-menu` | 分配菜单权限 |

## 数据库操作规范

### 异步查询

```python
# ✅ 正确：使用 async/await
result = await self.db.execute(
    select(SysUser).where(SysUser.id == user_id, SysUser.is_deleted == 0)
)
user = result.scalar_one_or_none()

# ✅ 正确：分页查询
rows = await self.db.execute(
    select(SysUser)
    .where(*conditions)
    .order_by(SysUser.create_time.desc())
    .offset(offset)
    .limit(page_size)
)
users = rows.scalars().all()

# ✅ 正确：原生 SQL（复杂联表查询）
result = await self.db.execute(
    text("""
        SELECT r.code FROM sys_role r
        INNER JOIN sys_user_role ur ON r.id = ur.role_id
        WHERE ur.user_id = :user_id AND r.is_deleted = 0 AND r.status = 1
    """),
    {"user_id": user_id},
)
```

### 事务管理

```python
# 由 get_db() 依赖自动管理：
# yield 前 → session 开始
# yield 后 → commit（成功）或 rollback（异常）
# finally → session.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()     # 自动提交
        except Exception:
            await session.rollback()   # 自动回滚
            raise
        finally:
            await session.close()
```

### 批量操作

```python
# ✅ 批量删除（原生 SQL）
await self.db.execute(
    text("UPDATE sys_user SET is_deleted = 1 WHERE id = ANY(:ids)"),
    {"ids": id_list},
)

# ✅ 批量插入
for data in batch:
    self.db.add(SysConfig(**data))
await self.db.flush()
```
