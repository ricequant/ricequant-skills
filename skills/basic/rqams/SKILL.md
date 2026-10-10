---
name: rqams
description: 处理 RQAMS 数据查询和操作时使用。默认走 rqamsh（rqams-harness 的 Python API 与 CLI）；rqams-cli 与 rqamsc-python 是既往的 rqamsc CLI 与 Python SDK 路径，仅作过渡，只在 rqamsh 未覆盖目标操作或用户明确要求时使用。
---

# RQAMS

RQAMS 业务数据的默认入口是 `rqamsh`（`rqams-harness` 项目）；`rqams-cli` 与 `rqamsc-python` 是既往的 `rqamsc` CLI 与 Python SDK 路径，作为过渡保留。

## 一、默认路径：rqamsh

先读 `rqamsh/SKILL.md`——安装与自检、调用形态、文档从哪里取与怎么检索都在那里；连接参数的位置与会话注入、能力边界、字段语义以它指向的 [ricequant/rqams-harness](https://github.com/ricequant/rqams-harness) 仓库 `README.md` 与 `docs/` 为准。本文件不重复它的命令字段与返回结构。

## 二、业务链路判断（三个路径通用）

处理具体任务前，先按 `references/` 判断需求在 AMS 估值主链路中的位置（对象层、输入层、计算层、结果层）：

- `references/ams_valuation_flow.md`：估值主链路，用来判断问题或需求落在哪一层。
- `references/custodian_event_workflow.md`：托管事件的创建、更新、上传、删除、排查，或用户提到申购、赎回、分红、费用、现金与应收应付调整时。
- `references/reconciliation_workflow.md`：对账与各类差异排查，或需要判断是否使用自动对账时。

## 三、通用安全要求

- 写操作（创建、更新、删除、上传、重算）除非用户已给出精确指令，执行前必须明确目标资源和关键字段；只有用户明确授权后才执行。
- 对账、托管事件的写操作分别遵守 `references/reconciliation_workflow.md` 和 `references/custodian_event_workflow.md`：先只读诊断并向用户报告，确认后再执行。
- 凭据与会话不要写进回复、仓库文件、skill 文件或可长期保留的日志；临时文件用完删除。

## 四、过渡路径：rqams-cli 与 rqamsc-python

只在 `rqamsh` 没有目标操作、或用户明确要求时使用。安装、文档缓存、登录 profile 与环境自检都以子技能文件为准，使用前先读 `rqams-cli/SKILL.md` 或 `rqamsc-python/SKILL.md`；命令字段不要向 `rqamsh` 对齐，两条过渡路径之间也不要互相补齐。

## 五、字段来源

不要在本文件维护命令字段或 API schema：`rqamsh` 以 `rqamsh schema` 与 `rqams-harness` 仓库的 `docs/` 为准；`rqams-cli` 以 `rqamsc schema list` 与其缓存命令文档为准；`rqamsc-python` 以子技能初始化脚本生成的索引与 API 文档为准。
