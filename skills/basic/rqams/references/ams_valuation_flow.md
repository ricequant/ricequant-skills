# AMS 估值主链路定位

本页用于在三个执行路径之间定位业务层，不定义估值公式、输入采用条件或结果就绪规则。`rqamsh` 的业务权威是[估值主线](https://github.com/ricequant/rqams-harness/blob/dev/docs/index.md#valuation-lifecycle)、[任务完成条件](https://github.com/ricequant/rqams-harness/blob/dev/docs/demo/README.md#task-readiness)与[未就绪处理](https://github.com/ricequant/rqams-harness/blob/dev/docs/connection.md#unready-inputs)。不要用本页的层级定位替代这些规则。

## 按用户目标定位

|用户目标|业务层|下一步|
|---|---|---|
|确认产品、产品组、资产单元及空间边界|对象层|按 `rqamsh/SKILL.md` 读取学习案例入口的对象与动作边界；产品组不是成员业务数据的批量写入口，资产单元不是券商账户|
|导入或更正流水、估值表、持仓、托管/份额事件、公允价|输入层|先区分对象与输入来源，再读对应业务页的采用方式、覆盖范围和写后验收|
|确认估值进度、历史更正后的后续影响|计算层|先读估值主线；检查计算状态，再读回用户所需日期的结果|
|读取头寸、净值、收益、风险、归因|结果层|按目标选择历史或实时产物；核对日期、来源、完整性、基准与模板|
|核对差异、缺件、人工结论或采用估值表覆盖|核对层|先读 `reconciliation_workflow.md`，查差异与处理差异分开授权|
|下载材料、汇总或投递|交付层|取数由所选工具完成；加工与第三方对接由 Agent 组合，不以一次下载或接口成功替代用户任务验收|

## 输入不能只按名称判断

- 产品估值报告、产品持仓表与资产单元持仓单不是同一种输入。资产单元持仓单只做数量核对，不参与产品估值、不触发重算；其余输入是否采用及如何影响后续结果，以对应业务页为准。
- 托管/份额事件的日期、现金与份额影响，按对应业务页核对；托管事件的跨工具处理要求见 `custodian_event_workflow.md`。
- 自定义合约公允价与估值表内的 `fair_value` / `fair_value_setl_ccy` 不同，分别查自定义标的或估值报告页面；对账价格差异见 `reconciliation_workflow.md`。
- 模拟交易信号经撮合形成流水，不是真实交易执行。

## 选择执行路径

默认读 `../rqamsh/SKILL.md`，由运行时 schema 确认真实操作命名与参数。仅在 Harness 无对应能力或用户明确要求时，才转 `rqams-cli` / `rqamsc-python`，并读取该路径的技能、当前文档与 schema；不得把路径之间的字段和认证方式互相套用。
