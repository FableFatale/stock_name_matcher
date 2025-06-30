#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT格式股票数据管理工具
用于管理和使用 all_stocks_20250616.txt 等TXT格式的股票列表
"""

import sys
import os
import argparse
import pandas as pd
import logging
from datetime import datetime
from local_stock_data import LocalStockData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_txt_files():
    """列出可用的TXT格式股票文件"""
    print("📁 查找TXT格式股票文件...")
    
    txt_files = []
    for filename in os.listdir("."):
        if filename.startswith("all_stocks_") and filename.endswith(".txt"):
            size = os.path.getsize(filename)
            mtime = os.path.getmtime(filename)
            txt_files.append({
                'name': filename,
                'size': size,
                'modified': mtime
            })
    
    if txt_files:
        print(f"✅ 找到 {len(txt_files)} 个TXT文件:")
        for file_info in txt_files:
            size_kb = file_info['size'] / 1024
            mod_time = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   - {file_info['name']} ({size_kb:.1f} KB, {mod_time})")
    else:
        print("❌ 未找到TXT格式股票文件")
    
    return txt_files

def analyze_txt_file(txt_file):
    """分析TXT文件内容"""
    print(f"\n📊 分析TXT文件: {txt_file}")
    print("-" * 50)
    
    if not os.path.exists(txt_file):
        print(f"❌ 文件不存在: {txt_file}")
        return False
    
    try:
        stock_count = 0
        valid_count = 0
        market_stats = {'沪市': 0, '深市': 0, '北交所': 0, '其他': 0}
        sample_stocks = []
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                stock_count += 1
                
                # 解析股票代码和名称
                if ',' in line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        name = parts[1].strip()
                        
                        # 验证股票代码格式
                        if len(code) == 6 and code.isdigit():
                            valid_count += 1
                            
                            # 统计市场分布
                            if code.startswith(('600', '601', '603', '605', '688')):
                                market_stats['沪市'] += 1
                            elif code.startswith(('000', '001', '002', '003', '300')):
                                market_stats['深市'] += 1
                            elif code.startswith(('8', '4')):
                                market_stats['北交所'] += 1
                            else:
                                market_stats['其他'] += 1
                            
                            # 收集样本
                            if len(sample_stocks) < 10:
                                sample_stocks.append((code, name))
        
        # 显示分析结果
        print(f"✅ 文件分析完成!")
        print(f"✅ 总行数: {line_num:,}")
        print(f"✅ 股票条目: {stock_count:,}")
        print(f"✅ 有效股票: {valid_count:,}")
        
        print(f"\n📈 市场分布:")
        for market, count in market_stats.items():
            if count > 0:
                percentage = (count / valid_count) * 100 if valid_count > 0 else 0
                print(f"   - {market}: {count:,} 只 ({percentage:.1f}%)")
        
        print(f"\n📋 样本股票 (前10只):")
        for code, name in sample_stocks:
            print(f"   - {code}: {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析文件时发生错误: {str(e)}")
        return False

def convert_txt_to_csv(txt_file, output_file=None):
    """将TXT文件转换为CSV格式"""
    print(f"\n🔄 转换TXT文件为CSV格式...")
    print(f"输入文件: {txt_file}")
    
    try:
        # 使用LocalStockData的转换功能
        stock_data = LocalStockData()
        
        if output_file is None:
            base_name = os.path.splitext(txt_file)[0]
            output_file = f"{base_name}_converted.csv"
        
        print(f"输出文件: {output_file}")
        
        success = stock_data.convert_txt_to_csv(txt_file, output_file)
        
        if success and os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ 转换成功!")
            print(f"✅ 输出文件: {output_file}")
            print(f"✅ 文件大小: {size:,} 字节")
            return True
        else:
            print(f"❌ 转换失败")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中发生错误: {str(e)}")
        return False

def test_stock_search(txt_file):
    """测试股票搜索功能"""
    print(f"\n🔍 测试股票搜索功能...")
    
    try:
        # 临时加载TXT数据进行测试
        stock_data = LocalStockData()
        data = stock_data._load_txt_stock_data(txt_file)
        
        if data is None or data.empty:
            print(f"❌ 无法加载TXT文件数据")
            return False
        
        print(f"✅ 数据加载成功，共 {len(data):,} 只股票")
        
        # 测试代码搜索
        test_codes = ['000001', '600036', '300059', '688001']
        print(f"\n📋 测试代码搜索:")
        for code in test_codes:
            result = data[data['代码'] == code]
            if not result.empty:
                name = result.iloc[0]['名称']
                print(f"   ✅ {code}: {name}")
            else:
                print(f"   ❌ {code}: 未找到")
        
        # 测试名称搜索
        test_names = ['平安银行', '万科', '中兴通讯']
        print(f"\n📋 测试名称搜索:")
        for name in test_names:
            result = data[data['名称'].str.contains(name, na=False)]
            if not result.empty:
                code = result.iloc[0]['代码']
                full_name = result.iloc[0]['名称']
                print(f"   ✅ {name}: {code} ({full_name})")
            else:
                print(f"   ❌ {name}: 未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试搜索功能时发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TXT格式股票数据管理工具')
    parser.add_argument('--list', action='store_true', help='列出可用的TXT文件')
    parser.add_argument('--analyze', help='分析指定的TXT文件')
    parser.add_argument('--convert', help='将TXT文件转换为CSV格式')
    parser.add_argument('--output', '-o', help='指定输出文件名（用于转换）')
    parser.add_argument('--test', help='测试指定TXT文件的搜索功能')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📈 TXT格式股票数据管理工具")
    print("=" * 60)
    
    # 如果没有参数，显示帮助信息
    if not any(vars(args).values()):
        # 自动列出文件并分析第一个找到的文件
        txt_files = list_txt_files()
        
        if txt_files:
            # 选择最新的文件进行分析
            latest_file = max(txt_files, key=lambda x: x['modified'])
            txt_file = latest_file['name']
            
            print(f"\n🎯 自动选择最新文件进行分析: {txt_file}")
            analyze_txt_file(txt_file)
            test_stock_search(txt_file)
        else:
            print("\n💡 使用说明:")
            print("   python txt_stock_manager.py --list              # 列出TXT文件")
            print("   python txt_stock_manager.py --analyze FILE      # 分析TXT文件")
            print("   python txt_stock_manager.py --convert FILE      # 转换为CSV")
            print("   python txt_stock_manager.py --test FILE         # 测试搜索功能")
        
        return 0
    
    success = True
    
    if args.list:
        list_txt_files()
    
    if args.analyze:
        success &= analyze_txt_file(args.analyze)
    
    if args.convert:
        success &= convert_txt_to_csv(args.convert, args.output)
    
    if args.test:
        success &= test_stock_search(args.test)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 操作完成!")
    else:
        print("❌ 操作过程中出现错误!")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
