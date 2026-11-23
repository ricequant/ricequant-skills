---
name: rqamsh
description: 用 rqamsh（rqams-harness）查询和操作 AMS 业务数据时使用：产品与产品组、工作空间、流水与估值报告导入、头寸、净值与收益、归因与持仓分析、模拟交易、风险监控、行情、周报、对账、托管与份额事件、权限与标签。
---

# rqamsh（rqams-harness）

AMS 业务数据的 Python API 与 CLI（仓库 `ricequant/rqams-harness`）：取 AMS 已算好的业务数据、执行受控写入。能力边界、字段语义、业务口径与写入护栏以当前 SDK 随附文档为准。Agent 负责主动建立连接，本机新用户默认通过网页填写 key；不索取账号密码或让用户把 key 发进对话。

## 一、安装与版本更新

发行包名 `rqams-harness`，Python 导入名与命令名都是 `rqamsh`，需 Python ≥3.10。使用已配置的包索引安装；无包索引时可从公开仓库源码安装。

```console
python -m pip install rqams-harness
python -m rqamsh docs --skill-dir "<此 SKILL.md 所在目录>"
```

已有 SDK 时先试 `python -m rqamsh docs`。如果没有 `docs` 命令，从已配置的索引升级 SDK。仅当索引已用同版本号替换发布包而普通升级不重装时，执行 `python -m pip install --no-cache-dir --force-reinstall --no-deps rqams-harness`，再运行同步命令。源码安装应选择已包含 `docs` 命令的修订，在仓库根目录用 `python -m pip install -e .` 替代第一行，不默认走仓库的默认分支。

安装或更新 Skill 或 SDK 后重跑同步命令。若 Skill 目录不可写，直接用 `rqamsh docs` 返回的随包路径；若同步反馈本地冲突，保留现有文件，改读随包路径。终端找不到 `rqamsh` 时激活安装环境，或用该环境的 `python -m rqamsh`。离线自检不代表已连接；用户要求实际接入时继续首次连接。

## 二、认证与调用

**需要连接且本机缺身份时：Agent 主动执行相关 CLI 只读命令，缺 key 默认打开网页。** 已有身份直接复用，不因新会话重复登录；概念咨询不触发登录。没有身份时提示用户在页面填写 key，并保持命令运行，登录后继续原任务。用户要求接入但尚无具体查询时可执行 `rqamsh workspaces list`；也可先执行 `rqamsh auth`。缺少 `RQAMSH_TOKEN` / `RQAMSH_BASE_URL` 不构成阻塞，不先索要地址、空间 ID 或管理员注入 token。仅明确远程、容器、无图形或无人值守环境才设 `RQAMSH_AUTO_LOGIN=0` 并用受限文件或环境变量注入；Agent 工具、捕获输出、非 TTY 不等于没有浏览器。按需接入与等待见随包文档 `demo/README.md#使用方式用户说业务agent-读文档`。登录设置含明文 key，不读取回显、不写进对话或日志。

```console
rqamsh products list
rqamsh --base-url <私有地址> products list
rqamsh --token @agentkey products list
```

未指定地址时优先沿用已保存部署，没有保存地址才连接官方 `https://www.ricequant.com`；首次连接私有部署或切换部署时明确目标地址，显式新令牌不会自动切换地址。完整地址优先级见 `connection.md#建立连接`。CLI 连接参数必须位于子命令之前。

令牌优先级：显式 `--token` / `RQAMSH_TOKEN` > 设置文件。`--token @文件` 从 UTF-8 文件读取，适合自动化；`--token <字面值>` 会进入 shell 历史、进程命令行和可能的日志，只适合临时调试。

一个令牌关联用户，用户可以是多个工作空间的成员。`rqamsh workspaces list` 读取自己的成员空间：记录以 `id` 唯一，另有 `name`、`admin`、`capacity`、`users`、`ctime`、`tags`、`description`，读取前不需要先选空间；成员身份不等于 AMS 权益或资源权限。未指定空间时，复用同部署保存身份沿用最后空间，否则使用成员列表首项（服务端原序首项，不排序、不按名称或 ID 取最小、不按 AMS 权益筛选）；没有任何成员空间则报错，首项缺权益由服务端拒绝，不自动换下一个，也不要换令牌试探。要读别的分区用 `rqamsh workspaces use --workspace <成员 ID>` 或 `--workspace-id`；`workspaces.use` 先核验成员关系，失败不改变当前空间、缓存与设置，仅复用保存身份时写回（自动选中的首项也会写回），注入令牌不继承也不改写保存的空间。`client.use_workspace()` 只改变请求路由，不增加授权，也不代表切换成功。字段、默认选择与写回见 `docs/workspaces.md#默认工作空间与切换`，认证与设置规则见 `docs/connection.md#token-auth`，切换规则见 `docs/workspaces.md#use`。

Python 的 `rqamsh.init()` / `Client` 不自动弹出登录页；本机首次先用 CLI 完成登录，之后 `rqamsh.init()` 省略 `token` 复用设置，再调用 `rqamsh.<块>.<操作>(...)`。已有安全注入身份时可显式传入；`RQAMSH_TOKEN` 只由 CLI 自动解析，Python 须自行读取并传参，不打印凭据。参数一律显式写成 `参数名=值`，CLI 用同名 `--参数名`。并行多个身份时各自持有显式 `Client`，不共享模块默认实例。

多步查询优先在一个 Python 进程复用 `Client` 和已解析的资源 ID，不为每步启动 CLI，也不为了找一个产品先逐项读全空间详情。多个独立只读优先用接口的数组形态，否则按 `connection.md#单字符串资源选择器` 组织有限并发。

## 三、取文档

运行 `rqamsh docs` 得到 `path` 和 `docs_sha256`。优先直接读 `path`；若宿主只能访问 Skill 目录，则按安装步骤同步，再读返回的 `sdk-docs/<docs_sha256>/` 路径。下文 `docs/` 代表选定的文档根目录。不全量加载、不在任务中拉取在线 `dev`。只有尚未安装 SDK、且只是了解概念时，可在线浏览[公开业务文档](https://github.com/ricequant/rqams-harness/blob/dev/docs/index.md)，不把开发分支当成已安装版本的契约。

|用户目标|直接入口|
|---|---|
|当前单产品综合简报，或要求当前与昨日比较|`docs/demo/product-briefing/README.md` 的「开始执行」「取数编排」：先取产品配置和当前快照，按实际日期和缺项决定后续读取。|
|明确日期的单产品头寸或净值|直接读 `docs/balances.md#get`，按请求业务日期读取，不额外查实时快照。|
|其他跨业务目标|`docs/demo/README.md` 的业务目标索引；没有匹配案例时用 `docs/index.md` 选业务块。|

先加载关键判断，再按需读取操作与字段；不把全文阅读当成开工前置。同一会话已读且文档未变时复用对应规则：

|可观察的任务阶段|执行前必读|带入下一步的判断|
|---|---|---|
|用户只问概念或能力，没有请求自己的数据或连接|对应业务页的概念说明；对象不明确时查 `docs/demo/README.md` 的「对象与动作边界」|直接用业务语言解释；不调用业务接口、不触发登录、不索取凭据|
|需要建立连接或业务目标尚未拆清，且没有可复用的上下文|`docs/demo/README.md` 的「接入与已有上下文」「目标拆解」|按实际需要补齐连接与目标；本机缺身份默认网页登录并继续原任务；已有身份及目标充分时直接推进，不按会话次数重走流程、不重复问角色|
|请求估值/净值更新、实时数据、批量汇总或分析结果|`docs/demo/README.md#task-readiness`；首次遇估值依赖时读 `docs/index.md#valuation-lifecycle`|明确本任务需要哪些产物、日期和覆盖范围；接口成功与计算状态不代替结果验收|
|结果缺项、字段缺失、任务运行中、失败或等待超时|`docs/connection.md#unready-inputs` 及「等待任务与判断完成」|按实际状态等待、诊断或报告阻塞；维护整体截止时间，保留已有结果，不换日期、不把小计说成全量|
|准备创建、修改、上传、删除、重算或持久化分析|`docs/demo/README.md#6-写操作计划卡` 与 `docs/index.md` 的「必要边界」；目标业务页的写入/覆盖/失败规则|只读查重直接执行；明确产品创建指令与公开默认足够时复用已有授权，不逐项询问数据源、账户或再次创建授权；真正需要确认时先展示完整创建信息再一次确认，最后读回；其他写操作仍按原授权边界执行|
|准备交付业务答案|`docs/demo/README.md#7-结果翻译` 及本次用到的权威字段/指标行|按对象时间、核验结论、解释依据、完整性与下一步组织；事实和推断分开，勾稽通过仅证明已核验关系，不证明全部输入齐全|

已定位操作时用 `rqamsh <块> <操作> --help` 核对参数；需要完整操作列表才运行 `rqamsh schema`。返回、日期、字段单位与业务含义只读本地文档命中的区间，不凭字段名推断。连接或空间异常时读 `connection.md` / `workspaces.md`。

## 四、检索

操作通常有 `## <操作名>`；同族合写时在所属业务块目录检索 `<块>.<操作>`，按命中的标题或行区间读。`analytics` 用 `docs/analytics/index.md` 的页面划分定位主题页。案例讲判断、分支和复查；不把示例数据当默认值，不以直接运行脚本代替当前任务的判断。

## 五、`rqamsh` 未覆盖时

`rqams-cli/` 与 `rqamsc-python/` 是既往路径，作为过渡保留：只有 `rqamsh` 确实没有对应操作、或用户明确要求使用 `rqamsc` CLI 时，才按 `../SKILL.md` 的路由规则走它们。
