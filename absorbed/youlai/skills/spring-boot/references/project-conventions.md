# 项目契约

修改 参考实现 的分包、模型、API 或校验时读取。命名与分层是本项目选择，不代表 Spring 强制要求。

## 分包

采用业务域分包、域内分层的单体结构。下列根包名 `com.example.app` 是占位写法，实际根包以目标仓库为准：

```text
com.example.app
├── common/       # 共享类型、常量和通用异常
├── framework/    # Web、Security、MyBatis 等基础设施
├── config/       # 跨域装配
├── support/      # file、mail、sms、realtime 等支撑能力
├── auth/         # password、sms、wxma、qrcode、oidc、session
├── system/       # 用户、角色、菜单、部门、字典
├── module/       # form、workflow 等业务域
└── codegen/      # 代码生成
```

- 新能力先放已有业务域，不为单个类建立顶级包。
- `common` 不依赖 `framework`、`config` 或业务域。`framework` 通过已有 Port 或回调获取业务能力；`config` 可作为组合根装配它们。
- 域私有装配和 `@ConfigurationProperties` 随消费模块放置，沿用已有 `config/`。跨域装配才进全局 `config/`；不为属性类另设没有收益的层级。
- 属性类沿用组件扫描、`@EnableConfigurationProperties` 或 `@ConfigurationPropertiesScan` 中的一种注册方式，避免重复 Bean。
- 跨域调用窄接口，不传递另一个域的 Entity；只在真实依赖需要时引入接口，不为直接调用增设 Facade 或事件。
- 已有 `IService` 不为形式全仓迁移；新增业务契约优先只暴露实际用例。调整依赖方向后运行现有架构测试。

## 对象分类与命名

| 对象   | 用途与命名                                                            |
| ------ | --------------------------------------------------------------------- |
| Entity | 持久化模型，沿用领域名和表映射；现有 `SysUser` 等不因审美要求单独迁移 |
| Form   | 业务写入与同形编辑回填，如 `UserForm`                                 |
| Query  | 筛选、分页和排序条件，如 `UserQuery`                                  |
| VO     | 对外响应或只读查询投影，如 `UserPageVO`                               |
| DTO    | 有明确传输用途的结构；在本项目主要用于内部传参和聚合结果              |

- `Form`、`Query` 在概念上也属于 DTO；分包只是细分用途。不改成整套 `Request / Response`，也不把 DTO 宣称为“只能内部使用”。
- 创建、更新字段与校验相同时共用 Form；确有差异才拆 `UserCreateForm`、`UserUpdateForm`。回填结构一致时可复用 Form，不复制同字段 VO。
- 查询统一用 `XxxQuery`，分页复用后端已有 `BaseQuery`。列表与导出可共用筛选；非分页条件不为统一继承基类。
- 新参数名用 `query`、`form`、`userId` 等明确名称；方法表达业务动作，避免 `data`、`params`、`process` 等无上下文名称。
- `TokenPair`、`LoginSession`、`RealtimeTicketResponse` 等协议或状态类型保留职责明确的名称，不叠加 DTO、VO、Response 后缀。只有应用事件放入 `event/`。
- 外部 Query 不接受当前用户、租户、权限范围等执行上下文，服务器自行取得。

## API 与数据契约

- 资源路径用复数名词，如 `/api/v1/users`；现有动作接口在修改时核对客户端，不为 REST 外观单独破坏契约。
- 更新以路径 ID 为唯一目标。共用 Form 即使携带回填 ID，Service 也不能据此切换目标；创建显式忽略该 ID。
- 嵌套资源同时核对父标识和子记录归属，不能只根据子 ID 更新或删除。
- Controller 返回 `Result<T>` 或 `PageResult<T>`，无数据为 `Result<Void>`。Service、Mapper 不返回 HTTP 包装。
- 分页可沿用 Service 的 `IPage<VO>`，由 Controller 调用 `PageResult.success(page)`；同一模块保持一致。
- 业务码沿用现有体系；HTTP 错误状态与统一异常处理一致，不能为某个接口另创一套。
- Java `Long` 标识在当前前端契约中按字符串处理；日期时间在 JSON 中为字符串。模型和示例以实际序列化结果为准。
- 权限沿用 `模块:资源:操作`。普通 CRUD 按 `list / create / update / delete / import / export` 等现有动作划分；身份设置等资源可以沿用已有 read/write。粒度按实际授权语义确定，不为少写配置一律合并。
- 写入的防重复与审计按实际风险使用已有机制，不能用防抖或 `@RepeatSubmit` 代替事务和数据库唯一约束。

## 分页与排序

```text
GET /api/v1/users?pageNum=1&pageSize=10&sort=createTime,desc&sort=id,desc
```

- `sort` 可重复传递，顺序表示优先级，表达式为 `属性名,asc|desc`。
- 这是与 Spring Data 相同形状的查询协议；MyBatis-Plus 不会因此自动获得 Spring Data 参数解析。
- 复用现有 `framework/mybatis/QuerySort`，把公开属性映射到服务器列白名单，拒绝未知字段、方向和过多排序项。不能把前端字符串直接拼到 SQL。
- 分页约束沿用 `BaseQuery` 和实际配置；不要在模板中写出另一组上限。稳定分页可增加 ID 作为末级排序。
- 排序不是展示列序号；字典、菜单等业务字段已有的 `sort` 含义不能混为查询表达式。

## 校验与一致性

- Body 使用 `@Valid`，Path/Query 标量声明正数、范围等约束；嵌套集合需检查元素约束和是否允许空集合。
- Spring MVC 6.1+ 可使用内建方法校验，处理 `MethodArgumentNotValidException` 和 `HandlerMethodValidationException`。类级 `@Validated` 会改走 AOP，不机械混用两条链路。
- 字符串非空用 `@NotBlank`；其他必填类型用 `@NotNull`。长度与字段类型、数据库约束一致，不给日期或数字生成 `@NotBlank`。
- 状态与类型码限制到允许值，新增、更新、状态变更和密码重置都需覆盖；不能只信任前端校验。
- 动态字段不能仅靠 `Map<String, Object>` 和 `@Valid`，需校验字段白名单、类型、长度及业务规则。
- 批量操作先明确全部失败或部分成功；多表写入、树路径和关联更新覆盖完整事务边界。
- 缓存和实时通知在事务成功后变更；提交后回调不能保证 Redis 可用或可靠投递。失败补偿仅在实际交付要求下设计。

相关机制见 [Spring MVC Validation](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html)。排序参数形状参考 [Spring Data Web](https://docs.spring.io/spring-data/commons/reference/repositories/core-extensions.html#core.web.basic)。
