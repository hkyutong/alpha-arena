#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha Arena MVP - 主程序
最简化的AI交易决策对比系统
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market import MarketData
from core.decision import DecisionMaker
from adapters.openai_adapter import OpenAIAdapter
from adapters.claude_adapter import ClaudeAdapter


def main():
    """主函数"""
    print("🚀 Alpha Arena - 最简化MVP")
    print("=" * 50)
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 初始化市场数据管理器
        print("📊 初始化市场数据管理器...")
        market_data = MarketData()
        
        if not market_data.is_api_available():
            print("❌ 交易所API不可用，请检查配置")
            return
        
        # 获取实时价格
        print("💰 获取实时价格...")
        prices = market_data.get_current_prices()
        
        print("\n📈 当前市场价格:")
        print(market_data.format_prices_for_display(prices))
        
        # 检查是否有有效价格
        valid_prices = {k: v for k, v in prices.items() if v > 0}
        if not valid_prices:
            print("❌ 没有获取到有效价格，请检查网络连接")
            return
        
        # 初始化LLM适配器
        print("\n🤖 初始化AI模型...")
        
        # OpenAI适配器
        try:
            openai_adapter = OpenAIAdapter()
            openai_decision_maker = DecisionMaker(openai_adapter)
            print(f"✅ OpenAI ({openai_adapter.get_model_name()}) 初始化成功")
        except Exception as e:
            print(f"❌ OpenAI初始化失败: {e}")
            openai_decision_maker = None
        
        # Claude适配器
        try:
            claude_adapter = ClaudeAdapter()
            claude_decision_maker = DecisionMaker(claude_adapter)
            print(f"✅ Claude ({claude_adapter.get_model_name()}) 初始化成功")
        except Exception as e:
            print(f"❌ Claude初始化失败: {e}")
            claude_decision_maker = None
        
        if not openai_decision_maker and not claude_decision_maker:
            print("❌ 没有可用的AI模型，请检查API密钥配置")
            return
        
        # 获取AI决策
        print("\n🧠 获取AI交易决策...")
        
        decisions = {}
        
        # OpenAI决策
        if openai_decision_maker:
            print("\n🤖 OpenAI决策:")
            try:
                openai_decision = openai_decision_maker.get_decision(prices)
                decisions['OpenAI'] = openai_decision
                print(openai_decision_maker.format_decision_for_display(openai_decision))
            except Exception as e:
                print(f"❌ OpenAI决策获取失败: {e}")
        
        # Claude决策
        if claude_decision_maker:
            print("\n🤖 Claude决策:")
            try:
                claude_decision = claude_decision_maker.get_decision(prices)
                decisions['Claude'] = claude_decision
                print(claude_decision_maker.format_decision_for_display(claude_decision))
            except Exception as e:
                print(f"❌ Claude决策获取失败: {e}")
        
        # 决策对比
        if len(decisions) >= 2:
            print("\n📊 决策对比:")
            print("-" * 30)
            
            for model_name, decision in decisions.items():
                symbol = decision.get('symbol', 'None')
                action = decision.get('action', 'HOLD')
                print(f"   {model_name}: {action} {symbol}")
            
            # 检查是否一致
            if len(decisions) == 2:
                openai_decision = decisions.get('OpenAI', {})
                claude_decision = decisions.get('Claude', {})
                
                if (openai_decision.get('symbol') == claude_decision.get('symbol') and 
                    openai_decision.get('action') == claude_decision.get('action')):
                    print("   🎯 两个AI达成一致！")
                else:
                    print("   ⚡ 两个AI意见分歧")
        
        print("\n✅ 运行完成！")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
