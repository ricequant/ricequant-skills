# ricequant-skills

Skills developed by RiceQuant for use with Claude Code.

## 目录结构

```
skills/
├── basic/
│   ├── ricequant/            # Ricequant 平台通用文档查询
│   ├── rqdata-python/        # RQData Python API 查询技能
│   └── rqams/                # RQAMS 业务路由与旧 CLI/SDK 过渡路径
└── research/                 # 股票研究报告技能（依赖 RQData CLI）
    ├── catalyst-calendar/    # 催化剂日历
    ├── earnings-analysis/    # 财报分析
    ├── earnings-preview/     # 财报预览
    ├── idea-generation/      # 投资创意生成
    ├── initiating-coverage/  # 首次覆盖研究
    ├── morning-note/         # 晨会纪要
    ├── report-renderer/      # HTML 报告渲染
    ├── sector-overview/      # 行业概览
    └── thesis-tracker/       # 投资论文跟踪
```

## Skills

### Basic

#### `ricequant`

Ricequant 平台通用文档查询工具。通过在线文档自动检索，覆盖以下组件：

| 组件 | 说明 |
|---|---|
| RQAlphaPlus | 回测框架——参数配置、交易接口、数据查询接口 |
| RQData | 数据 API——A 股、港股、期货、期权、指数、基金、可转债 |
| RQFactor | 因子计算——内置因子、内置算子、自定义算子 |
| RQOptimizer | 优化器——选股 API、投资组合优化 |
| RQPAttr | 归因分析——Brinson 行业归因、因子归因 |
| RQSDK | 本地开发套件——环境配置、组件集成 |
| RQAMS / RQAMSC | 资产管理系统与 Python SDK——产品、工作空间、交易流水、估值表、持仓、分析与自动化接口 |

**注意：** 需联网访问 `ricequant.com` 文档。`document-index.txt` 未列出 RQAMS，查询 RQAMS / RQAMSC 时需直接访问 `https://www.ricequant.com/doc/rqams/` 或 `https://www.ricequant.com/doc/rqamsc/`。

---

#### `rqdata-python`

RQData 数据 API 使用指南。支持 A 股、港股、期货、期权、指数、基金、可转债等市场数据查询，包含 HTTP API 和 Python API 文档。本地缓存文档，无需联网即可查询。

**前置要求：** 正确安装 rqsdk 并配置许可证。

---

#### `rqams`

AMS 业务数据优先使用 `rqamsh`。[SDK 与 Agent Skill 安装说明](https://github.com/ricequant/rqams-harness/blob/dev/README.md#agent-skill)由 `rqams-harness` 维护，使用它不需要先安装本仓库。

本仓库的 [`rqams`](skills/basic/rqams/SKILL.md) 提供业务路由，保留 `rqams-cli` 与 `rqamsc-python` 过渡路径。仅在 `rqamsh` 未覆盖目标操作或用户明确要求时使用；各自的前置要求和安装方式见对应 Skill。

---

### Research

> **注意：** 所有 research skills 依赖 **RQData CLI**（`rqdata` 命令行工具），请确保已正确安装并配置后再使用。
> RQData CLI github 仓库：https://github.com/ricequant/rqdata-cli
> RQData CLI 安装命令：`npm install -g @ricequant2026/rqdata-cli`

所有 research skills 均遵循三阶段流程：**数据采集 → 报告生成 → HTML 渲染**，输出专业可读的研究报告。

| Skill | 说明 |
|---|---|
| `catalyst-calendar` | 催化剂日历——追踪覆盖股票池未来 30 天的财报、分红、公告等重要事件 |
| `earnings-analysis` | 财报分析——财报披露后基于真实财务数据、市场预期和股价反应完成结构化复盘 |
| `earnings-preview` | 财报预览——财报发布前基于历史财务、一致预期和研报口径构建可追踪的预判框架 |
| `idea-generation` | 投资创意生成——系统化量化筛选，输出价值、成长、质量三类候选股 |
| `initiating-coverage` | 首次覆盖研究——基于财务、股权、交易、分红、可比公司等数据输出长篇结构化研究报告 |
| `morning-note` | 晨会纪要——汇总隔夜公告、财务更新、昨日股价表现与今日重点观察名单 |
| `report-renderer` | HTML 渲染——将其他 skill 生成的 Markdown 报告渲染为专业可浏览的 HTML 文档 |
| `sector-overview` | 行业概览——基于行业股票池与真实财务/估值/价格数据完成行业层面结构化分析 |
| `thesis-tracker` | 投资论文跟踪——系统化跟踪核心观点、关键支柱、催化剂和风险信号 |

## 示例输出

`research-example/` 目录包含各 research skill 的示例输出文件，可供参考。
