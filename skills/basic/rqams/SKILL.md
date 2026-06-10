---
name: rqams
description: 处理 RQAMS 数据查询和操作时使用。标准产品、workspace、交易流水、估值表、持仓报表、模拟交易、对账、报表和分析任务优先路由到 rqams-cli；需要 Python SDK 脚本、多 API 组合处理、本地 Python 环境诊断或 CLI 未覆盖接口时路由到 rqamsc-python。
---

# RQAMS

此 skill 是 RQAMS 的统一入口，负责在两个执行路径之间选择：

- `rqams-cli/`：使用本地 `rqamsc` CLI 处理标准 RQAMS 操作。
- `rqamsc-python/`：使用 Python SDK 编写脚本、处理复杂工作流、诊断环境，或调用 CLI 尚未覆盖的接口。

处理具体 RQAMS 任务前，先按 `references/ams_valuation_flow.md` 理解用户需求在 AMS 估值主链路中的位置：对象层、输入层、计算层或结果层。确定业务位置后，再路由到 CLI 或 Python 路径。

涉及对账、reconciliation、估值表差异、持仓差异、净值差异、现金/应收应付差异或需要判断是否使用 `auto` 对账时，必须先阅读 `references/reconciliation_workflow.md`。该文档是工具无关的对账处理准则，适用于 `rqams-cli` 和 `rqamsc-python`。

## 路由规则

当用户要查询、创建、更新、删除、上传、下载、重算或汇总标准 RQAMS 资源时，优先使用 `rqams-cli`。标准资源包括 workspace、产品、产品组、交易流水、估值表、持仓报表、事件、自定义对象、模拟交易、对账、分析和报表。

当用户明确要求 Python 代码、需要可复用脚本或 notebook 式流程、需要组合多个 API 做自定义处理、需要检查本地 Python `rqamsc` 环境，或 CLI schema 未覆盖目标 API 时，使用 `rqamsc-python`。

如果两条路径都能完成任务，一次性操作使用 CLI，复杂数据处理使用 Python。

## CLI 路径

使用 CLI 路径前，先阅读 `rqams-cli/SKILL.md`。

以运行时 schema 作为命令契约：

```powershell
rqamsc schema list
rqamsc schema get --payload '{"command":"get product-list"}'
```

再按统一格式调用：

```powershell
rqamsc <verb> <resource> --payload <json|@file|->
```

## Python 路径

使用 Python 路径前，先阅读 `rqamsc-python/SKILL.md`。

按子 skill 说明使用 `rqamsc-python/scripts/` 中的脚本初始化或检查 Python 环境。

## 安全要求

对于创建、更新、删除、上传、重算等写操作，除非用户已经给出精确指令，否则执行前必须明确目标资源和关键 payload 字段。

对账写操作必须遵守 `references/reconciliation_workflow.md`：先只读诊断并向用户报告差异、拟写入/删除内容、影响范围和预期效果，用户确认后再执行。

不要在顶层文件重复维护命令字段或 API 对象 schema。CLI 运行时 schema、`rqams-cli/scripts/init_skill.py` 生成的 CLI 文档缓存、Python 子 skill 初始化脚本生成的索引和通用 reference 才是事实来源。
