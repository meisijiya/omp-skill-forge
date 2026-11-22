# 数据与认证

修改模型、ORM、认证鉴权与数据库操作时读取。以当前仓库配置为准。

## 目录

- Eloquent Model 规范
- 认证与鉴权
- 数据库操作规范

---

## Eloquent Model 规范

### Model 继承 Base

```php
<?php
namespace App\Models;

use App\Traits\HasOperator;
use App\Traits\IsDeletedSoftDeletes;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Tymon\JWTAuth\Contracts\JWTSubject;
use Illuminate\Foundation\Auth\User as Authenticatable;

#[Fillable(['username', 'password', 'avatar', 'mobile', 'email', 'status'])]
#[Hidden(['password', 'salt'])]
class SysUser extends Authenticatable implements JWTSubject
{
    use HasOperator, IsDeletedSoftDeletes;

    protected $table      = 'sys_user';
    protected $primaryKey = 'id';

    const string SYS_USER_TOKEN = 'admin';   // JWT guard 名
    const int USER_FREEZE   = 0;
    const int USER_ACTIVATE = 1;
    const string CAPTCHA_KEY = 'captcha:';

    // 自定义时间字段名（覆盖 Eloquent 默认 created_at/updated_at）
    const string CREATED_AT = 'create_time';
    const string UPDATED_AT = 'update_time';

    protected $casts = [
        'id'          => 'string',
        'status'      => 'integer',
        'create_time' => 'datetime',
        'update_time' => 'datetime',
    ];

    // 统一序列化格式
    protected function serializeDate(\DateTimeInterface $date): string
    {
        return $date->format('Y-m-d H:i:s');
    }
}
```

### 基础模型 Base

`app/Models/Base.php` 定义全项目共享常量，业务模型继承它：

| 常量 | 值 | 含义 |
| --- | --- | --- |
| `STATUS_ENABLE` | `1` | 启用 |
| `STATUS_DISABLE` | `0` | 禁用 |
| `HAVE_DELETED` / `NOT_DELETED` | `1` / `0` | 逻辑删除标记 |
| `CREATED_AT` / `UPDATED_AT` | `'create_time'` / `'update_time'` | 时间字段名 |

### MySQL 类型映射

| MySQL 类型 | PHP 类型 / cast | 说明 |
| --- | --- | --- |
| `bigint` | `string`（cast） | 主键、外键（避免 JS 精度丢失） |
| `int` / `tinyint` | `integer` | 状态、标识位 |
| `varchar(n)` | `string` | 变长字符串 |
| `text` | `string` | 长文本 |
| `datetime` / `timestamp` | `datetime` | 时间 |
| `json` | `array` / `json` | JSON 字段 |

### 逻辑删除与字段命名

- 逻辑删除用 `is_deleted` 字段（由 `IsDeletedSoftDeletes` trait 处理），查询默认过滤 `is_deleted = 0`
- 字段命名对照：

| SQL 列名 | Model 属性 | 响应键（驼峰） | 说明 |
| --- | --- | --- | --- |
| `dept_id` | `dept_id` | `deptId` | 部门 ID |
| `create_time` | `create_time` | `createTime` | 创建时间 |
| `is_deleted` | `is_deleted` | — | 逻辑删除（内部） |
| `parent_id` | `parent_id` | `parentId` | 父节点 ID |

> **转换规则**：Model → 响应 时由 `ApiResponse` 自动完成 snake_case → camelCase，无需手写 `toVo()`。

### 关联与访问器

```php
// 多对多：用户-角色（带 tenant_id pivot）
public function roles(): BelongsToMany
{
    return $this->belongsToMany(SysRole::class, 'sys_user_role', 'user_id', 'role_id')
        ->withPivot('tenant_id')
        ->where('sys_role.is_deleted', Base::NOT_DELETED)
        ->where('status', Base::STATUS_ENABLE);
}

// 访问器：输出时计算 dept_name
public function getDeptNameAttribute(): string
{
    return $this->dept?->name ?? '';
}
```

## 认证与鉴权

### JWT 中间件

路由通过 `jwt.admin` 别名挂载认证中间件（注册于 `bootstrap/app.php`）：

```php
// bootstrap/app.php
$middleware->alias([
    'jwt.admin' => AdminAuthMiddleware::class,
    'permission' => PermissionMiddleware::class,
]);
```

`AdminAuthMiddleware` 行为：
- 用 `auth('admin')->check()` 校验 Token（`admin` 即 `SysUser::SYS_USER_TOKEN`）
- 过期抛 `USER_TOKEN_EXPIRED`，无效抛 `USER_NO_LOGIN`
- 通过后将 `authUser`（来自 `getJWTCustomClaims()`）写入 `$request->attributes->set('authUser', ...)`
- 当前登录用户用 `$request->user()` 或 `request()->user()` 获取

### 登录与 Token

```php
// AuthController::login
$user = $this->userService->accountLogin($account);   // 按 username/email/mobile 猜测字段
if (!password_verify($password, $user->password)) {
    throw new BusinessException(ResultCode::USER_PASSWORD_ERROR->getMsg());
}
return $this->success($this->buildToken($user), '登录成功');
// buildToken 返回 { access_token, refresh_token, token_type: Bearer, expires_in }
```

### 权限校验

- 权限标识格式：`模块:实体:操作`（如 `sys:user:query`、`sys:user:create`）
- 菜单表 `sys_menu.perm` 存放权限字符串，用户权限由角色聚合
- 权限判断在 Service 层通过 `authUser['authorities']`（角色编码 `ROLE_xxx`）与模型 `hasPermission()` 完成
- `PermissionMiddleware` 为占位实现，真正的鉴权在业务/路由层处理；新增敏感接口时按约定在 `routes/api.php` 包 `permission` 中间件或于 Service 内校验

### 多租户

- 模型带 `tenant_id` 字段；用户 JWT claims 含 `tenant_id`
- 切换租户：`POST /api/v1/auth/switch-tenant`
- 租户管理接口：`/api/v1/tenants`、`/api/v1/tenant-plans`
- 新增查询需在 Service 层携带 `tenant_id` 隔离条件，避免跨租户数据泄漏

## 数据库操作规范

### Eloquent 查询

```php
// ✅ 单条查询
$user = SysUser::with(['roles'])->findOrFail($id);

// ✅ 分页 + 筛选
$query = SysUser::query()->select(self::LIST_FIELDS)->with('dept')->orderBy('id', 'asc');
$this->applyFilters($query, $filters);     // 业务筛选
$query->paginate($perPage);

// ✅ 模糊搜索（orWhere 包子查询）
$query->where(function ($q) use ($keyword) {
    $q->whereLike('username', "%{$keyword}%")
      ->orWhere('nickname', 'like', "%{$keyword}%")
      ->orWhere('mobile', 'like', "%{$keyword}%");
});

// ✅ 关联存在性过滤（部门树）
$query->whereHas('dept', function ($q) use ($params) {
    $q->whereRaw("concat(',', concat(tree_path, ',', id), ',') like ?", ["%,{$params['dept_id']},%"]);
});
```

### 事务管理

```php
// ✅ 多步写用事务
return DB::transaction(function () use ($ids) {
    SysUserRole::query()->whereIn('user_id', $ids)->delete();
    SysUser::query()->whereIn('id', $ids)->delete();
    return count($ids);
});
```

### 批量与关联操作

```php
// ✅ 创建并同步多对多
$user = SysUser::query()->create($data);
if (!empty($data['role_ids'])) {
    $user->roles()->sync($data['role_ids']);   // 支持 tenant_id pivot
}

// ✅ 逻辑删除（is_deleted 标记）
SysUser::query()->whereIn('id', $ids)->update(['is_deleted' => Base::HAVE_DELETED]);

// ✅ 软删除 trait（IsDeletedSoftDeletes）自动过滤已删除
```
