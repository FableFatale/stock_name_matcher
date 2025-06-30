#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stock_name_list 系统
验证新的股票数据管理系统是否正常工作
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
from auto_file_manager import AutoFileManager
from local_stock_data import LocalStockData
from stock_name_matcher import StockNameMatcher

def test_stock_name_list_directory():
    """测试 stock_name_list 目录"""
    print("🔍 测试 stock_name_list 目录...")
    
    # 检查目录是否存在
    if not os.path.exists("stock_name_list"):
        print("❌ stock_name_list 目录不存在")
        return False
    
    # 检查是否有CSV文件
    csv_files = [f for f in os.listdir("stock_name_list") if f.endswith('.csv')]
    if not csv_files:
        print("❌ stock_name_list 目录中没有CSV文件")
        return False
    
    print(f"✅ 找到 {len(csv_files)} 个CSV文件:")
    for file in csv_files:
        filepath = os.path.join("stock_name_list", file)
        size = os.path.getsize(filepath) / (1024 * 1024)
        print(f"  - {file} ({size:.2f} MB)")
    
    return True

def test_auto_file_manager():
    """测试自动文件管理器"""
    print("\n🔍 测试自动文件管理器...")
    
    try:
        manager = AutoFileManager()
        
        # 检查监控目录
        print(f"📁 监控目录: {manager.watch_directory}")
        
        # 扫描文件
        files = manager.scan_for_new_files()
        print(f"📊 扫描结果: {len(files)} 个文件")
        
        # 获取文件信息
        files_info = manager.get_current_files_info()
        print(f"📋 文件统计:")
        print(f"  - 监控目录: {len(files_info['watch_files'])} 个文件")
        print(f"  - 数据目录: {len(files_info['data_files'])} 个文件")
        print(f"  - 备份目录: {len(files_info['backup_files'])} 个文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 自动文件管理器测试失败: {e}")
        return False

def test_local_stock_data():
    """测试本地股票数据加载"""
    print("\n🔍 测试本地股票数据加载...")
    
    try:
        # 强制重新加载
        local_data = LocalStockData()
        local_data.stock_list = None  # 清除缓存
        
        # 获取股票列表
        stock_list = local_data.get_stock_list()
        
        if stock_list is None or len(stock_list) == 0:
            print("❌ 未能加载股票数据")
            return False
        
        # 获取数据信息
        data_info = local_data.get_data_info()
        
        print(f"✅ 成功加载 {len(stock_list)} 只股票")
        print(f"📊 数据统计:")
        print(f"  - 总股票数: {data_info.get('总股票数', 0)}")
        print(f"  - 数据源: {data_info.get('数据源', '未知')}")
        print(f"  - 市场分布: {data_info.get('市场分布', {})}")
        
        # 测试搜索功能
        test_codes = ['000001', '000037', '600000', '600036', '300001']
        success_count = 0
        
        print(f"🧪 测试搜索功能:")
        for code in test_codes:
            result = local_data.search_by_code(code)
            if result is not None and len(result) > 0:
                stock_name = result.iloc[0]['名称']
                print(f"  ✅ {code}: {stock_name}")
                success_count += 1
            else:
                print(f"  ❌ {code}: 未找到")
        
        success_rate = success_count / len(test_codes) * 100
        print(f"📈 搜索成功率: {success_rate:.1f}% ({success_count}/{len(test_codes)})")
        
        return success_rate >= 80  # 80%以上算成功
        
    except Exception as e:
        print(f"❌ 本地股票数据测试失败: {e}")
        return False

def test_stock_matching():
    """测试股票匹配功能"""
    print("\n🔍 测试股票匹配功能...")
    
    try:
        # 创建匹配器
        matcher = StockNameMatcher(api_source='local')
        
        # 测试股票代码
        test_codes = ['000001', '000037', '600000', '600036', '300001']
        success_count = 0
        
        print(f"🧪 测试股票匹配:")
        for code in test_codes:
            result = matcher.match_stock_code(code)
            if result and result.get('匹配状态') == '匹配成功':
                print(f"  ✅ {code}: {result.get('股票名称')} - {result.get('匹配状态')}")
                success_count += 1
            else:
                print(f"  ❌ {code}: {result.get('匹配状态', '匹配失败')}")
        
        success_rate = success_count / len(test_codes) * 100
        print(f"📈 匹配成功率: {success_rate:.1f}% ({success_count}/{len(test_codes)})")
        
        return success_rate >= 80  # 80%以上算成功
        
    except Exception as e:
        print(f"❌ 股票匹配测试失败: {e}")
        return False

def test_performance():
    """测试性能"""
    print("\n🔍 测试性能...")
    
    try:
        matcher = StockNameMatcher(api_source='local')
        
        # 测试批量匹配性能
        test_codes = ['000001', '000002', '000037', '600000', '600036'] * 20  # 100个代码
        
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
        print(f"  平均耗时: {avg_time:.4f} 秒/个")
        print(f"  成功率: {success_count/len(test_codes)*100:.1f}%")
        
        # 性能标准：平均每个代码处理时间小于0.01秒
        return avg_time < 0.01
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def create_test_stock_file():
    """创建测试股票文件"""
    print("\n📝 创建测试股票文件...")
    
    # 创建一个新的测试文件
    test_data = [
        {'code': '000001', 'name': '平安银行'},
        {'code': '000002', 'name': '万科A'},
        {'code': '600000', 'name': '浦发银行'},
        {'code': '600036', 'name': '招商银行'},
        {'code': '300001', 'name': '特锐德'}
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_stocks_{timestamp}.csv"
    filepath = os.path.join("stock_name_list", filename)
    
    df = pd.DataFrame(test_data)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"✅ 测试文件已创建: {filepath}")
    return filepath

def test_new_file_detection():
    """测试新文件检测"""
    print("\n🔍 测试新文件检测...")
    
    try:
        # 创建测试文件
        test_file = create_test_stock_file()
        
        # 测试自动文件管理器是否能检测到
        manager = AutoFileManager()
        new_files = manager.scan_for_new_files()
        
        if new_files:
            print(f"✅ 检测到新文件: {[os.path.basename(f) for f in new_files]}")
            
            # 测试自动更新
            result = manager.auto_update()
            if result['updated']:
                print(f"✅ 自动更新成功: {result['new_files']}")
                return True
            else:
                print(f"❌ 自动更新失败: {result['errors']}")
                return False
        else:
            print("❌ 未检测到新文件")
            return False
            
    except Exception as e:
        print(f"❌ 新文件检测测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        try:
            if 'test_file' in locals() and os.path.exists(test_file):
                os.remove(test_file)
                print(f"🗑️ 已清理测试文件: {test_file}")
        except:
            pass

def main():
    """主函数"""
    print("🚀 stock_name_list 系统测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("stock_name_list 目录", test_stock_name_list_directory),
        ("自动文件管理器", test_auto_file_manager),
        ("本地股票数据加载", test_local_stock_data),
        ("股票匹配功能", test_stock_matching),
        ("性能测试", test_performance),
        ("新文件检测", test_new_file_detection)
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
        print("🎉 所有测试通过！stock_name_list 系统运行正常")
        print("\n💡 使用说明:")
        print("  1. 将新的股票数据CSV文件放入 'stock_name_list' 目录")
        print("  2. 系统会自动使用最新的文件")
        print("  3. 支持任何包含 'code' 和 'name' 列的CSV文件")
        print("  4. 通过Web界面可以手动触发更新")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == '__main__':
    main()
