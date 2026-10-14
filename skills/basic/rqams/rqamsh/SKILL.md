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

`schema` 与 `--help` 离线可用，用于发现操作与参数；终端找不到 `rqamsh` 时先激活安装该包的 Python 环境，或改用 `python -m rqamsh`。更新已有安装：拉取仓库最新代码后重跑上面的安装与自检命令，操作有无变化以 `rqamsh schema` 为准。

## 二、调用

CLI 的连接参数必须位于子命令之前，也可用 `RQAMSH_BASE_URL`、`RQAMSH_COOKIE` 提供（只有基础地址必需）：

```console
rqamsh --base-url <AMS 地址> --cookie sid=<令牌> products list
```

CLI 默认使用当前身份可见空间中的第一个，命令直接执行，无需先列举。需要指定非默认分区时在该命令前加 `--workspace-id <id>`（也可用 `RQAMSH_WORKSPACE_ID` 提供）；CLI 每个进程只执行一个操作，所以每个要换分区的命令各自带上该参数。`rqamsh --base-url <AMS 地址> --cookie sid=<令牌> workspaces list` 可查看当前身份可见的空间。

Python 侧先 `rqamsh.init(base_url, cookies={...})`，再用 `rqamsh.<块>.<操作>(...)`；客户端在首次业务调用时自动把当前身份可见空间中的第一个作为默认分区，无需预先指定或列举。需要切换分区时用 `client.workspaces.use(<id 或名称>)`，`client.workspaces.list()` 可随时查看可见空间，这两个调用本身不影响默认分区。并行多个身份时各自持有显式 `Client`，不共享模块默认实例。参数一律显式写成 `参数名=值`，CLI 用同名的 `--参数名`。会话怎么取得见仓库 `docs/connection.md`。

## 三、取文档

文档仓库（公开）：[ricequant/rqams-harness](https://github.com/ricequant/rqams-harness)，契约文档入口 [docs/index.md](https://github.com/ricequant/rqams-harness/blob/main/docs/index.md)。两种取法内容等价，按环境择一：

- 克隆后本地检索（可跨页 grep）：`git clone --depth 1 https://github.com/ricequant/rqams-harness.git`
- 按页读原文（无需克隆，适合克隆受限的网络）：`https://raw.githubusercontent.com/ricequant/rqams-harness/main/<path>`（`<path>` 是仓库内相对路径，如 `docs/balances.md`），读工具可按行区间分段取用，不必整页加载。
- 文档随仓库更新、没有自动推送：每次任务开始时重新获取（重新 `clone --depth 1`，或对已有的本地副本先 `git pull`），不要复用旧副本；`raw` 单页读的一直是默认分支上的最新内容。

入口按顺序读，不要一次读多页：`README.md` → `docs/index.md` → `docs/connection.md`（连接、等待、错误、未就绪与取数节奏）→ 目标业务页 `docs/<块>.md` → 有字段页的块再读 `docs/fields/<块>.md`（`docs/fields/` 只覆盖承载对象的块，字段页清单见 `docs/index.md`）。

开工前必读：先在 `docs/index.md` 读「常见场景」「口径速查」与「必要边界」（后者含执行与交付纪律），再读 `docs/connection.md` 与目标业务页，然后才开始调用；不要凭字段名或操作名推断业务口径，口径以权威页为准。

## 四、检索

- `docs/*.md` 的行尾由取文档方式决定：Windows 上 `git clone`（`core.autocrlf=true`）得到 CRLF，Linux 与 raw 单页是 LF。因此 `grep` 模式统一不要带 `$` 锚，写 `^## get`，不要写 `^## get$`。
- 操作标题有两级粒度：多数操作有独立的 `## <方法名>` 小节，少数族级小节把若干操作写在正文里。本地副本固定三步：`grep -n "^## " docs/<块>.md` 看结构 → `grep -rn "<块>\.<操作>" docs` 取页与行号（`-r` 是为了带上子页） → 只读该行号附近的区间。只读 raw 时没有跨页 grep，改用 `docs/index.md` 的导航加页内 `## ` 小节定位，需要跨页找操作名时再克隆。
- 一个业务块可能不止一页：`analytics` 块是块入口页 `docs/analytics/index.md`（块总述、跨族场景表、接口公共约定、四页导航）加 `docs/analytics/` 下的四个主题子页（`metrics`、`holdings_analysis`、`attribution`、`portfolio_analysis`）。查该块的操作先看入口页的「页面划分」，再只读命中的子页；子页不重复场景表与接口约定，需要时点回入口页。
- 单页可能很大（`docs/analytics/metrics.md` 470 行、`docs/fields/balances.md` 460 行），不要整页读，也不要一次读多页。
- 文档与本地安装版本不一致时，以 `rqamsh schema` 的运行时输出为准。

## 五、`rqamsh` 未覆盖时

`rqams-cli/` 与 `rqamsc-python/` 是既往路径，作为过渡保留：只有 `rqamsh` 确实没有对应操作、或用户明确要求使用 `rqamsc` CLI 时，才按 `../SKILL.md` 的路由规则走它们。
