---
name: forge-fastapi
description: 用于 FastAPI 后端的开发、审查与重构，涵盖异步 REST API、SQLAlchemy 2.0 异步 ORM、Pydantic v2 校验、JWT/Redis 令牌与权限控制。适用于新增接口、新增模块或调整数据访问层时；技术选型以仓库现状为准。
---

# FastAPI 后端开发

依据当前仓库的技术栈与既有契约完成后端开发、审查与重构。下列约定用于约束新增代码；仓库已有规则优先。

## 开始前

- 读取 `pyproject.toml`、锁文件、`app/main.py` 与相关业务域，确认实际依赖版本与分层方式。
- 查看 Git 状态，保留未提交改动，不顺手重构无关代码。
- 按任务从下表读取对应参考，不一次性加载全部文件。

## 按任务读取

| 任务 | 参考 |
| --- | --- |
| 技术栈与目录结构 | [项目布局](references/project-layout.md) |
| 文件、类型、方法与变量的命名 | [命名规范](references/naming.md) |
| 路由、状态码、业务错误码与统一响应 | [接口契约](references/api-contract.md) |
| 模型、ORM、认证鉴权与数据库操作 | [数据与认证](references/data-and-auth.md) |
| 新增业务模块的完整步骤 | [新增模块](references/new-module.md) |
| 注释、检查清单、反模式与部署 | [交付质量](references/quality.md) |

## 核心约定

- ORM 使用 SQLAlchemy 2.0 的 `Mapped` / `mapped_column` 异步写法，数据校验使用 Pydantic v2。
- 路由注册时固定路径必须排在 `/{id}` 等动态路径之前，避免路径被提前匹配。
- 成功响应统一包装为 `Result[T]`，异常保留正确的 HTTP 状态，业务码只用于补充语义。
- 数据库会话由依赖注入管理，事务边界在 service 层，不在 router 中手工提交。
- 权限标识沿用仓库既有命名，不在同一项目混用 `add/edit` 与 `create/update`。
- docstring 使用 Google 风格，解释业务约束与边界条件，不复述签名。

## 完成前

- 运行项目原生的格式化、静态检查与测试命令，如实报告失败与未覆盖项。
- 新增接口保持与现有响应结构、错误码和权限标识一致。
- 不通过放宽类型、跳过校验或删除断言掩盖失败。
- 说明修改内容、验证结果与剩余风险。
