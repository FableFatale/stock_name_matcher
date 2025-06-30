#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的股票数据文件加载
验证 all_stocks_20250620.csv 是否能正确加载和使用
"""

import os
import sys
import logging
from local_stock_data import LocalStockData
from stock_name_matcher import StockNameMatcher

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_local_stock_data():
    """测试本地股票数据加载"""
    print("🔍 测试本地股票数据加载...")
    
    try:
        # 创建本地数据管理器
        local_data = LocalStockData()
        
        # 获取数据信息
        data_info = local_data.get_data_info()
        print(f"📊 数据信息:")
        for key, value in data_info.items():
            print(f"  {key}: {value}")
        
        # 获取股票列表
        stock_list = local_data.get_stock_list()
        if stock_list is not None and len(stock_list) > 0:
            print(f"\n✅ 成功加载 {len(stock_list)} 只股票")
            print(f"📋 列名: {list(stock_list.columns)}")
            print(f"📄 前5条数据:")
            print(stock_list.head())
            
            # 测试一些关键股票代码
            test_codes = ['000001', '000037', '000603', '000798', '600000', '600036']
            print(f"\n🧪 测试关键股票代码:")
            for code in test_codes:
                result = local_data.search_by_code(code)
                if result is not None and len(result) > 0:
                    stock_info = result.iloc[0]
                    print(f"  ✅ {code}: {stock_info['名称']}")
                else:
                    print(f"  ❌ {code}: 未找到")
            
            return True
        else:
            print("❌ 未能加载股票数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_stock_matcher():
    """测试股票匹配器"""
    print("\n🔍 测试股票匹配器...")
    
    try:
        # 创建匹配器
        matcher = StockNameMatcher(api_source='local')
        
        # 测试股票代码匹配
        test_codes = ['000001', '000037', '000603', '600000', '600036']
        print(f"🧪 测试股票代码匹配:")
        
        for code in test_codes:
            result = matcher.match_stock_code(code)
            if result and result.get('匹配状态') == '匹配成功':
                print(f"  ✅ {code}: {result.get('股票名称', '未知')} - {result.get('匹配状态')}")
            else:
                print(f"  ❌ {code}: {result.get('匹配状态', '匹配失败')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票匹配器测试失败: {e}")
        return False

def test_data_files():
    """测试数据文件检测"""
    print("\n🔍 检测可用的数据文件...")
    
    try:
        local_data = LocalStockData()
        files_info = local_data.get_available_data_files()
        
        print(f"📁 CSV文件:")
        for file_info in files_info['csv_files']:
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
        
        print(f"📁 TXT文件:")
        for file_info in files_info['txt_files']:
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
        
        if files_info['recommended']:
            print(f"🎯 推荐使用: {files_info['recommended']['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据文件检测失败: {e}")
        return False

def test_performance():
    """测试性能"""
    print("\n⚡ 测试匹配性能...")
    
    try:
        import time
        matcher = StockNameMatcher(api_source='local')
        
        # 测试批量匹配
        test_codes = ['000001', '000002', '000037', '000603', '000798'] * 10  # 50个代码
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def check_file_exists():
    """检查新的股票数据文件是否存在"""
    print("📁 检查股票数据文件...")
    
    target_file = "all_stocks_20250620.csv"
    if os.path.exists(target_file):
        size = os.path.getsize(target_file)
        size_mb = size / (1024 * 1024)
        print(f"✅ 找到文件: {target_file} ({size_mb:.2f} MB)")
        
        # 检查文件内容
        try:
            import pandas as pd
            df = pd.read_csv(target_file, nrows=5)
            print(f"📋 文件列名: {list(df.columns)}")
            print(f"📊 预览数据:")
            print(df)
            return True
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return False
    else:
        print(f"❌ 未找到文件: {target_file}")
        
        # 列出当前目录的相关文件
        print("📁 当前目录的股票数据文件:")
        for filename in os.listdir("."):
            if (filename.startswith("all_stocks_") or filename.startswith("stock_list_")) and filename.endswith((".csv", ".txt")):
                size = os.path.getsize(filename)
                size_mb = size / (1024 * 1024)
                print(f"  - {filename} ({size_mb:.2f} MB)")
        
        return False

def main():
    """主函数"""
    print("🚀 新股票数据文件测试")
    print("=" * 50)
    
    # 检查文件是否存在
    file_exists = check_file_exists()
    
    if not file_exists:
        print("\n⚠️  新的股票数据文件不存在，测试可能使用旧数据")
    
    # 运行测试
    tests = [
        ("数据文件检测", test_data_files),
        ("本地股票数据加载", test_local_stock_data),
        ("股票匹配器", test_stock_matcher),
        ("性能测试", test_performance)
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
        print("🎉 所有测试通过！新的股票数据已成功集成")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == '__main__':
    main()
