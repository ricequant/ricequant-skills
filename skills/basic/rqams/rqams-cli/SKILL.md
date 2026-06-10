---
name: rqams-cli
description: 使用本地 rqamsc CLI 查询和操作 RQAMS 时使用，覆盖产品、workspace、交易流水、估值表、持仓报表、模拟交易、对账、报表和分析数据等标准任务。
---

# RQAMS CLI

当用户请求可由本地 `rqamsc` 命令完成的 RQAMS 数据查询或操作时，使用此 skill。

## 使用方法

### 文档缓存

查文档前，先在 skill 目录运行：

```powershell
python scripts/init_skill.py
```

`init_skill.py` 管理 CLI 文档缓存。它会复用本地 `cache/`；只有文档或命令索引缺失、缓存超过 7 天，或显式传入 `--force-refresh` 时，才从 GitHub 同步 CLI 文档到本地 `cache/` 并生成命令索引。

常用命令：
- 普通查文档：`python scripts/init_skill.py`
- 强制刷新文档：`python scripts/init_skill.py --force-refresh`

### 前置检查

先确认 CLI 可用：

```shell
rqamsc --version
```

如果 `rqamsc` 不可用，先按官方 CLI 文档确认当前应使用全局安装、源码运行还是项目内构建方式；不要在 skill 中维护安装命令细节。

### 事实来源

不要在 skill 中重复维护完整命令字段、安装命令或业务 payload 结构。事实来源按用途使用：

1. CLI 运行时 schema：当前二进制的机器可执行契约，用来确认目标命令是否存在、payload 字段形状、输出格式能力和兼容性。
2. 本地生成的缓存文档：业务语义、人类可读说明、调用协议、文件路径字段、示例和排错建议，位于 `cache/docs/`。
3. GitHub 文档：缓存刷新来源，地址为 `https://github.com/ricequant/rqams-cli/tree/master/docs`；日常查阅优先使用本地缓存。

运行时 schema 示例：

```powershell
rqamsc schema list
rqamsc schema get --payload '{"command":"get product-list"}'
```

执行任何非 `schema` / `--version` 的业务命令前，必须先查本地缓存文档确认命令命名、请求 payload、文件路径字段、输出 envelope/NDJSON 和业务数据格式；不要只根据 schema 字段名猜测接口语义：

- `cache/docs/rqams_cli_manual.md`
- `cache/docs/commands/*.md`
- `cache/doc_index/command_index.md`

其中 `cache/docs/rqams_cli_manual.md` 是总入口，解释统一调用协议、命令发现、认证与 workspace、文件上传/下载和 Agent 使用建议；`cache/docs/commands/*.md` 按业务域说明具体命令、字段和示例；`cache/doc_index/command_index.md` 用于快速定位命令所在文档和行号。若文档与运行时 schema 不一致，执行层面优先按运行时 schema，业务解释和示例仍参考缓存文档，并在回复中说明差异。

### 命令调用

统一命令格式：

```text
rqamsc <verb> <resource> --payload <json|@file|->
```

优先使用 JSON payload：

```shell
rqamsc <verb> <resource> --payload '{"field":"value"}'
```

Windows `cmd.exe` 不适合直接写复杂 inline JSON；优先改用 PowerShell，或把 payload 写入文件后使用 `--payload @payload.json`。

payload 较大时，使用文件或 stdin：

```powershell
rqamsc <verb> <resource> --payload @payload.json
Get-Content -Raw payload.json | rqamsc <verb> <resource> --payload -
```

默认输出是 JSON envelope。只有 `schema get` 显示命令支持 NDJSON 时，才使用 `"format":"ndjson"`。

### 安全要求

对于创建、更新、删除、上传、重算等写操作，除非用户已给出精确指令，否则执行命令前必须明确目标资源和关键 payload 字段。

命令失败时，读取 JSON envelope 中的 `error.code` 和 `error.message`，总结可执行的问题和下一步，不要只贴原始日志。
