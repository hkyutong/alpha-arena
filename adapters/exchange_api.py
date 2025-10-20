#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易所API适配器
基于现有的Bitget API获取真实价格数据
"""

import os
import sys
from typing import Dict, List

# 添加cex_scripts路径到sys.path
cex_scripts_path = "/Users/binguo/workspaces/cex_scripts/scripts/tools"
if cex_scripts_path not in sys.path:
    sys.path.append(cex_scripts_path)

try:
    from cex_verified_api_client import BitgetVerifiedAPIClient
except ImportError:
    print("❌ 无法导入BitgetVerifiedAPIClient，请检查cex_scripts路径")
    BitgetVerifiedAPIClient = None


class ExchangeAPI:
    """交易所API适配器"""
    
    def __init__(self):
        """初始化交易所API"""
        if BitgetVerifiedAPIClient is None:
            raise ImportError("BitgetVerifiedAPIClient未找到")
        
        try:
            self.client = BitgetVerifiedAPIClient()
            print("✅ Bitget API客户端初始化成功")
        except Exception as e:
            print(f"❌ Bitget API客户端初始化失败: {e}")
            self.client = None
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        获取多个代币的最新价格
        
        Args:
            symbols: 代币符号列表，如['BTCUSDT', 'ETHUSDT']
            
        Returns:
            价格字典，格式为{symbol: price}
        """
        if self.client is None:
            print("❌ API客户端未初始化")
            return {symbol: 0.0 for symbol in symbols}
        
        prices = {}
        
        for symbol in symbols:
            try:
                price = self.client.get_current_price(symbol)
                prices[symbol] = price
                print(f"✅ {symbol}: ${price:.4f}")
            except Exception as e:
                print(f"❌ 获取{symbol}价格失败: {e}")
                prices[symbol] = 0.0
        
        return prices
    
    def get_single_price(self, symbol: str) -> float:
        """
        获取单个代币的价格
        
        Args:
            symbol: 代币符号，如'BTCUSDT'
            
        Returns:
            价格
        """
        if self.client is None:
            return 0.0
        
        try:
            return self.client.get_current_price(symbol)
        except Exception as e:
            print(f"❌ 获取{symbol}价格失败: {e}")
            return 0.0
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.client is not None
