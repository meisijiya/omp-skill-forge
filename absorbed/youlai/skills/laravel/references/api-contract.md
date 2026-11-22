# 接口契约

修改路由、状态码、业务错误码与统一响应时读取。以当前仓库配置为准。

## 目录

- 路由与 API 规范
- HTTP 状态码与业务错误码
- 统一响应格式

---

## 路由与 API 规范

### 路由文件与版本前缀

所有 API 定义在 `routes/api.php`，统一加 `v1` 前缀、命名空间 `App\Http\Controllers\V1`：

```php
// routes/api.php
Route::prefix('v1')->namespace('App\Http\Controllers\V1')->group(function () {
    // 公开
    Route::prefix('auth')->group(function () {
        Route::post('login', [AuthController::class, 'login']);
        Route::get('captcha', [AuthController::class, 'captcha']);
    });

    // 需要 JWT 认证
    Route::middleware(['jwt.admin'])->group(function () {
        Route::prefix('users')->group(function () {
            Route::get('me', [SysUserController::class, 'me']);
            Route::put('{id}/password/reset', [SysUserController::class, 'restPassword'])
                ->where(['id' => '[0-9]+']);
            Route::get('options', [SysUserController::class, 'options']);
            Route::get('{id}/form', [SysUserController::class, 'show'])
                ->where(['id' => '[0-9]+']);
            apiIdResource(SysUserController::class);
        });
    });
});
```

| 模块 | 前缀 | 说明 |
| --- | --- | --- |
| 认证 | `/api/v1/auth` | login / register / captcha / refresh-token |
| 用户 | `/api/v1/users` | 用户管理 |
| 角色 | `/api/v1/roles` | 角色管理 |
| 菜单 | `/api/v1/menus` | 菜单管理 |
| 部门 | `/api/v1/depts` | 部门管理 |
| 字典 | `/api/v1/dicts`、`/api/v1/dicts/{name}/items` | 字典与字典项 |
| 配置 | `/api/v1/configs` | 系统配置 |
| 通知 | `/api/v1/notices` | 通知公告 |
| 日志 | `/api/v1/logs` | 操作日志 |
| 文件 | `/api/v1/files` | 文件上传/删除 |
| 代码生成 | `/api/v1/codegen` | 代码生成 |
| 租户 | `/api/v1/tenants`、`/api/v1/tenant-plans` | 多租户 |

### 标准 CRUD 路径

| 操作 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 分页列表 | `GET` | `/api/v1/users` | Query：`pageNum`/`pageSize`/`keywords`/... |
| 表单数据 | `GET` | `/api/v1/users/{id}/form` | 路径参数 `id` |
| 新增 | `POST` | `/api/v1/users` | Body：snake_case 字段 |
| 更新 | `PUT` | `/api/v1/users/{id}` | Body：snake_case 字段 |
| 批量删除 | `DELETE` | `/api/v1/users/{ids}` | `ids` 逗号分隔 |
| 重置密码 | `PUT` | `/api/v1/users/{id}/password/reset` | |
| 分配角色 | `POST` / `PUT` | `/api/v1/users/{id}/roles` | |
| 下拉选项 | `GET` | `/api/v1/roles/options` | 返回 `[{value, label}]` |
| 当前用户 | `GET` | `/api/v1/users/me` | 当前登录用户信息 |
| 菜单路由 | `GET` | `/api/v1/menus/routes` | 动态路由树 |

### 路由注册顺序（重要！）

**固定路径端点必须注册在路径参数端点之前**，否则 Laravel 会优先匹配 `{id}/form` 等泛化路由：

```php
Route::prefix('users')->group(function () {
    Route::get('me', [SysUserController::class, 'me']);                 // 固定 —— 在前
    Route::get('options', [SysUserController::class, 'options']);       // 固定 —— 在前
    Route::get('export', [SysUserController::class, 'export']);         // 固定 —— 在前
    Route::get('{id}/form', [SysUserController::class, 'show'])         // 路径参数
        ->where(['id' => '[0-9]+']);
    apiIdResource(SysUserController::class);                            // index/store/show/update/destroy
});
```

> `apiIdResource()` 是项目封装助手：把标准 `apiResource` 的单参数 `id` 约束为数字，避免每个模块重复写 `->where()`。新增模块直接传控制器类名即可。

### 控制器方法模板

```php
<?php
namespace App\Http\Controllers\V1;

use App\Common\Enums\ResultCode;
use App\Exceptions\BusinessException;
use App\Http\Controllers\Controller;
use App\Http\Validates\SysUserValidate;
use App\Models\SysUser;
use App\Services\SysUserService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SysUserController extends Controller
{
    protected string $validatorClass = SysUserValidate::class;   // 绑定验证器

    public function __construct(
        protected SysUserService $userService,
    ) {}

    /**
     * 用户分页列表
     */
    public function index(Request $request): JsonResponse
    {
        $filters  = $request->only(['keywords', 'status', 'created_at', 'dept_id']);
        $pageSize = (int) $request->input('pageSize', self::PER_PAGE);
        $result   = $this->userService->paginate($filters, $pageSize);

        return $this->success($result);
    }

    /**
     * 创建用户
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $this->validateScene($request, 'create');   // 调用 SysUserValidate::rules('create')
        $data = $this->userService->create($validated);
        return $this->success($this->userService->format($data), '创建成功');
    }
}
```

## HTTP 状态码与业务错误码

### 设计理念

对齐 参考实现：**HTTP 状态码恒为 200**，业务状态码通过 body 的 `code` 字段传递。前端 axios 拦截器统一从 `response.data.code` 读取业务码。

### 业务错误码（ResultCode 枚举）

枚举定义在 `app/Common/Enums/ResultCode.php`，实现 `IResultCode` 接口，提供 `getCode()` / `getMsg()`：

| 错误码 | 枚举 | 含义 |
| --- | --- | --- |
| `00000` | `SUCCESS` | 成功 |
| `A0201` | `ACCOUNT_NOT_FOUND` | 用户账户不存在 |
| `A0202` | `ACCOUNT_FROZEN` | 用户账户被冻结 |
| `A0205` | `USER_TOKEN_INVALID` | 无效的 Token |
| `A0206` | `USER_TOKEN_EXPIRED` | Token 过期 |
| `A0210` | `USER_PASSWORD_ERROR` | 用户密码错误 |
| `A0211` | `DELETE_SUPER_ADMIN` | 不允许删除超级管理员 |
| `A0212` | `CANNOT_DELETE_SELF` | 不能删除当前登录账号 |
| `A0301` | `ACCESS_UNAUTHORIZED` | 访问未授权 |
| `A0400` | `USER_REQUEST_PARAMETER_ERROR` | 用户请求参数错误 |
| `B0001` | `SYSTEM_ERROR` | 系统执行出错 |
| `C0300` | `DATABASE_SERVICE_ERROR` | 数据库服务出错 |

首位编码规则：
- `0` 成功（`00000`）
- `A` 用户端错误（认证/权限/参数）
- `B` 系统端错误
- `C` 第三方/数据库错误

### 业务异常抛出

```php
use App\Common\Enums\ResultCode;
use App\Exceptions\BusinessException;

// ✅ 参数校验失败（控制器里由 validateScene 自动抛出，无需手写）
throw new BusinessException(ResultCode::USER_REQUEST_PARAMETER_ERROR->getCode(), $validator->errors()->first());

// ✅ 数据不存在
throw new BusinessException(ResultCode::ACCOUNT_NOT_FOUND->getMsg());

// ✅ 权限不足
throw new BusinessException(ResultCode::ACCESS_UNAUTHORIZED->getMsg());

// ✅ 不能删除自己
throw new BusinessException(ResultCode::CANNOT_DELETE_SELF->getMsg());
```

`BusinessException` 由 `bootstrap/app.php` 的异常处理器或全局异常渲染为统一响应（HTTP 200 + `code`/`msg`/`data`）。

## 统一响应格式

### Result 结构

```json
{
    "code": "00000",
    "msg": "操作成功",
    "data": { "…" },
    "traceId": "uuid-…"
}
```

响应由 `App\Traits\ApiResponse` 提供，所有控制器基类 `Controller` 已 `use ApiResponse`：

```php
// 成功（data 可空，自动 snake_case → camelCase）
return $this->success($data, '操作成功');

// 失败（不推荐直接用，优先用业务异常）
return $this->fail('操作失败', 'B0001');

// 业务错误（推荐，传枚举）
return $this->error(ResultCode::ACCESS_UNAUTHORIZED);

// 参数验证失败
return $this->validationError($errors, '参数验证失败');
```

### 分页响应

Eloquent 分页器（`LengthAwarePaginator`）直接作为 `data` 返回，经 `CaseConversion` 自动转为：

```json
{
    "code": "00000",
    "msg": "操作成功",
    "data": {
        "list": [ "…" ],
        "total": 100,
        "pageNum": 1,
        "pageSize": 10
    }
}
```

> **前端约定**：分页参数命名为 `pageNum` / `pageSize`（camelCase）。Laravel 端读取 `$request->input('pageSize')` 传给 `paginate()`，响应中由转换 Trait 输出驼峰键。

### 驼峰自动转换

`ApiResponse` 通过 `CaseConversion` trait 的 `convertToCamelCase()` 在输出时把数组键 / 对象属性从 snake_case 转为 camelCase。因此：

- Model 属性、`$request->input()` 用 snake_case（`dept_id`、`create_time`）
- 返回的 `data` 自动变 camelCase（`deptId`、`createTime`）
- 不需要手动在 Service 里 `toCamelCase`，但 `format()` 等手工组装数组时请直接用 camelCase 键名
