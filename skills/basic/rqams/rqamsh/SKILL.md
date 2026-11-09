---
name: rqamsh
description: 用 rqamsh（rqams-harness）查询和操作 AMS 业务数据时使用：产品与产品组、工作空间、流水与估值报告导入、头寸报表与估值报告、净值与收益指标、归因与持仓分析、模拟交易、风险监控、行情数据、周报、对账、托管与份额事件、资源权限与标签。文档由 agent 自行从公开仓库获取，本技能不预置缓存。
---

# rqamsh（rqams-harness）

AMS 业务数据的 Python API 与 CLI（仓库 `ricequant/rqams-harness`）：取 AMS 已算好的业务数据、执行受控写入。本技能只给发行包、调用形态与取文档方式的最小指引；能力边界、字段语义、业务口径与写入护栏以该仓库的 `README.md` 与 `docs/` 为准。Agent 负责主动建立连接，本机新用户默认通过网页填写 key；不索取账号密码或让用户把 key 发进对话。

## 一、安装与版本更新

发行包名 `rqams-harness`，Python 导入名与命令名都是 `rqamsh`，需 Python ≥3.10。取到仓库后（见「三、取文档」）在仓库根目录就地安装：

```console
python -m pip install -e .
rqamsh --help
rqamsh schema
```

`schema` 与 `--help` 离线可用，只验证安装，不代表已连接。用户让 Agent 安装或开始使用时，检查后继续下节的首次连接，不停在“安装成功”。终端找不到 `rqamsh` 时先激活安装环境，或改用 `python -m rqamsh`。更新包：editable 安装先拉取仓库最新代码再重跑 `python -m pip install -e .`，从包索引安装用 `python -m pip install --upgrade rqams-harness`；更新后跑 `rqamsh schema` 确认操作。当前文档从 `dev` 分支获取；版本级变化见仓库 `CHANGELOG.md`，当前契约以 `rqamsh schema` 为准。

## 二、认证与调用

**需要连接且本机缺身份时：Agent 主动执行相关 CLI 只读命令，缺 key 默认打开网页。** 已有身份直接复用，不因新会话重复登录；概念咨询不触发登录。没有身份时提示用户在页面填写 key，并保持命令运行，登录后继续原任务。用户要求接入但尚无具体查询时可执行 `rqamsh workspaces list`；也可先执行 `rqamsh auth`。缺少 `RQAMSH_TOKEN` / `RQAMSH_BASE_URL` 不构成阻塞，不先索要地址、空间 ID 或管理员注入 token。仅明确远程、容器、无图形或无人值守环境才设 `RQAMSH_AUTO_LOGIN=0` 并用受限文件或环境变量注入；Agent 工具、捕获输出、非 TTY 不等于没有浏览器。按需接入与等待规则见[接入与已有上下文](https://github.com/ricequant/rqams-harness/blob/dev/docs/demo/README.md#使用方式用户说业务agent-读文档)。登录设置含明文 key，不读取回显、不写进对话或日志。

```console
rqamsh products list
rqamsh --base-url <私有地址> products list
rqamsh --token @agentkey products list
```

未指定地址时优先沿用已保存部署，没有保存地址才连接官方 `https://www.ricequant.com`；首次连接私有部署或切换部署时明确目标地址，显式新令牌不会自动切换地址。CLI 与 Python 的完整地址优先级见 [建立连接](https://github.com/ricequant/rqams-harness/blob/dev/docs/connection.md#建立连接)。CLI 连接参数必须位于子命令之前。

令牌优先级：显式 `--token` / `RQAMSH_TOKEN` > 设置文件。`--token @文件` 从 UTF-8 文件读取，适合自动化；`--token <字面值>` 会进入 shell 历史、进程命令行和可能的日志，只适合临时调试。

一个令牌关联用户，用户可以是多个工作空间的成员。`rqamsh workspaces list` 读取自己的成员空间：记录以 `id` 唯一，另有 `name`、`admin`、`capacity`、`users`、`ctime`、`tags`、`description`，读取前不需要先选空间；成员身份不等于 AMS 权益或资源权限。未指定空间时，复用同部署保存身份沿用最后空间，否则使用成员列表首项（服务端原序首项，不排序、不按名称或 ID 取最小、不按 AMS 权益筛选）；没有任何成员空间则报错，首项缺权益由服务端拒绝，不自动换下一个，也不要换令牌试探。要读别的分区用 `rqamsh workspaces use --workspace <成员 ID>` 或 `--workspace-id`；`workspaces.use` 先核验成员关系，失败不改变当前空间、缓存与设置，仅复用保存身份时写回（自动选中的首项也会写回），注入令牌不继承也不改写保存的空间。`client.use_workspace()` 只改变请求路由，不增加授权，也不代表切换成功。字段、默认选择与写回见 `docs/workspaces.md#默认工作空间与切换`，认证与设置规则见 `docs/connection.md#token-auth`，切换规则见 `docs/workspaces.md#use`。

Python 的 `rqamsh.init()` / `Client` 不自动弹出登录页；本机首次先用 CLI 完成登录，之后 `rqamsh.init()` 省略 `token` 复用设置，再调用 `rqamsh.<块>.<操作>(...)`。已有安全注入身份时可显式传入；`RQAMSH_TOKEN` 只由 CLI 自动解析，Python 须自行读取并传参，不打印凭据。参数一律显式写成 `参数名=值`，CLI 用同名 `--参数名`。并行多个身份时各自持有显式 `Client`，不共享模块默认实例。

多步查询优先用一个 Python 进程完成，不要为每一步启动一次 CLI：同一 `Client` 会复用资源索引，先解析一次目标资源并记下 ID，后续调用直接传 ID。`products.list` / `resource_catalog()` 会核验整个空间，单资源解析只核验命中项；不要为了拿一个产品 ID 先列全量再逐项读。多个独立只读优先使用接口的数组形态，否则按[连接说明](https://github.com/ricequant/rqams-harness/blob/dev/docs/connection.md#单字符串资源选择器)组织有限并发；并发建议只在该页维护。单产品综合分析的指标选择、共享取数与昨日比较见[学习案例](https://github.com/ricequant/rqams-harness/blob/dev/docs/demo/product-briefing/README.md)，不以直接运行示例脚本代替任务推理。

## 三、取文档

文档仓库（公开）：[ricequant/rqams-harness](https://github.com/ricequant/rqams-harness)，当前契约文档入口 [docs/index.md](https://github.com/ricequant/rqams-harness/blob/dev/docs/index.md)。两种取法内容等价，按环境择一：

- 克隆后本地检索（可跨页 grep）：`git clone --branch dev --depth 1 https://github.com/ricequant/rqams-harness.git`。
- 按页读原文（无需克隆，适合克隆受限的网络）：`https://raw.githubusercontent.com/ricequant/rqams-harness/dev/<path>`（`<path>` 是仓库内相对路径，如 `docs/balances.md`），读工具可按行区间分段取用，不必整页加载。
- 文档随仓库更新、没有自动推送：每次任务开始时重新获取 `dev` 文档；已有副本核对分支后 `git pull --ff-only`，不要继续读旧副本；`raw` 按上述分支获取。

先加载关键判断，再按需读取操作与字段；不把全文阅读当成开工前置。同一会话已读且文档未变时复用对应规则：

|可观察的任务阶段|执行前必读|带入下一步的判断|
|---|---|---|
|用户只问概念或能力，没有请求自己的数据或连接|对应业务页的概念说明；对象不明确时查 `docs/demo/README.md` 的「对象与动作边界」|直接用业务语言解释；不调用业务接口、不触发登录、不索取凭据|
|需要建立连接或业务目标尚未拆清，且没有可复用的上下文|`docs/demo/README.md` 的「接入与已有上下文」「目标拆解」|按实际需要补齐连接与目标；本机缺身份默认网页登录并继续原任务；已有身份及目标充分时直接推进，不按会话次数重走流程、不重复问角色|
|请求估值/净值更新、实时数据、批量汇总或分析结果|`docs/demo/README.md#task-readiness`；首次遇估值依赖时读 `docs/index.md#valuation-lifecycle`|明确本任务需要哪些产物、日期和覆盖范围；接口成功与计算状态不代替结果验收|
|结果缺项、字段缺失、任务运行中、失败或等待超时|`docs/connection.md#unready-inputs` 及「等待任务与判断完成」|按实际状态等待、诊断或报告阻塞；维护整体截止时间，保留已有结果，不换日期、不把小计说成全量|
|准备创建、修改、上传、删除、重算或持久化分析|`docs/demo/README.md#6-写操作计划卡` 与 `docs/index.md` 的「必要边界」；目标业务页的写入/覆盖/失败规则|只读查重直接执行；明确产品创建指令与公开默认足够时复用已有授权，不逐项询问数据源、账户或再次创建授权；真正需要确认时先展示完整创建信息再一次确认，最后读回；其他写操作仍按原授权边界执行|
|准备交付业务答案|`docs/demo/README.md#7-结果翻译` 及本次用到的权威字段/指标行|按对象时间、核验结论、解释依据、完整性与下一步组织；事实和推断分开，勾稽通过仅证明已核验关系，不证明全部输入齐全|

用当前 `rqamsh schema`（或 `rqamsh <块> <操作> --help`）确认操作与参数；返回结构查对应业务页。只读命中的操作区间，有子页先看入口的页面划分；涉及收益、净值、比例、风险、暴露时必须核对权威字段/指标行。对象或动作有歧义时查 `docs/demo/README.md` 的共用判断；具体问题拆解和能力组织按需看对应案例，不以运行案例脚本代替判断。连接或空间异常时读 `connection.md` / `workspaces.md`，不从字段名、操作名或模型常识反推业务口径。

`README.md` 只用于安装、认证与项目边界；不要因为它在入口就整页读。

单产品多维度简报按「一次快照 + 必要计算」组织，避免同一数据重复取：`balances.get` 已含净值、收益、仓位、行业与逐持仓盈亏；行业权重和前十集中度可直接由 `positions[].industry` / `market_value` 汇总，只有需要服务端分类体系或层级时才调 `analytics.asset_weight`。当前风格用 `analytics.realtime_factor_exposure`；历史风格才提交业绩归因。风险指标用 `analytics.indicators`，不要用风险归因代替常规风险摘要。收益必须取 `daily_returns`；`unit_net_value` 是单位净值，其环比不是收益率，不能用它代替。

## 四、检索

需要学习跨业务处理时，先查 [核心学习案例](https://github.com/ricequant/rqams-harness/blob/dev/docs/demo/README.md)，读取对应案例的观察、判断依据、分支、授权、复查和停止条件；教学构造材料不是实际部署回执，可选脚本也不覆盖整棵诊断决策树。API 参数、字段与公式仍回到 `docs/` 和当前 schema，不把样例数字或时点当默认值；其他业务按对应业务页说明执行，不把缺少案例解释为缺少 API。案例、脚本及必要材料统一位于 `docs/demo/`，获取完整 `docs/` 才能保留树内相对链接，复制单页不会带上引用文件。

- `docs/*.md` 的行尾由取文档方式决定：Windows 上 `git clone`（`core.autocrlf=true`）得到 CRLF，Linux 与 raw 单页是 LF。因此 `grep` 模式统一不要带 `$` 锚，写 `^## get`，不要写 `^## get$`。
- 操作标题有两级粒度：多数操作有独立的 `## <方法名>` 小节，少数族级小节把若干操作写在正文里。本地副本固定三步：`grep -n "^## " docs/<块>.md` 看结构 → `grep -rn "<块>\.<操作>" docs` 取页与行号（`-r` 是为了带上子页） → 只读该行号附近的区间。只读 raw 时没有跨页 grep，改用 `docs/index.md` 的导航加页内 `## ` 小节定位，需要跨页找操作名时再克隆。
- 一个业务块可能不止一页：`analytics` 块是块入口页 `docs/analytics/index.md`（块总述、跨族场景表、接口公共约定、四页导航）加 `docs/analytics/` 下的四个主题子页（`metrics`、`holdings_analysis`、`attribution`、`portfolio_analysis`）。查该块的操作先看入口页的「页面划分」，再只读命中的子页；子页不重复场景表与接口约定，需要时点回入口页。
- 单页可能很大（`docs/analytics/metrics.md` 470 行、`docs/fields/balances.md` 460 行），不要整页读，也不要一次读多页。
- 文档与本地安装版本不一致时，以 `rqamsh schema` 的运行时输出为准。

## 五、`rqamsh` 未覆盖时

`rqams-cli/` 与 `rqamsc-python/` 是既往路径，作为过渡保留：只有 `rqamsh` 确实没有对应操作、或用户明确要求使用 `rqamsc` CLI 时，才按 `../SKILL.md` 的路由规则走它们。
