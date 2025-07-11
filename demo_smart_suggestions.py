#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能API配置建议功能演示脚本
模拟真实使用场景，展示智能建议功能
"""

from config_manager import config_manager
import time
import requests

def demo_scenario_1():
    """演示场景1: 免费数据源连续超时"""
    print("📊 演示场景1: 免费数据源连续超时")
    print("-" * 50)
    
    source = "akshare"
    print(f"用户选择了 {source} 数据源进行股票匹配...")
    
    # 模拟连续3次超时失败
    for i in range(3):
        print(f"\n第 {i+1} 次请求:")
        print(f"  ⏱️  请求 {source} API...")
        time.sleep(0.5)  # 模拟请求延迟
        print(f"  ❌ 请求超时 (30秒)")
        
        # 记录失败
        config_manager.record_data_source_failure(source, "timeout")
        
        # 检查是否应该建议
        suggestion = config_manager.should_suggest_api_config(source)
        
        if suggestion["should_suggest"]:
            print(f"  💡 系统建议: {suggestion['suggestion_reason']}")
            print(f"  🔧 建议操作: 配置 {source} API密钥以获得更稳定的服务")
            break
        else:
            print(f"  📊 失败统计: {suggestion['failure_count']}/{suggestion['failure_threshold']}")
    
    print("\n✅ 演示完成: 系统智能检测到连续失败并提供了配置建议")

def demo_scenario_2():
    """演示场景2: 用户配置API密钥后的效果"""
    print("\n📊 演示场景2: 用户配置API密钥后的效果")
    print("-" * 50)
    
    source = "sina"
    
    # 先模拟失败触发建议
    print(f"用户使用 {source} 数据源，遇到连续失败...")
    for i in range(3):
        config_manager.record_data_source_failure(source, "timeout")
    
    suggestion_before = config_manager.should_suggest_api_config(source)
    print(f"配置前建议状态: {suggestion_before['should_suggest']}")
    print(f"建议原因: {suggestion_before['suggestion_reason']}")
    
    # 用户配置API密钥
    print(f"\n🔧 用户配置了 {source} API密钥...")
    config_manager.set_api_key(source, "user_configured_api_key_12345")
    
    # 检查配置后的建议状态
    suggestion_after = config_manager.should_suggest_api_config(source)
    print(f"配置后建议状态: {suggestion_after['should_suggest']}")
    print(f"建议原因: {suggestion_after['suggestion_reason']}")
    
    print("\n✅ 演示完成: 配置API密钥后，系统不再提示建议")

def demo_scenario_3():
    """演示场景3: 多数据源状态监控"""
    print("\n📊 演示场景3: 多数据源状态监控")
    print("-" * 50)
    
    # 模拟不同数据源的不同状态
    scenarios = [
        {"source": "tencent", "failures": 1, "desc": "偶尔失败"},
        {"source": "eastmoney", "failures": 3, "desc": "达到阈值"},
        {"source": "netease", "failures": 5, "desc": "严重问题"},
    ]
    
    for scenario in scenarios:
        source = scenario["source"]
        failures = scenario["failures"]
        desc = scenario["desc"]
        
        print(f"\n{source} 数据源 ({desc}):")
        for i in range(failures):
            config_manager.record_data_source_failure(source, "timeout")
        
        suggestion = config_manager.should_suggest_api_config(source)
        print(f"  失败次数: {suggestion['failure_count']}")
        print(f"  建议配置: {suggestion['should_suggest']}")
        print(f"  状态说明: {suggestion['suggestion_reason']}")
    
    # 显示整体统计
    print(f"\n📈 整体数据源状态:")
    stats = config_manager.get_data_source_stats()
    
    for source, stat in stats.items():
        if stat['total_requests'] > 0:  # 只显示有请求的数据源
            status_icon = "🟢" if stat['success_rate'] >= 80 else "🟡" if stat['success_rate'] >= 50 else "🔴"
            api_icon = "🔑" if stat['has_api_key'] else "🔓"
            suggest_icon = "💡" if stat['should_suggest_api'] else "✅"
            
            print(f"  {status_icon} {source}: 成功率 {stat['success_rate']}% {api_icon} {suggest_icon}")
    
    print("\n✅ 演示完成: 系统提供了全面的数据源状态监控")

def demo_web_interface():
    """演示场景4: Web界面集成效果"""
    print("\n📊 演示场景4: Web界面集成效果")
    print("-" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试数据源建议API
        print("🌐 测试Web界面API集成...")
        
        # 获取数据源统计
        response = requests.get(f"{base_url}/api/data_source_stats")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print("📊 当前数据源状态 (Web API):")
            for source, stat in stats.items():
                if stat['total_requests'] > 0:
                    print(f"  {source}: 失败{stat['failure_count']}次, 成功率{stat['success_rate']}%")
                    if stat['should_suggest_api']:
                        print(f"    💡 建议: {stat['suggestion_reason']}")
        
        # 测试建议API
        print(f"\n🔍 检查特定数据源建议...")
        response = requests.get(f"{base_url}/api/data_source_suggestion/eastmoney")
        if response.status_code == 200:
            data = response.json()
            suggestion = data.get('suggestion', {})
            print(f"eastmoney 建议状态: {suggestion.get('should_suggest', False)}")
            print(f"建议原因: {suggestion.get('suggestion_reason', '无')}")
        
        print("\n✅ 演示完成: Web界面API集成正常工作")
        
    except requests.exceptions.ConnectionError:
        print("⚠️  Web应用未运行，跳过Web界面演示")
        print("   请运行 'python app.py' 启动Web应用后重试")
    except Exception as e:
        print(f"❌ Web界面演示失败: {e}")

def demo_user_workflow():
    """演示场景5: 完整用户工作流程"""
    print("\n📊 演示场景5: 完整用户工作流程")
    print("-" * 50)
    
    print("👤 用户工作流程模拟:")
    print("1. 用户选择免费数据源进行股票匹配")
    print("2. 遇到网络问题，连续失败")
    print("3. 系统智能提示配置API密钥")
    print("4. 用户配置API密钥")
    print("5. 系统恢复正常工作")
    
    source = "xueqiu"
    
    # 步骤1-2: 模拟失败
    print(f"\n🔄 步骤1-2: 用户使用 {source}，遇到连续失败...")
    for i in range(3):
        config_manager.record_data_source_failure(source, "network_error")
        print(f"  第{i+1}次失败: 网络连接超时")
    
    # 步骤3: 系统提示
    suggestion = config_manager.should_suggest_api_config(source)
    if suggestion["should_suggest"]:
        print(f"\n💡 步骤3: 系统智能提示")
        print(f"  {suggestion['suggestion_reason']}")
        print(f"  建议: 配置 {source} API密钥以获得更稳定的服务")
    
    # 步骤4: 用户配置
    print(f"\n🔧 步骤4: 用户配置API密钥")
    config_manager.set_api_key(source, "user_api_key_configured")
    print(f"  ✅ {source} API密钥配置完成")
    
    # 步骤5: 检查状态
    suggestion_after = config_manager.should_suggest_api_config(source)
    print(f"\n📊 步骤5: 系统状态更新")
    print(f"  建议状态: {suggestion_after['should_suggest']}")
    print(f"  状态说明: {suggestion_after['suggestion_reason']}")
    
    print("\n✅ 演示完成: 完整工作流程展示了智能建议的实用价值")

def reset_demo_data():
    """重置演示数据"""
    print("🔄 重置演示数据...")
    config_manager.config_data["data_source_monitoring"] = {
        "failure_counts": {},
        "last_failures": {},
        "last_suggestions": {},
        "total_requests": {},
        "success_rates": {}
    }
    
    # 清空演示用的API密钥
    demo_sources = ["akshare", "sina", "tencent", "eastmoney", "netease", "xueqiu"]
    for source in demo_sources:
        config_manager.set_api_key(source, "")
    
    config_manager.save_config()
    print("✅ 演示数据已重置")

if __name__ == "__main__":
    print("🎬 智能API配置建议功能演示")
    print("=" * 60)
    print("本演示将展示系统如何智能检测数据源问题并提供配置建议")
    print("=" * 60)
    
    # 重置数据
    reset_demo_data()
    
    # 运行演示场景
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    demo_web_interface()
    demo_user_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成!")
    print("💡 主要特性:")
    print("  ✅ 智能检测数据源连续失败")
    print("  ✅ 自动建议配置API密钥")
    print("  ✅ 建议冷却机制避免重复提示")
    print("  ✅ API密钥配置后自动停止建议")
    print("  ✅ 全面的数据源状态监控")
    print("  ✅ Web界面无缝集成")
    print("\n🚀 用户现在可以享受更智能的股票数据管理体验！")
