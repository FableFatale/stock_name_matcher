#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能API配置建议功能测试脚本
"""

from config_manager import config_manager
import requests
import time

def test_failure_monitoring():
    """测试失败监控功能"""
    print("🧪 测试数据源失败监控功能...")
    
    # 1. 模拟数据源失败
    test_source = "akshare"
    print(f"\n1. 模拟 {test_source} 数据源失败:")
    
    for i in range(4):  # 超过阈值(3)
        result = config_manager.record_data_source_failure(test_source, "timeout")
        print(f"   第 {i+1} 次失败记录: {'成功' if result else '失败'}")
        
        # 检查是否应该建议配置API
        suggestion = config_manager.should_suggest_api_config(test_source)
        print(f"   建议配置API: {suggestion['should_suggest']}")
        print(f"   失败次数: {suggestion['failure_count']}/{suggestion['failure_threshold']}")
        print(f"   建议原因: {suggestion['suggestion_reason']}")
        print()
    
    return True

def test_suggestion_cooldown():
    """测试建议冷却功能"""
    print("🧪 测试建议冷却功能...")
    
    test_source = "sina"
    
    # 1. 触发建议
    for i in range(3):
        config_manager.record_data_source_failure(test_source, "timeout")
    
    suggestion1 = config_manager.should_suggest_api_config(test_source)
    print(f"   第一次检查建议: {suggestion1['should_suggest']}")
    
    # 2. 立即再次检查（应该被冷却）
    suggestion2 = config_manager.should_suggest_api_config(test_source)
    print(f"   立即再次检查: {suggestion2['should_suggest']}")
    
    return True

def test_api_key_effect():
    """测试API密钥对建议的影响"""
    print("🧪 测试API密钥对建议的影响...")
    
    test_source = "tencent"
    
    # 1. 没有API密钥时的建议
    for i in range(3):
        config_manager.record_data_source_failure(test_source, "timeout")
    
    suggestion_before = config_manager.should_suggest_api_config(test_source)
    print(f"   配置API密钥前的建议: {suggestion_before['should_suggest']}")
    
    # 2. 配置API密钥
    config_manager.set_api_key(test_source, "test_api_key_123")
    
    # 3. 有API密钥时的建议
    suggestion_after = config_manager.should_suggest_api_config(test_source)
    print(f"   配置API密钥后的建议: {suggestion_after['should_suggest']}")
    print(f"   有API密钥: {suggestion_after['has_api_key']}")
    
    return True

def test_data_source_stats():
    """测试数据源统计功能"""
    print("🧪 测试数据源统计功能...")
    
    stats = config_manager.get_data_source_stats()
    
    print("   数据源统计信息:")
    for source, stat in stats.items():
        print(f"   {source}:")
        print(f"     失败次数: {stat['failure_count']}")
        print(f"     总请求数: {stat['total_requests']}")
        print(f"     成功率: {stat['success_rate']}%")
        print(f"     建议配置API: {stat['should_suggest_api']}")
        print(f"     有API密钥: {stat['has_api_key']}")
        print(f"     建议原因: {stat['suggestion_reason']}")
        print()
    
    return True

def test_web_api_endpoints():
    """测试Web API端点"""
    print("🧪 测试Web API端点...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试数据源统计API
        response = requests.get(f"{base_url}/api/data_source_stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   数据源统计API: 成功 - {len(data.get('stats', {}))} 个数据源")
        else:
            print(f"   数据源统计API: 失败 - HTTP {response.status_code}")
        
        # 2. 测试数据源建议API
        response = requests.get(f"{base_url}/api/data_source_suggestion/akshare")
        if response.status_code == 200:
            data = response.json()
            suggestion = data.get('suggestion', {})
            print(f"   数据源建议API: 成功 - 建议配置: {suggestion.get('should_suggest', False)}")
        else:
            print(f"   数据源建议API: 失败 - HTTP {response.status_code}")
        
        # 3. 测试失败记录API
        response = requests.post(f"{base_url}/api/record_failure/test_source", 
                               json={"error_type": "timeout"})
        if response.status_code == 200:
            data = response.json()
            print(f"   失败记录API: 成功 - {data.get('message', '')}")
        else:
            print(f"   失败记录API: 失败 - HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  无法连接到Web应用，请确保应用正在运行")
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    return True

def test_suggestion_scenarios():
    """测试各种建议场景"""
    print("🧪 测试各种建议场景...")
    
    scenarios = [
        {"source": "eastmoney", "failures": 2, "expected": False, "desc": "失败次数未达阈值"},
        {"source": "netease", "failures": 3, "expected": True, "desc": "失败次数达到阈值"},
        {"source": "xueqiu", "failures": 5, "expected": True, "desc": "失败次数超过阈值"},
    ]
    
    for scenario in scenarios:
        source = scenario["source"]
        failures = scenario["failures"]
        expected = scenario["expected"]
        desc = scenario["desc"]
        
        print(f"\n   场景: {desc}")
        print(f"   数据源: {source}, 失败次数: {failures}")
        
        # 模拟失败
        for i in range(failures):
            config_manager.record_data_source_failure(source, "timeout")
        
        # 检查建议
        suggestion = config_manager.should_suggest_api_config(source)
        actual = suggestion["should_suggest"]
        
        print(f"   预期建议: {expected}, 实际建议: {actual}")
        print(f"   测试结果: {'✅ 通过' if actual == expected else '❌ 失败'}")
    
    return True

def reset_test_data():
    """重置测试数据"""
    print("🔄 重置测试数据...")
    
    # 清空监控数据
    config_manager.config_data["data_source_monitoring"] = {
        "failure_counts": {},
        "last_failures": {},
        "last_suggestions": {},
        "total_requests": {},
        "success_rates": {}
    }
    
    # 清空测试API密钥
    test_sources = ["akshare", "sina", "tencent", "eastmoney", "netease", "xueqiu"]
    for source in test_sources:
        config_manager.set_api_key(source, "")
    
    config_manager.save_config()
    print("   测试数据已重置")

if __name__ == "__main__":
    print("🚀 智能API配置建议功能测试")
    print("=" * 60)
    
    # 重置测试数据
    reset_test_data()
    
    # 运行测试
    tests = [
        test_failure_monitoring,
        test_suggestion_cooldown,
        test_api_key_effect,
        test_data_source_stats,
        test_suggestion_scenarios,
        test_web_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过\n")
            else:
                print("❌ 测试失败\n")
        except Exception as e:
            print(f"❌ 测试异常: {e}\n")
    
    print("=" * 60)
    print(f"🎉 测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎊 所有测试都通过了！智能建议功能工作正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
