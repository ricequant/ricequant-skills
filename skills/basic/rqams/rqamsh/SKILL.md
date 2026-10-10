---
name: rqamsh
description: 用 rqamsh（rqams-harness）查询和操作 AMS 业务数据时使用：产品与产品组、工作空间、流水与估值报告导入、头寸报表与估值报告、净值与收益指标、归因与持仓分析、周报、对账、托管与份额事件、资源权限与标签。文档由 agent 自行从公开仓库获取，本技能不预置缓存。
---

# rqamsh（rqams-harness）

AMS 业务数据的 Python API 与 CLI（仓库 `ricequant/rqams-harness`）：取 AMS 已算好的业务数据、执行受控写入。本技能只给发行包、调用形态与取文档方式的最小指引；能力边界、字段语义、业务口径与写入护栏以该仓库的 `README.md` 与 `docs/` 为准。会话与凭据由调用方提供，本技能不代办登录、不索取账号密码。

## 一、安装与自检

发行包名 `rqams-harness`，Python 导入名与命令名都是 `rqamsh`，需 Python ≥3.10。取到仓库后（见「三、取文档」）在仓库根目录就地安装：

```console
python -m pip install -e .
rqamsh --help
rqamsh schema
```

`schema` 与 `--help` 离线可用，用于发现操作与参数；终端找不到 `rqamsh` 时先激活安装该包的 Python 环境，或改用 `python -m rqamsh`。

## 二、调用

CLI 的连接参数必须位于子命令之前，也可用 `RQAMSH_BASE_URL`、`RQAMSH_WORKSPACE_ID`、`RQAMSH_COOKIE` 提供（前两个必需）：

```console
rqamsh --base-url <AMS 地址> --workspace-id <空间 ID> --cookie sid=<令牌> products list
```

Python 侧先 `rqamsh.init(base_url, workspace_id=..., cookies={...})`，再用 `rqamsh.<块>.<操作>(...)`；并行多个身份时各自持有显式 `Client`，不共享模块默认实例。参数一律显式写成 `参数名=值`，CLI 用同名的 `--参数名`。会话怎么取得见仓库 `docs/connection.md`。

## 三、取文档

文档仓库（公开）：[ricequant/rqams-harness](https://github.com/ricequant/rqams-harness)，契约文档入口 [docs/index.md](https://github.com/ricequant/rqams-harness/blob/main/docs/index.md)。两种取法内容等价，按环境择一：

- 克隆后本地检索（可跨页 grep）：`git clone --depth 1 https://github.com/ricequant/rqams-harness.git`
- 按页读原文（无需克隆，适合克隆受限的网络）：`https://raw.githubusercontent.com/ricequant/rqams-harness/main/<path>`（`<path>` 是仓库内相对路径，如 `docs/balances.md`），读工具可按行区间分段取用，不必整页加载。

入口按顺序读，不要一次读多页：`README.md` → `docs/index.md` → 目标业务页 `docs/<块>.md` → 有字段页的块再读 `docs/fields/<块>.md`（`docs/fields/` 只覆盖承载对象的块，字段页清单见 `docs/index.md`）。

## 四、检索

- `docs/*.md` 的行尾由取文档方式决定：Windows 上 `git clone`（`core.autocrlf=true`）得到 CRLF，Linux 与 raw 单页是 LF。因此 `grep` 模式统一不要带 `$` 锚，写 `^## get`，不要写 `^## get$`。
- 操作标题有两级粒度：多数操作有独立的 `## <方法名>` 小节，少数族级小节把若干操作写在正文里。本地副本固定三步：`grep -n "^## " docs/<块>.md` 看结构 → `grep -n "<块>\.<操作>" docs/*.md` 取页与行号 → 只读该行号附近的区间。只读 raw 时没有跨页 grep，改用 `docs/index.md` 的导航加页内 `## ` 小节定位，需要跨页找操作名时再克隆。
- 单页可能很大（`docs/analytics.md` 1500+ 行、`docs/fields/balances.md` 460+ 行），不要整页读，也不要一次读多页。
- 文档与本地安装版本不一致时，以 `rqamsh schema` 的运行时输出为准。

## 五、`rqamsh` 未覆盖时

`rqams-cli/` 与 `rqamsc-python/` 是既往路径，作为过渡保留：只有 `rqamsh` 确实没有对应操作、或用户明确要求使用 `rqamsc` CLI 时，才按 `../SKILL.md` 的路由规则走它们。
