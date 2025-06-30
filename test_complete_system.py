#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统测试
测试自动文件管理、股票匹配和Web应用的集成
"""

import os
import sys
import time
import pandas as pd
import requests
from datetime import datetime
from auto_file_manager import AutoFileManager

def create_test_stock_file():
    """创建测试股票数据文件"""
    print("📝 创建测试股票数据文件...")
    
    # 创建包含一些真实股票代码的测试数据
    test_data = [
        {'code': '000001', 'name': '平安银行'},
        {'code': '000002', 'name': '万科A'},
        {'code': '000037', 'name': '深南电A'},
        {'code': '000603', 'name': '盛达资源'},
        {'code': '000798', 'name': '中水渔业'},
        {'code': '600000', 'name': '浦发银行'},
        {'code': '600036', 'name': '招商银行'},
        {'code': '600519', 'name': '贵州茅台'},
        {'code': '600887', 'name': '伊利股份'},
        {'code': '601318', 'name': '中国平安'}
    ]
    
    # 保存到监控目录
    manager = AutoFileManager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_stocks_{timestamp}.csv"
    filepath = os.path.join(manager.watch_directory, filename)
    
    df = pd.DataFrame(test_data)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"✅ 测试文件已创建: {filepath}")
    return filepath

def test_auto_file_manager():
    """测试自动文件管理器"""
    print("\n🔍 测试自动文件管理器...")
    
    # 创建测试文件
    test_file = create_test_stock_file()
    
    try:
        # 运行自动更新
        manager = AutoFileManager()
        result = manager.auto_update()
        
        if result['updated']:
            print(f"✅ 自动更新成功: {result['new_files']}")
            return True
        else:
            print(f"❌ 自动更新失败: {result['errors']}")
            return False
            
    except Exception as e:
        print(f"❌ 自动文件管理器测试失败: {e}")
        return False

def test_stock_matching():
    """测试股票匹配功能"""
    print("\n🔍 测试股票匹配功能...")
    
    try:
        from stock_name_matcher import StockNameMatcher
        
        # 创建匹配器
        matcher = StockNameMatcher(api_source='local')
        
        # 测试几个股票代码
        test_codes = ['000001', '000037', '600000', '600036']
        success_count = 0
        
        for code in test_codes:
            result = matcher.match_stock_code(code)
            if result and result.get('匹配状态') == '匹配成功':
                print(f"  ✅ {code}: {result.get('股票名称')}")
                success_count += 1
            else:
                print(f"  ❌ {code}: {result.get('匹配状态', '匹配失败')}")
        
        success_rate = success_count / len(test_codes) * 100
        print(f"📊 匹配成功率: {success_rate:.1f}% ({success_count}/{len(test_codes)})")
        
        return success_rate >= 80  # 80%以上算成功
        
    except Exception as e:
        print(f"❌ 股票匹配测试失败: {e}")
        return False

def test_web_api():
    """测试Web API"""
    print("\n🔍 测试Web API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试API状态
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API状态正常: {data.get('stock_count', 0)} 只股票")
        else:
            print(f"❌ API状态异常: {response.status_code}")
            return False
        
        # 测试股票数据状态
        response = requests.get(f"{base_url}/api/stock_data_status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 股票数据状态正常: {data['current_data']['total_stocks']} 只股票")
        else:
            print(f"❌ 股票数据状态异常: {response.status_code}")
            return False
        
        # 测试单个股票匹配
        response = requests.get(f"{base_url}/api/test_match/000001", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('match_result', {}).get('匹配状态') == '匹配成功':
                print(f"✅ 单个匹配测试成功: 000001 -> {data['match_result']['股票名称']}")
            else:
                print(f"❌ 单个匹配测试失败: {data.get('match_result', {}).get('匹配状态', '未知')}")
                return False
        else:
            print(f"❌ 单个匹配测试异常: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Web API测试失败: {e}")
        print("💡 请确保Web应用正在运行 (python app.py)")
        return False

def test_performance():
    """测试性能"""
    print("\n🔍 测试性能...")
    
    try:
        from stock_name_matcher import StockNameMatcher
        
        # 创建匹配器
        matcher = StockNameMatcher(api_source='local')
        
        # 测试批量匹配性能
        test_codes = ['000001', '000002', '000037', '600000', '600036'] * 10  # 50个代码
        
        start_time = time.time()
        success_count = 0
        
        for code in test_codes:
            result = matcher.match_stock_code(code)
            if result and result.get('匹配状态') == '匹配成功':
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(test_codes)
        
        print(f"📊 性能测试结果:")
        print(f"  总数: {len(test_codes)} 个代码")
        print(f"  成功: {success_count} 个")
        print(f"  总耗时: {total_time:.3f} 秒")
        print(f"  平均耗时: {avg_time:.3f} 秒/个")
        print(f"  成功率: {success_count/len(test_codes)*100:.1f}%")
        
        # 性能标准：平均每个代码处理时间小于0.1秒
        return avg_time < 0.1
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 完整系统测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("自动文件管理器", test_auto_file_manager),
        ("股票匹配功能", test_stock_matching),
        ("性能测试", test_performance),
        ("Web API", test_web_api)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False
    
    # 总结
    print(f"\n{'='*50}")
    print("📋 测试总结:")
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    print(f"\n🎯 总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！系统运行正常")
        print("\n💡 使用说明:")
        print("  1. 将新的股票数据CSV文件放入 'new_stock_files' 目录")
        print("  2. 通过Web界面上传文件或运行 'python auto_file_manager.py'")
        print("  3. 系统会自动处理并更新股票数据")
        print("  4. 在Web界面中上传要处理的文件进行股票匹配")
    else:
        print("⚠️  部分测试失败，请检查配置")
        
        if not results.get("Web API", True):
            print("\n🔧 Web API测试失败的可能原因:")
            print("  - Web应用未启动，请运行: python app.py")
            print("  - 端口5000被占用")
            print("  - 防火墙阻止了连接")

if __name__ == '__main__':
    main()
