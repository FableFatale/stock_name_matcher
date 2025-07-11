#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能建议API功能
"""

import requests
import json

def test_failure_suggestion():
    """测试失败建议功能"""
    print("🧪 测试智能建议API功能")
    print("-" * 40)
    
    # 记录多次失败来触发建议
    for i in range(4):
        response = requests.post('http://localhost:5000/api/record_failure/akshare', 
                               json={'error_type': 'timeout'})
        
        if response.status_code == 200:
            data = response.json()
            suggestion = data.get('suggestion', {})
            
            print(f"第{i+1}次失败:")
            print(f"  失败次数: {suggestion.get('failure_count', 0)}/{suggestion.get('failure_threshold', 3)}")
            print(f"  建议配置: {suggestion.get('should_suggest', False)}")
            print(f"  建议原因: {suggestion.get('suggestion_reason', '无')}")
            
            if suggestion.get('should_suggest', False):
                print(f"  🎯 触发建议！系统建议用户配置API密钥")
            
            print()
        else:
            print(f"第{i+1}次失败: API请求失败 - {response.status_code}")
    
    # 检查数据源统计
    print("📊 检查数据源统计:")
    response = requests.get('http://localhost:5000/api/data_source_stats')
    if response.status_code == 200:
        data = response.json()
        akshare_stats = data.get('stats', {}).get('akshare', {})
        
        print(f"  AKShare统计:")
        print(f"    失败次数: {akshare_stats.get('failure_count', 0)}")
        print(f"    总请求数: {akshare_stats.get('total_requests', 0)}")
        print(f"    成功率: {akshare_stats.get('success_rate', 100)}%")
        print(f"    建议配置API: {akshare_stats.get('should_suggest_api', False)}")
        print(f"    建议原因: {akshare_stats.get('suggestion_reason', '无')}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    try:
        test_failure_suggestion()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web应用，请确保应用正在运行 (python app.py)")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
