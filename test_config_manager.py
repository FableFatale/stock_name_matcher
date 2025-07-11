#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器测试脚本
"""

from config_manager import config_manager
import json

def test_config_manager():
    """测试配置管理器功能"""
    print("🧪 开始测试配置管理器...")
    
    # 1. 测试API密钥设置和获取
    print("\n1. 测试API密钥功能:")
    
    # 设置测试API密钥
    test_key = "test_api_key_12345"
    result = config_manager.set_api_key('tushare', test_key)
    print(f"   设置Tushare API密钥: {'成功' if result else '失败'}")
    
    # 获取API密钥
    retrieved_key = config_manager.get_api_key('tushare')
    print(f"   获取Tushare API密钥: {'成功' if retrieved_key == test_key else '失败'}")
    print(f"   密钥内容: {retrieved_key[:10]}..." if len(retrieved_key) > 10 else f"   密钥内容: {retrieved_key}")
    
    # 2. 测试配置摘要
    print("\n2. 测试配置摘要:")
    summary = config_manager.get_config_summary()
    print(f"   配置版本: {summary.get('version', 'unknown')}")
    print(f"   主要数据源: {summary.get('primary_data_source', 'unknown')}")
    print(f"   API密钥状态: {len([k for k, v in summary.get('api_keys_status', {}).items() if v.get('configured', False)])} 个已配置")
    
    # 3. 测试连接测试
    print("\n3. 测试连接功能:")
    
    # 测试本地数据源
    local_result = config_manager.test_api_connection('local')
    print(f"   本地数据源: {local_result['status']} - {local_result['message']}")
    
    # 测试AKShare连接
    akshare_result = config_manager.test_api_connection('akshare')
    print(f"   AKShare: {akshare_result['status']} - {akshare_result['message']}")
    
    # 4. 测试数据源配置
    print("\n4. 测试数据源配置:")
    data_source_config = config_manager.get_data_source_config()
    print(f"   主要数据源: {data_source_config.get('primary', 'unknown')}")
    print(f"   备用数据源: {', '.join(data_source_config.get('fallback', []))}")
    print(f"   超时设置: {data_source_config.get('timeout', 'unknown')} 秒")
    
    # 5. 测试系统设置
    print("\n5. 测试系统设置:")
    system_settings = config_manager.get_system_settings()
    print(f"   最大文件大小: {system_settings.get('max_file_size_mb', 'unknown')} MB")
    print(f"   支持的文件类型: {', '.join(system_settings.get('allowed_file_types', []))}")
    print(f"   自动备份: {'启用' if system_settings.get('auto_backup', False) else '禁用'}")
    print(f"   性能优化: {'启用' if system_settings.get('performance_optimization', False) else '禁用'}")
    
    # 6. 测试用户偏好
    print("\n6. 测试用户偏好:")
    user_preferences = config_manager.get_user_preferences()
    print(f"   默认API源: {user_preferences.get('default_api_source', 'unknown')}")
    print(f"   交叉验证: {'启用' if user_preferences.get('enable_cross_validation', False) else '禁用'}")
    print(f"   自动更新股票列表: {'启用' if user_preferences.get('auto_update_stock_list', False) else '禁用'}")
    
    print("\n✅ 配置管理器测试完成!")
    
    return True

def test_api_endpoints():
    """测试API端点（需要Web应用运行）"""
    print("\n🌐 测试Web API端点...")
    
    import requests
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试配置状态API
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            data = response.json()
            print(f"   配置状态API: 成功 - {data.get('status', 'unknown')}")
        else:
            print(f"   配置状态API: 失败 - HTTP {response.status_code}")
        
        # 测试API密钥状态API
        response = requests.get(f"{base_url}/api/config/api_keys")
        if response.status_code == 200:
            data = response.json()
            print(f"   API密钥状态API: 成功 - {len(data.get('api_keys', {}))} 个数据源")
        else:
            print(f"   API密钥状态API: 失败 - HTTP {response.status_code}")
        
        # 测试连接测试API
        response = requests.get(f"{base_url}/api/config/test_connection/local")
        if response.status_code == 200:
            data = response.json()
            print(f"   连接测试API: 成功 - 本地数据源状态: {data.get('status', 'unknown')}")
        else:
            print(f"   连接测试API: 失败 - HTTP {response.status_code}")
        
        # 测试股票数据状态API
        response = requests.get(f"{base_url}/api/stock_data_status")
        if response.status_code == 200:
            data = response.json()
            current_data = data.get('current_data', {})
            print(f"   股票数据状态API: 成功 - {current_data.get('total_stocks', 0)} 只股票")
        else:
            print(f"   股票数据状态API: 失败 - HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  无法连接到Web应用，请确保应用正在运行 (python app.py)")
    except Exception as e:
        print(f"   ❌ API测试失败: {e}")
    
    print("\n✅ Web API测试完成!")

if __name__ == "__main__":
    print("🚀 股票数据管理系统测试")
    print("=" * 50)
    
    # 测试配置管理器
    test_config_manager()
    
    # 测试Web API端点
    test_api_endpoints()
    
    print("\n🎉 所有测试完成!")
