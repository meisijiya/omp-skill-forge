# 认证与权限

修改登录、会话、Spring Security 或权限时读取。本文件描述 参考实现 当前实现，配置以 `SecurityProperties` 为准。

## 职责与依赖

```text
framework/security/
  token/       AccessTokenCodec、JwtAccessTokenCodec、OpaqueAccessTokenCodec
  session/     SessionService、RedisSessionStore、SessionValidator
  port/        UserAuthenticationPort、PermissionPort
  model/       SecurityUser、SecurityUserDetails、TokenPair

auth/
  password/    密码登录
  sms/         短信登录
  wxma/        微信小程序登录
  qrcode/      扫码登录
  oidc/        统一认证
  session/     刷新与退出的 HTTP 接口

system/adapter/security/   业务身份与权限查询
config/SecurityConfig     安全过滤器链装配
support/realtime/         实时连接，复用会话校验
```

- `framework.security` 定义契约，不依赖 `auth`、`system` 或 `support` 的实现。
- 各登录方式验证身份后交给 `SessionService` 创建会话，不各自实现刷新与撤销。
- `AccessTokenCodec` 只处理访问令牌格式；账号状态、权限和登录来源由会话服务处理。
- `SessionValidator` 按登录来源检查认证配置，不让基础安全包依赖 OIDC 实现。
- 沿用现有分包；一次直接调用能表达的用例，不额外增加 Facade、Command 或事件层。

## 双模式配置

```yaml
security:
  token:
    type: jwt # jwt 或 redis-token，二选一
    access-token-time-to-live: 2h
    refresh-token-time-to-live: 7d
    allow-multi-login: true
    jwt:
      secret-key: ${JWT_SECRET_KEY}
  permit-all-urls:
    - /api/v1/auth/login
    - /api/v1/auth/refresh-token
```

- JWT 与随机令牌策略按配置互斥加载。`redis-token` 不要求配置 JWT 密钥。
- `redis-token` 是不透明随机令牌，客户端不能从中读取身份；服务端凭摘要查询 Redis。
- 两种模式都使用 Redis 会话，提供退出撤销、权限更新及刷新轮换。JWT 模式不等于无状态登录。
- OIDC 是外部身份认证方式，不决定本地访问令牌格式，两种模式均可使用。
- 刷新凭证使用独立随机值；只存摘要，每次成功刷新后轮换，绝对会话期限不延长。
- 演示配置与演示 SQL 可以保留。生产密钥由部署配置提供，不在日志中输出凭证。

## 必须保留的行为

1. 刷新时重新检查账号与权限，不能只换一份相同身份的令牌。
2. 注销撤销当前会话；账号、角色或身份关联变更影响身份、状态或授权快照时，按现有契约撤销相关会话。仅修改角色展示名称不要求重新登录。
3. 数据库事务成功后才发布或撤销会话，回滚不产生有效凭证或误踢用户。
4. 刷新轮换及一次性票据消费必须原子执行，不能改成分离的 GET/DELETE。
5. 外部登录来源关闭、配置改变或缺少对应校验器时拒绝认证。
6. 凭证无效返回 401，权限不足返回 403，存储暂不可用与认证失败分别处理。

SQL 与 Redis 之间没有分布式事务。修改跨存储行为时说明实际保证，不把提交后回调描述为强一致事务。

## 匿名路径与权限

`permit-all-urls` 使用 `permitAll`，请求仍经过安全过滤器链。业务匿名接口不使用 `web.ignoring()`。

```java
@PreAuthorize("@ss.hasPerm('sys:user:create')")
@PreAuthorize("@ss.hasPerm('sys:user:update')")
@PreAuthorize("@ss.hasPerm('sys:user:delete')")
```

- 权限沿用 `模块:资源:操作`，具体动作与同类模块一致，不混用 `edit/update`。
- Controller 检查入口权限；Service 检查资源归属、数据范围和状态转换。
- 不为减少按钮数量合并语义不同的权限，也不为尚未实现的功能预建权限。

## 外部身份关联

OIDC 身份随本地会话保存，不另建桥接会话，也不默认要求认证中心提供准入组。会话期限和撤销复用 `SessionService`；ID Token 仅在服务端用于发起登出。本项目未接收认证中心的登出通知，不能将本地来源校验描述为实时检查认证中心会话。

- `sys_user_identity` 只保存本地用户与外部账号的映射，不是认证中心用户目录。
- `provider` 是具体认证源的稳定配置标识；`providerAccountId` 保存来源方账号 ID，例如 OIDC `sub`、微信 OpenID 或 GitHub/Gitee 用户 ID。展示名不参与匹配。
- 同一 `provider` 不能在保留关联数据时更换 issuer 或 AppID；多个小程序分别配置 provider，不能假设 OpenID 跨 AppID 相同。
- OIDC 页面在选中的本地用户下设置 subject，issuer/provider 由后端配置取得；没有接入管理 API 时，不编造认证中心账号列表。
- 外部账号已关联其他用户时拒绝占用，不自动迁移。以数据库唯一约束和事务覆盖并发保存；相同关联重复保存不撤销会话。
- 登录来源与本地权限分离：外部账号确认身份，本地用户承载角色、部门和数据权限。关联变更与会话撤销需保持已实现的失败语义。

## 验证

修改认证链路时运行现有会话契约、HTTP 认证和架构依赖测试。涉及 Redis 原子脚本时，使用隔离 Redis 验证轮换、重复消费与竞争条件。涉及前端时核对成对凭证存储、续期合并、旧会话响应和登出清理。
