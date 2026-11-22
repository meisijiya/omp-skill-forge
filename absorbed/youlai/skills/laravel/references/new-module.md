# 新增模块

修改新增业务模块的完整步骤时读取。以当前仓库配置为准。

## 目录

- 添加新模块 — 完整教程

---

## 添加新模块 — 完整教程

以添加 **"字典项"** 模块为例。

### Step 1: 创建 Model

```php
<?php
namespace App\Models;

use App\Traits\IsDeletedSoftDeletes;
use Illuminate\Database\Eloquent\Attributes\Fillable;

#[Fillable(['dict_code', 'value', 'label', 'tag_type', 'status', 'sort'])]
class SysDictItem extends Base
{
    protected $table = 'sys_dict_item';

    const string CREATED_AT = 'create_time';
    const string UPDATED_AT = 'update_time';
}
```

### Step 2: 创建 Validate

```php
<?php
namespace App\Http\Validates;

use Illuminate\Validation\Rule;

class SysDictItemValidate extends BaseValidate
{
    public function rules(string $scene = 'create', ?int $id = null): array
    {
        return match ($scene) {
            'create' => [
                'dict_code' => ['required', 'string', 'max:50'],
                'value'     => ['required', 'string', 'max:50'],
                'label'     => ['required', 'string', 'max:100'],
                'status'    => 'nullable|integer|in:0,1',
                'sort'      => 'nullable|integer',
            ],
            'update' => [
                'dict_code' => ['nullable', 'string', 'max:50'],
                'value'     => ['nullable', 'string', 'max:50'],
                'label'     => ['nullable', 'string', 'max:100'],
            ],
            default => [],
        };
    }

    public function messages(): array
    {
        return [
            'dict_code.required' => '字典编码不能为空',
            'value.required'     => '字典值不能为空',
            'label.required'     => '字典标签不能为空',
        ];
    }
}
```

### Step 3: 创建 Service

```php
<?php
namespace App\Services;

use App\Attributes\LogAction;
use App\Common\Enums\ActionType;
use App\Common\Enums\LogModule;
use App\Models\SysDictItem;

class SysDictItemService extends BaseService
{
    #[LogAction(module: LogModule::DICT, action: ActionType::QUERY)]
    protected function paginate(array $filters, int $perPage)
    {
        $query = SysDictItem::query()->where('is_deleted', 0);
        // … 筛选 + 分页
        return $query->paginate($perPage);
    }

    #[LogAction(module: LogModule::DICT, action: ActionType::CREATE)]
    protected function create(array $data): SysDictItem
    {
        return SysDictItem::query()->create($data);
    }

    protected function format(SysDictItem $item): array
    {
        return [
            'id'        => $item->id,
            'dictCode'  => $item->dict_code,
            'value'     => $item->value,
            'label'     => $item->label,
            'status'    => $item->status,
            'sort'      => $item->sort,
        ];
    }
}
```

### Step 4: 创建 Controller

```php
<?php
namespace App\Http\Controllers\V1;

use App\Http\Controllers\Controller;
use App\Http\Validates\SysDictItemValidate;
use App\Services\SysDictItemService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SysDictItemController extends Controller
{
    protected string $validatorClass = SysDictItemValidate::class;

    public function __construct(protected SysDictItemService $service) {}

    public function index(Request $request): JsonResponse
    {
        $filters  = $request->only(['dict_code', 'value']);
        $pageSize = (int) $request->input('pageSize', self::PER_PAGE);
        return $this->success($this->service->paginate($filters, $pageSize));
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $this->validateScene($request, 'create');
        return $this->success($this->service->format($this->service->create($validated)), '创建成功');
    }
}
```

### Step 5: 注册路由

```php
// routes/api.php（在 jwt.admin 分组内）
Route::prefix('dicts')->group(function () {
    Route::get('{id}/form', [SysDictItemController::class, 'show'])
        ->where(['id' => '[0-9]+']);
    apiIdResource(SysDictItemController::class);
    Route::prefix('{name}/items')->group(function () {
        Route::get('/', [SysDictItemController::class, 'items']);
        Route::get('options', [SysDictItemController::class, 'options']);
    });
});
```

### Step 6: 验证

```bash
php artisan serve          # 启动 HTTP
php artisan sse:start --auth=admin start   # 启动 SSE（如需）
# 访问 /api/v1/dicts 确认路由已注册
```
