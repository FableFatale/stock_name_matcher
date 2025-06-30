#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试股票匹配问题
"""

import pandas as pd
import logging
from stock_name_matcher import StockNameMatcher
from local_stock_data import LocalStockData

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_stock_matching():
    """调试股票匹配问题"""
    
    # 创建本地股票数据管理器
    local_data = LocalStockData()
    stock_list = local_data.get_stock_list()
    
    print(f"股票列表加载完成，共 {len(stock_list)} 只股票")
    print(f"列名: {list(stock_list.columns)}")
    print(f"前5行数据:")
    print(stock_list.head())
    
    # 检查特定股票代码
    test_codes = ['000037', '000603', '000798', '000823', '000970', '000985']
    
    print("\n=== 检查股票列表中是否存在测试代码 ===")
    for code in test_codes:
        matches = stock_list[stock_list['代码'] == code]
        if len(matches) > 0:
            stock_info = matches.iloc[0]
            print(f"✓ {code}: {stock_info['名称']}")
        else:
            print(f"✗ {code}: 未找到")
    
    # 创建股票匹配器
    matcher = StockNameMatcher()
    
    print("\n=== 测试标准化代码功能 ===")
    test_inputs = ["'000037", "'000603", "'000798", "'000823", "'000970", "'000985"]
    
    for input_code in test_inputs:
        normalized = matcher._normalize_stock_code(input_code)
        print(f"输入: {input_code} -> 标准化: {normalized}")
        
        # 测试匹配
        result = matcher.match_stock_code(input_code)
        print(f"匹配结果: {result.get('匹配状态', '未知')}")
        if result.get('匹配状态') == '匹配成功':
            print(f"  股票名称: {result.get('股票名称', '')}")
        print()

if __name__ == "__main__":
    debug_stock_matching()
