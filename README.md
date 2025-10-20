# 🧠 Alpha Arena

> 一个让 AI 模型在真实市场中进行实盘交易与对抗的实验平台。  
> “让智能体在不确定性中生存，并最终学会盈利。”

---

## 📘 项目简介

**Alpha Arena** 是一个以真实市场为测试场的 AI 智能体交易实验平台。  
每个模型（如 GPT-5、Claude、DeepSeek、Gemini 等）都会获得相同的实时市场数据与初始资金，独立决策、执行交易，并实时比较收益、回撤和风险控制能力。

该项目旨在探索：
- 大语言模型是否能在真实金融市场中形成可持续的交易逻辑；
- 不同模型在风险、反应速度、决策稳定性方面的差异；
- 如何通过强化学习、策略蒸馏等手段让 AI 智能体不断进化。

---

## 🏗️ 系统模块（MVP 阶段）

| 模块 | 说明 |
|------|------|
| **Orchestrator** | 调度中心，负责行情采集、模型调用、下单执行 |
| **LLM Gateway** | 各大模型统一接入网关 |
| **Exchange Adapter** | 交易所接口 |
| **Portfolio & Risk** | 账本与风控模块 |
| **Dashboard** | 可视化界面（Streamlit 实时展示净值曲线与交易详情） |

---

## ⚙️ 技术栈

- **Backend**：Python 3.11 / FastAPI / pandas / asyncio  
- **Database**：PostgreSQL + Redis  
- **Frontend**：Streamlit (或 Next.js 可视化面板)  
- **LLM 接口**：OpenAI / DeepSeek / Anthropic / Google / Qwen  

---

## 🚀 快速开始（预告）

```bash
git clone https://github.com/AmadeusGB/alpha-arena.git
cd alpha-arena
docker compose up
