# 📈 Alpha Arena — 实盘对抗的 AI 交易实验平台

> 让多个 AI 模型在**同一市场、同一规则、同一时钟**下交易，并用**清晰可视化**比较谁更稳、谁更赚。
>
> ⚠️ 本项目仅用于**研究与教育**，不构成投资建议；请在合规前提下使用。

---

## 📘 项目简介

**Alpha Arena** 是一个以真实市场为测试场的 **AI 智能体交易对抗平台**。平台为每个模型提供**相同的实时数据与初始资金**，统一决策节奏与撮合假设，实时输出 **净值曲线 / PnL / 持仓 / 成交** 与风险指标，并保留**决策可追溯**的全链路信息（Prompt、行情快照、执行回报）。

---

## 🎯 MVP 目标与边界

**目标（能跑 / 可比 / 可复现）**

1. 同步时钟、同步行情、统一规则；2–6 个模型并行给出**结构化交易决策**。
2. 为每个模型维持**独立账本**，完成撮合并**实时统计净值**与核心指标。
3. **全链路审计**：每次决策可回看 Prompt、行情快照、输出 JSON、成交回报。

**边界（MVP 阶段暂不做）**

* 先用**现货**两标的（`BTCUSDT` / `ETHUSDT`），不做杠杆与合约；
* 仅做**做多/空仓**，不做做空；
* 仅用**市价单 + 固定滑点**；
* **固定 5 分钟**决策节奏，统一同根时钟。

**探索方向**

* 大模型在真实市场中的**稳定性 / 反应速度 / 风控差异**；
* **多模型对抗**与**自一致性投票**对收益与回撤的影响；
* **策略蒸馏 / 强化学习**让智能体从对抗中持续进化。

---

## 🏗️ 系统架构

```
/arena-mvp
├─ apps/
│  ├─ orchestrator/        # 调度：定时取数 → 生成 Prompt → 请求 LLM → 校验 → 执行 → 记账
│  ├─ exchange_adapter/    # 交易所适配：优先 paper（仿真撮合+固定滑点），预留 Bitget/OKX/CCXT
│  ├─ llm_gateway/         # LLM 网关：统一请求/重试/限速/超时（默认 8s 超时=HOLD）
│  ├─ portfolio/           # 账本 & 风控：每模型一账本；费率/滑点/限仓/强平
│  └─ dashboard/           # 可视化：净值曲线、PnL、持仓、成交、延迟、错误率
├─ storage/
│  ├─ postgres/            # K线、撮合、交易、资产、Prompt、决策、指标
│  └─ redis/               # 短期队列、去重、限速
├─ docker-compose.yml
└─ README.md
```

### 📋 服务职责速览

| 模块                   | 职责                                                                     |
| -------------------- | ---------------------------------------------------------------------- |
| **Orchestrator**     | 每 5 分钟取最近 60 分钟 1m K 线与盘口 → 生成统一 Prompt → 并行请求各 LLM → 校验 JSON → 送风控/执行 |
| **LLM Gateway**      | 统一供应商（OpenAI / DeepSeek / Anthropic / Google / Qwen…）的超时、重试、限速、日志      |
| **Exchange Adapter** | 先 **paper-trading**；可配置切换到 **Bitget 现货** 等实盘路径                         |
| **Portfolio**        | 现金/持仓/浮盈；统一费率（如万 5）、统一滑点（如 5–10bp）、限仓与强平规则                             |
| **Dashboard**        | 净值、当日 PnL、持仓/成交表、延迟与错误率；支持审计回放                                         |

---

## ⚙️ 技术栈

* **Backend**：Python 3.8+ / FastAPI / pandas / asyncio
* **Database**：PostgreSQL + Redis
* **Frontend**：Streamlit（或 Next.js 面板）
* **LLM 接口**：OpenAI / DeepSeek / Anthropic / Google / Qwen
* **交易所**：Bitget / OKX / CCXT（优先 paper）

---

## 📊 交易规范

### 统一 Prompt（摘要）

```
System: 你是量化交易代理，请仅输出一个 JSON，严格遵守 schema。
Market Time (UTC): {ts}
Account: cash_usdt: {cash}, positions: [{symbol, qty, avg_px}]
Universe: [BTCUSDT, ETHUSDT] (spot only)
Last 60m 1m-bars (ohlcv): {per-symbol arrays}
Live Ticker: {bid, ask, mid, spread_bp}
Fees: 5 bp; Slippage: 10 bp (est.)
Constraints:
  - Cadence: 5m once
  - Max gross exposure: 20% NAV per trade
  - Long only; at most 1 open symbol
  - Provide TP/SL as absolute prices
Task: If in position: hold/close with reasons; If flat: buy/hold with reasons
Return JSON only. No extra text.
```

### 输出 Schema（严格校验）

```json
{
  "symbol": "BTCUSDT|ETHUSDT|null",
  "action": "BUY|SELL|HOLD",
  "position_size_pct": 0.0,
  "take_profit": 0.0,
  "stop_loss": 0.0,
  "confidence": 0.0,
  "rationale": "short text (<=200 chars)"
}
```

### 风控与执行规则（MVP）

* **初始资金**：USDT 10,000 / 模型
* **单次下单**：≤ 20% NAV
* **持仓限制**：最多同时 1 个标的
* **止损/止盈**：由模型给出，风控兜底强平阈值 **-5%**
* **手续费**：万 5；**滑点**：10bp（paper）
* **去重**：5 分钟内仅一次新决策
* **超时处理**：LLM 超时 8s → **HOLD**

### 评价指标

* **实时**：净值、当日 PnL、持仓、暴露比例、推理延迟/超时率
* **阶段**：累计收益、最大回撤（MDD）、Calmar/Sharpe、胜率、盈亏比、交易次数、持仓时长、滑点/费率占比
* **合规性**：越权（超额下单）、JSON 违规、超时、拒答次数

---

## 🚀 实现计划（5–7 天可跑）

| 天数          | 任务                                                                                |
| ----------- | --------------------------------------------------------------------------------- |
| **Day 1**   | 初始化仓库 & Docker；建表（trades/positions/nav/prompts/decisions/metrics）；接 paper 撮合与行情抓取 |
| **Day 2**   | 完成 Orchestrator 基本循环；对接 1 家 LLM 跑通 E2E                                            |
| **Day 3**   | 接入 2–3 家 LLM；并行推理、超时回退、JSON 校验；风控兜底（限仓/止盈止损/强平）                                   |
| **Day 4**   | Dashboard（Streamlit）+ 实时/日内指标；审计回放（Prompt/JSON/行情快照）                              |
| **Day 5–7** | 稳定性与回测回灌；可选切换 **Bitget 现货** 做小额实盘链路验证                                             |

---

## 🔧 关键配置（默认值）

| 参数     | 默认                    |
| ------ | --------------------- |
| 决策周期   | 5m                    |
| 标的     | BTCUSDT / ETHUSDT（现货） |
| 初始资金   | $10,000 / 模型          |
| 单笔最大下单 | 20% NAV               |
| 手续费    | 万 5（paper）            |
| 滑点     | 10 bp（paper）          |
| 强平阈值   | -5%                   |
| LLM 超时 | 8s（超时=HOLD）           |
| 并发     | 按模型并行，串行写库            |

---

## 🛡️ 合规与安全

* **只读/最小权限** API Key；现货、单向做多；
* **资金隔离**：每模型独立子账户/账本；
* **Kill-Switch**：回撤 > 10% 自动全平并停机；
* **限速与熔断**：对 LLM 与交易所均设速率限制与退避重试；
* **审计日志**：入库 + 滚动文件备份。

---

## ⚡ 快速开始（MVP）

> 以 Python 版为例，先跑“真实价格获取 + 多模型决策对比”的最小闭环。

```bash
# 1) 克隆你的仓库
# git clone <your-repo-url> alpha-arena && cd alpha-arena

# 2) 安装依赖
pip install -r requirements.txt

# 3) 配置密钥
cp env.example .env
# 编辑 .env 填入 LLM/行情/交易所 API Key（paper 模式可用公钥或模拟）

# 4) 运行
python main.py
```

**版本与变更**

* 版本号：见 `VERSION.md`
* 变更日志：见 `CHANGELOG.md`

---

## 🔮 后续迭代（超出 MVP）

* 做空/杠杆、更多下单类型（限价 / 冰山）；
* 多时间框（1m+5m+1h）与归纳型多轮推理；
* **策略蒸馏**：从 LLM 决策中抽取可执行规则，训练轻量 Policy；
* 实盘风控：交易所回报校验、风控分级、OMS 异常自动降级；
* 公平性工具：时延对齐、成本对齐、数据漂移告警。

---

## 🤝 贡献

欢迎提交 Issue / PR：

* **Bug**：附复现步骤与环境；
* **新功能**：建议先开 Issue 对齐接口/数据结构；
* **文档**：欢迎完善部署脚本、Docker 化与 FAQ。

---

## 📄 许可证

MIT License（详见 `LICENSE`）。
