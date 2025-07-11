#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票名称匹配器快速开始脚本
演示基本功能和使用方法
"""

import os
import sys
import pandas as pd
from datetime import datetime

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 股票名称匹配器 - 快速开始")
    print("=" * 60)
    print("这个脚本将演示如何使用股票名称匹配器")
    print("从Excel/CSV文件中匹配A股股票信息")
    print("=" * 60)

def check_dependencies():
    """检查依赖是否安装"""
    print("\n📋 检查依赖...")
    
    required_modules = [
        'pandas',
        'akshare', 
        'fuzzywuzzy',
        'openpyxl'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - 未安装")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺少依赖: {', '.join(missing_modules)}")
        print("请运行以下命令安装：")
        print("python install_dependencies.py")
        print("或者：")
        print("pip install pandas akshare fuzzywuzzy python-Levenshtein openpyxl")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def create_sample_data():
    """创建示例数据"""
    print("\n📝 创建示例数据...")
    
    # 创建示例股票数据
    sample_data = {
        '股票名称': [
            '平安银行',
            '招商银行',
            '中国平安',
            '贵州茅台',
            '五粮液',
            '美的集团',
            '格力电器',
            '比亚迪',
            '宁德时代',
            '中国移动',
            '工商银行',
            '建设银行',
            '中石油',
            '中石化',
            '紫金矿业',
            '茅台',  # 简称测试
            '招行',  # 简称测试
            '平安',  # 简称测试
            '不存在的股票',  # 测试无匹配情况
            'ST股票'  # 测试特殊情况
        ],
        '参考价格': [
            10.45, 35.20, 45.80, 1680.50, 120.30,
            58.90, 32.40, 245.60, 185.20, 78.90,
            4.85, 6.20, 7.20, 5.60, 12.80,
            1680.00, 35.00, 45.00, 100.00, 5.50
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # 保存为CSV文件
    csv_file = "quick_start_sample.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✅ 示例数据已保存到: {csv_file}")
    
    # 保存为Excel文件
    excel_file = "quick_start_sample.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"✅ 示例数据已保存到: {excel_file}")
    
    return csv_file, excel_file

def run_matcher_demo(input_file):
    """运行匹配器演示"""
    print(f"\n🔍 运行股票名称匹配演示...")
    print(f"输入文件: {input_file}")
    
    try:
        # 导入股票匹配器
        from stock_name_matcher import StockNameMatcher
        
        # 创建匹配器实例
        print("正在初始化匹配器...")
        matcher = StockNameMatcher()
        
        # 处理文件
        print("正在处理文件...")
        output_file = matcher.process_excel_file(input_file)
        
        print(f"✅ 匹配完成！结果已保存到: {output_file}")
        
        # 读取并显示结果摘要
        result_df = pd.read_csv(output_file)
        
        print("\n📊 匹配结果摘要:")
        print(f"  总股票数: {len(result_df)}")
        print(f"  成功匹配: {len(result_df[result_df['匹配股票代码'] != ''])}")
        print(f"  精确匹配: {len(result_df[result_df['匹配类型'] == '精确匹配'])}")
        print(f"  模糊匹配: {len(result_df[result_df['匹配类型'] == '模糊匹配'])}")
        print(f"  包含匹配: {len(result_df[result_df['匹配类型'] == '包含匹配'])}")
        print(f"  未匹配: {len(result_df[result_df['匹配股票代码'] == ''])}")
        
        # 显示前几个匹配结果
        print("\n📋 前5个匹配结果:")
        display_columns = ['原始名称', '匹配股票代码', '匹配股票名称', '匹配类型', '匹配度']
        print(result_df[display_columns].head().to_string(index=False))
        
        return output_file
        
    except ImportError:
        print("❌ 无法导入股票匹配器模块")
        print("请确保 stock_name_matcher.py 文件存在")
        return None
    except Exception as e:
        print(f"❌ 运行匹配器时出错: {e}")
        return None

def show_usage_examples():
    """显示使用示例"""
    print("\n📚 使用示例:")
    print("\n1. 基本用法:")
    print("   python stock_name_matcher.py input_file.xlsx")
    
    print("\n2. 指定输出文件:")
    print("   python stock_name_matcher.py input_file.xlsx -o results.csv")
    
    print("\n3. 指定列名:")
    print("   python stock_name_matcher.py input_file.xlsx -n '股票名称' -p '价格'")
    
    print("\n4. 运行测试:")
    print("   python test_stock_matcher.py")
    
    print("\n5. 查看帮助:")
    print("   python stock_name_matcher.py --help")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 创建示例数据
    csv_file, excel_file = create_sample_data()
    
    # 运行演示
    result_file = run_matcher_demo(csv_file)
    
    if result_file:
        print("\n🎉 演示完成！")
        print(f"\n📁 生成的文件:")
        print(f"  输入文件: {csv_file}")
        print(f"  输出文件: {result_file}")
        
        # 显示使用示例
        show_usage_examples()
        
        print(f"\n📖 更多信息请查看:")
        print("  股票名称匹配器使用说明.md")
        
        return 0
    else:
        print("\n❌ 演示失败")
        print("请检查错误信息并重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
