#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试
"""

from stock_name_matcher import StockNameMatcher

def test_api_matching():
    """测试API匹配功能"""
    apis = ['akshare', 'sina', 'tencent', 'eastmoney', 'local']
    test_code = "'000037"
    
    print("🧪 快速API匹配测试")
    print("="*50)
    
    for api in apis:
        print(f"\n测试 {api.upper()}...")
        try:
            matcher = StockNameMatcher(api_source=api)
            result = matcher.match_stock_code(test_code)
            
            status = result.get('匹配状态', '未知')
            name = result.get('股票名称', 'N/A')
            
            if status == '匹配成功':
                print(f"✅ {api}: {status} - {name}")
            else:
                print(f"❌ {api}: {status}")
                
        except Exception as e:
            print(f"❌ {api}: 错误 - {str(e)[:50]}...")

if __name__ == "__main__":
    test_api_matching()
