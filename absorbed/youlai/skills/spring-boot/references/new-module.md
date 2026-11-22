# 资源开发

新增资源前核对项目契约，再检查同域模块和生成模板。以下以精简公告资源说明结构，示例省略 imports；字段与权限仍须依据实际需求。

## 最小结构

```text
system/
├── controller/NoticeController.java
├── converter/NoticeConverter.java
├── mapper/NoticeMapper.java
├── model/
│   ├── entity/Notice.java
│   ├── form/NoticeForm.java
│   ├── query/NoticeQuery.java
│   └── vo/NoticePageVO.java
└── service/
    ├── NoticeService.java
    └── impl/NoticeServiceImpl.java
```

只创建本次用到的类。简单资源不拆独立模块；配置归属、模型分类和依赖方向沿用项目契约。

## 写入与查询模型

新增、修改约束相同时共用表单：

```java
/**
 * 公告表单。
 */
@Data
@Schema(description = "公告表单")
public class NoticeForm {

    @Schema(description = "公告标题")
    @NotBlank(message = "公告标题不能为空")
    @Size(max = 50, message = "公告标题不能超过50个字符")
    private String title;
}

/**
 * 公告查询条件。
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class NoticeQuery extends BaseQuery {

    @Schema(description = "标题关键字")
    private String keywords;
}
```

Form 不需要重复路径 ID；已有回填 ID 时由 Service 忽略。排序只有实际支持时才增加 `sort` 字段和白名单。

## 转换与业务契约

Mapper 继承 `BaseMapper<Notice>`。简单读写用 Entity 与 MapStruct；复杂联表可直接投影 `NoticePageVO`。

```java
/**
 * 转换公告表单。
 */
@Mapper(componentModel = "spring")
public interface NoticeConverter {

    /**
     * 创建公告实体，忽略客户端标识。
     */
    @Mapping(target = "id", ignore = true)
    Notice toEntity(NoticeForm form);

    /**
     * 更新可编辑字段，保留实体标识。
     */
    @Mapping(target = "id", ignore = true)
    void updateEntity(NoticeForm form, @MappingTarget Notice entity);
}

/**
 * 管理公告。
 */
public interface NoticeService {

    /**
     * 分页查询公告。
     */
    IPage<NoticePageVO> getNoticePage(NoticeQuery query);

    /**
     * 创建公告并返回记录 ID。
     */
    Long createNotice(NoticeForm form);

    /**
     * 修改指定公告，不存在时失败。
     */
    void updateNotice(Long noticeId, NoticeForm form);
}
```

实现类创建时调用 `insert`；修改时加载并检查目标，再更新可编辑字段，不能用 `saveOrUpdate` 混淆新增与修改。还应忽略实际 Entity 中由服务器维护的审计、租户等字段。多表一致写入才增加对应事务边界。

## HTTP 接口

```java
/**
 * 公告管理接口。
 */
@Tag(name = "公告管理")
@RestController
@RequestMapping("/api/v1/notices")
@RequiredArgsConstructor
public class NoticeController {

    private final NoticeService noticeService;

    /**
     * 分页查询公告。
     */
    @Operation(summary = "公告分页列表")
    @GetMapping
    @PreAuthorize("@ss.hasPerm('sys:notice:list')")
    public PageResult<NoticePageVO> getNoticePage(@Valid NoticeQuery query) {
        return PageResult.success(noticeService.getNoticePage(query));
    }

    /**
     * 创建公告。
     */
    @Operation(summary = "新增公告")
    @PostMapping
    @PreAuthorize("@ss.hasPerm('sys:notice:create')")
    @Log(module = LogModuleEnum.NOTICE, value = ActionTypeEnum.INSERT)
    public Result<Long> createNotice(@Valid @RequestBody NoticeForm form) {
        return Result.success(noticeService.createNotice(form));
    }

    /**
     * 修改指定公告。
     */
    @Operation(summary = "修改公告")
    @PutMapping("/{noticeId}")
    @PreAuthorize("@ss.hasPerm('sys:notice:update')")
    @Log(module = LogModuleEnum.NOTICE, value = ActionTypeEnum.UPDATE)
    public Result<Void> updateNotice(
            @PathVariable @Positive Long noticeId,
            @Valid @RequestBody NoticeForm form
    ) {
        noticeService.updateNotice(noticeId, form);
        return Result.success();
    }
}
```

示例采用 MVC 内建方法校验，不添加类级 `@Validated`。真实接口如沿用 AOP 校验，应确认相应异常处理链。

## 验证重点

- 对新增、更新核对字段校验、权限和不存在的资源；路径 ID 与请求体冲突时不能改写其他记录。
- 根据功能覆盖排序白名单、分页边界、唯一约束、父子归属和事务回滚。
- 生成器变更需验证生成结果能编译，不能只校验模板文件文本。
- 外部环境测试使用隔离数据；不要为普通单元测试依赖开发数据库或认证中心。
