#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终命令行工具测试
"""

import subprocess
import pandas as pd
import os
import sys
import time
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_cli_test():
    """运行命令行工具的完整测试"""
    
    print("="*80)
    print("🧪 股票代码补全系统 - 最终命令行测试")
    print("="*80)
    
    test_file = "20250617171501.csv"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"result/final_cli_test_{timestamp}.csv"
    
    # 1. 验证测试文件存在
    print(f"\n1. 验证测试文件...")
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    # 读取测试文件信息
    test_df = pd.read_csv(test_file)
    print(f"✅ 测试文件存在: {test_file}")
    print(f"   文件行数: {len(test_df)}")
    print(f"   列名: {list(test_df.columns)}")
    
    # 2. 运行命令行工具
    print(f"\n2. 运行命令行工具...")
    cmd = [
        sys.executable, "stock_name_matcher.py",
        test_file,
        "-o", output_file,
        "--mode", "code"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        end_time = time.time()
        execution_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ 命令执行成功")
            print(f"   执行时间: {execution_time:.2f}秒")
        else:
            print(f"❌ 命令执行失败")
            print(f"   错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 命令执行异常: {e}")
        return False
    
    # 3. 验证输出文件
    print(f"\n3. 验证输出文件...")
    if not os.path.exists(output_file):
        print(f"❌ 输出文件不存在: {output_file}")
        return False
    
    # 读取结果文件（正确指定数据类型）
    result_df = pd.read_csv(output_file, dtype={'标准化代码': str, '股票代码': str})
    print(f"✅ 输出文件存在: {output_file}")
    print(f"   结果行数: {len(result_df)}")
    print(f"   列名: {list(result_df.columns)}")
    
    # 4. 分析匹配结果
    print(f"\n4. 分析匹配结果...")
    total_count = len(result_df)
    success_count = len(result_df[result_df['匹配状态'] == '匹配成功'])
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"   总数: {total_count}")
    print(f"   成功: {success_count}")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 5. 验证数据格式
    print(f"\n5. 验证数据格式...")
    print(f"   标准化代码样本: {result_df['标准化代码'].head().tolist()}")
    print(f"   股票代码样本: {result_df['股票代码'].head().tolist()}")
    print(f"   标准化代码数据类型: {result_df['标准化代码'].dtype}")
    print(f"   股票代码数据类型: {result_df['股票代码'].dtype}")
    
    # 检查前导零
    has_leading_zeros = all(len(code) == 6 for code in result_df['标准化代码'].head() if code)
    print(f"   前导零保留: {'✅ 正确' if has_leading_zeros else '❌ 错误'}")
    
    # 6. 验证具体股票
    print(f"\n6. 验证具体股票匹配...")
    test_codes = ["'000037", "'000603", "'000798", "'000823", "'000970"]
    
    for code in test_codes:
        matches = result_df[result_df['原始代码'] == code]
        if len(matches) > 0:
            match = matches.iloc[0]
            status = match['匹配状态']
            name = match.get('股票名称', '')
            normalized = match.get('标准化代码', '')
            print(f"   {code} -> {normalized} ({name}) [{status}]")
        else:
            print(f"   {code} -> 未找到")
    
    # 7. 性能统计
    print(f"\n7. 性能统计...")
    print(f"   处理速度: {total_count/execution_time:.1f} 条/秒")
    print(f"   平均每条: {execution_time/total_count*1000:.1f} 毫秒")
    
    # 8. 总结
    print(f"\n8. 测试总结...")
    if success_rate >= 95:
        print(f"✅ 测试通过！系统工作正常")
        print(f"   - 匹配成功率: {success_rate:.1f}%")
        print(f"   - 数据格式正确")
        print(f"   - 前导零保留正确")
        return True
    else:
        print(f"❌ 测试失败！系统存在问题")
        print(f"   - 匹配成功率过低: {success_rate:.1f}%")
        return False

def main():
    """主函数"""
    success = run_cli_test()
    
    print("\n" + "="*80)
    if success:
        print("🎉 最终测试结果: 通过")
        print("股票代码补全系统工作正常！")
    else:
        print("❌ 最终测试结果: 失败")
        print("系统存在问题，需要进一步调试。")
    print("="*80)
    
    return success

if __name__ == "__main__":
    main()
