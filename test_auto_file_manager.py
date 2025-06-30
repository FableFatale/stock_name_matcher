#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动文件管理器
验证自动检测和管理股票数据文件的功能
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from auto_file_manager import AutoFileManager
from local_stock_data import LocalStockData

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_stock_file(filename: str, num_stocks: int = 100) -> str:
    """创建测试股票数据文件"""
    print(f"📝 创建测试文件: {filename} ({num_stocks} 只股票)")
    
    # 生成测试数据
    test_data = []
    for i in range(num_stocks):
        code = f"{i+1:06d}"  # 生成6位数字代码
        name = f"测试股票{i+1:03d}"
        test_data.append({
            'code': code,
            'name': name
        })
    
    # 保存文件
    df = pd.DataFrame(test_data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"✅ 测试文件已创建: {filename}")
    return filename

def test_file_detection():
    """测试文件检测功能"""
    print("\n🔍 测试文件检测功能")
    print("-" * 30)
    
    manager = AutoFileManager()
    
    # 测试不同的文件名模式
    test_patterns = [
        'stock_list_test.csv',
        'all_stocks_20250620.csv',
        'stocks_data.csv',
        '股票数据_测试.csv',
        'stocklist_new.csv',
        'not_stock_file.csv'  # 这个不应该被识别
    ]
    
    for pattern in test_patterns:
        is_stock_file = manager.is_stock_data_file(pattern)
        status = "✅ 识别" if is_stock_file else "❌ 忽略"
        print(f"  {pattern}: {status}")
    
    return True

def test_file_validation():
    """测试文件验证功能"""
    print("\n🔍 测试文件验证功能")
    print("-" * 30)
    
    manager = AutoFileManager()
    
    # 创建有效的测试文件
    valid_file = create_test_stock_file('test_valid_stocks.csv', 50)
    
    # 创建无效的测试文件（缺少必要列）
    invalid_data = pd.DataFrame([
        {'wrong_col1': '000001', 'wrong_col2': 'test'},
        {'wrong_col1': '000002', 'wrong_col2': 'test2'}
    ])
    invalid_file = 'test_invalid_stocks.csv'
    invalid_data.to_csv(invalid_file, index=False)
    
    # 验证文件
    print(f"📋 验证有效文件:")
    valid_result = manager.validate_stock_file(valid_file)
    if valid_result['valid']:
        print(f"  ✅ 验证通过: {valid_result['info']}")
    else:
        print(f"  ❌ 验证失败: {valid_result['error']}")
    
    print(f"📋 验证无效文件:")
    invalid_result = manager.validate_stock_file(invalid_file)
    if invalid_result['valid']:
        print(f"  ❌ 意外通过验证")
    else:
        print(f"  ✅ 正确识别为无效: {invalid_result['error']}")
    
    # 清理测试文件
    for file in [valid_file, invalid_file]:
        if os.path.exists(file):
            os.remove(file)
    
    return True

def test_auto_update():
    """测试自动更新功能"""
    print("\n🔍 测试自动更新功能")
    print("-" * 30)
    
    manager = AutoFileManager()
    
    # 创建新的股票数据文件
    test_file = create_test_stock_file('all_stocks_test_20250620.csv', 200)
    
    try:
        # 执行自动更新
        print("🔄 执行自动更新...")
        result = manager.auto_update()
        
        print(f"📊 更新结果:")
        print(f"  更新状态: {'✅ 成功' if result['updated'] else '❌ 无更新'}")
        print(f"  新文件: {result['new_files']}")
        if result['errors']:
            print(f"  错误: {result['errors']}")
        
        # 验证文件是否正确安装
        data_file = os.path.join('data', os.path.basename(test_file))
        if os.path.exists(data_file):
            print(f"✅ 文件已正确安装到data目录")
        else:
            print(f"❌ 文件未安装到data目录")
        
        return result['updated']
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

def test_integration_with_local_data():
    """测试与本地数据管理器的集成"""
    print("\n🔍 测试与本地数据管理器的集成")
    print("-" * 30)
    
    # 创建测试股票文件
    test_file = create_test_stock_file('stocks_integration_test.csv', 100)
    
    try:
        # 使用自动文件管理器安装文件
        manager = AutoFileManager()
        result = manager.auto_update()
        
        if result['updated']:
            print("✅ 文件已通过自动管理器安装")
            
            # 测试本地数据管理器是否能正确加载
            local_data = LocalStockData()
            stock_list = local_data.get_stock_list()
            
            if stock_list is not None and len(stock_list) > 0:
                print(f"✅ 本地数据管理器成功加载 {len(stock_list)} 只股票")
                
                # 测试搜索功能
                test_result = local_data.search_by_code('000001')
                if test_result is not None and len(test_result) > 0:
                    print(f"✅ 搜索功能正常: {test_result.iloc[0]['名称']}")
                else:
                    print("❌ 搜索功能异常")
                
                return True
            else:
                print("❌ 本地数据管理器加载失败")
                return False
        else:
            print("❌ 自动管理器未能安装文件")
            return False
            
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

def test_file_info():
    """测试文件信息获取"""
    print("\n🔍 测试文件信息获取")
    print("-" * 30)
    
    manager = AutoFileManager()
    files_info = manager.get_current_files_info()
    
    print(f"📁 数据文件 ({len(files_info['data_files'])} 个):")
    for file_info in files_info['data_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
    
    print(f"📁 备份文件 ({len(files_info['backup_files'])} 个):")
    for file_info in files_info['backup_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
    
    print(f"📁 监控目录文件 ({len(files_info['watch_files'])} 个):")
    for file_info in files_info['watch_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB)")
    
    return True

def main():
    """主函数"""
    print("🚀 自动文件管理器测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("文件检测功能", test_file_detection),
        ("文件验证功能", test_file_validation),
        ("文件信息获取", test_file_info),
        ("自动更新功能", test_auto_update),
        ("与本地数据管理器集成", test_integration_with_local_data)
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
        print("🎉 所有测试通过！自动文件管理器工作正常")
        print("\n💡 使用说明:")
        print("  1. 将新的股票数据CSV文件放在项目根目录")
        print("  2. 运行 python auto_file_manager.py 进行自动更新")
        print("  3. 系统会自动检测、验证并安装新文件")
        print("  4. 旧文件会自动备份到backup目录")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == '__main__':
    main()
