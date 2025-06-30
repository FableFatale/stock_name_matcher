#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个股票代码匹配
"""

import requests
import json

def test_single_match():
    """测试单个股票代码匹配"""
    base_url = "http://localhost:5000"
    
    # 测试API状态
    print("1. 测试API状态...")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API状态: {data.get('status')}")
            print(f"股票数量: {data.get('stock_count')}")
        else:
            print(f"API状态异常: {response.text}")
            return
    except Exception as e:
        print(f"无法连接到API: {e}")
        return
    
    # 测试单个股票代码匹配
    print("\n2. 测试单个股票代码匹配...")
    test_codes = ['000037', "'000037"]
    
    for code in test_codes:
        print(f"\n测试代码: {code}")
        try:
            # URL编码处理
            import urllib.parse
            encoded_code = urllib.parse.quote(code)
            url = f"{base_url}/api/test_match/{encoded_code}"
            print(f"请求URL: {url}")
            
            response = requests.get(url)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"原始代码: {data.get('original_code')}")
                print(f"标准化代码: {data.get('normalized_code')}")
                
                match_result = data.get('match_result', {})
                print(f"匹配状态: {match_result.get('匹配状态')}")
                print(f"股票名称: {match_result.get('股票名称')}")
                
                stock_info = data.get('stock_list_info', {})
                print(f"股票列表总数: {stock_info.get('total_stocks')}")
                print(f"有代码列: {stock_info.get('has_code_column')}")
                print(f"样本代码: {stock_info.get('sample_codes')}")
            else:
                print(f"请求失败: {response.text}")
                
        except Exception as e:
            print(f"测试异常: {e}")

if __name__ == "__main__":
    test_single_match()
