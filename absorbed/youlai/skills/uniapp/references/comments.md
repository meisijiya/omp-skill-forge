# 注释

默认使用简洁中文，技术标识保留原文。以下多行格式及适用范围是本项目约定。

## 形式

| 成员                                                   | 形式                                 |
| ------------------------------------------------------ | ------------------------------------ |
| 业务函数、API 方法、Store action、组合函数及其私有方法 | 多行 JSDoc                           |
| 类、类型、接口、枚举，包括内部声明                     | 多行 JSDoc                           |
| props、interface/type 字段、枚举成员                   | 简短时可用单行 JSDoc，多个约束时展开 |
| ref、computed、局部变量、实现原因                      | `//`；自解释的可省略                 |
| 生命周期、watch 和请求选项里的匿名回调                 | 不单独添加方法文档                   |

业务方法无论是否导出，都用 `/**`、正文、`*/` 分别占行的形式。不能因为函数私有或名称清楚就改成单行 JSDoc。

```ts
/**
 * 发送验证码并启动重发倒计时。
 */
async function sendCode() {
  await SmsAPI.sendCode(mobile.value);
  countdown.start();
}

/**
 * 短信登录凭证。
 */
interface SmsLoginParams {
  /** 接收登录验证码的手机号 */
  mobile: string;
}

// 微信端在页面布局完成后再测量胶囊位置。
onReady(measureNavigationBar);
```

## 内容

- 每个业务方法用一句话说明具体动作；先改善命名，不靠长注释弥补职责不清。
- 有真实的单位、前置条件、副作用或失败行为时再补一句，不抄写实现步骤。
- `@param`、`@returns`、`@throws` 只补充类型未表达的信息。
- 平台差异写清目标平台及实际原因；不写没有验证过的兼容性结论。
- 事务、并发、计时器和迟到回调的必要约束用相邻的短行注释。
- 长流程、使用示例、兼容决策放 `docs`。
- 文件头只说明无法从文件名看出的职责或共用关系，不重复「用户类型定义」「工具函数」；保留许可证。
- 示例按需标记「查询条件」「表单配置」「自定义插槽」，不逐行翻译模板。
- 删除过期注释、装饰分隔线和注释掉的旧代码，不维护逐文件变更流水。
- TODO / FIXME 必须描述可执行的事项；能直接修复的不要留下标记。

Store 的 ref/computed 变量需要解释时用行注释；动作方法仍使用多行文档。类型字段说明按复杂度选择单行或多行，不重复类型名称。

## 条件编译

`#ifdef/#ifndef/#endif` 是编译指令，不能当作无用注释删除。脚本使用行注释，模板使用 HTML 注释，样式使用块注释；保持标识和配对完整。

参考：[uni-app 条件编译](https://uniapp.dcloud.net.cn/tutorial/platform.html#preprocessor)、[TSDoc @param](https://tsdoc.org/pages/tags/param/)、[Google TypeScript 注释说明](https://google.github.io/styleguide/tsguide.html#make-comments-that-actually-add-information)。方法一律展开多行属于项目约定。
