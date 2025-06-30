#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细验证股票匹配结果
"""

import pandas as pd
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_results():
    """验证匹配结果的详细信息"""
    
    # 读取命令行和Web界面的结果
    cli_file = "result/test_cli_20250618_103705.csv"
    web_file = "result/stock_completion_20250618_103743.csv"
    
    try:
        cli_df = pd.read_csv(cli_file)
        web_df = pd.read_csv(web_file)
        
        print("="*80)
        print("📊 详细验证股票匹配结果")
        print("="*80)
        
        # 基本统计
        print(f"\n📋 基本统计:")
        print(f"命令行结果: {len(cli_df)} 条记录")
        print(f"Web界面结果: {len(web_df)} 条记录")
        
        cli_success = len(cli_df[cli_df['匹配状态'] == '匹配成功'])
        web_success = len(web_df[web_df['匹配状态'] == '匹配成功'])
        
        print(f"命令行成功: {cli_success}/{len(cli_df)} ({cli_success/len(cli_df)*100:.1f}%)")
        print(f"Web界面成功: {web_success}/{len(web_df)} ({web_success/len(web_df)*100:.1f}%)")
        
        # 检查具体的股票代码匹配
        print(f"\n🔍 检查前10个股票的匹配结果:")
        print("-"*80)
        print(f"{'原始代码':<12} {'CLI匹配':<8} {'Web匹配':<8} {'CLI股票名称':<12} {'Web股票名称':<12} {'一致性'}")
        print("-"*80)
        
        consistent_count = 0
        total_count = min(len(cli_df), len(web_df))
        
        for i in range(min(10, total_count)):
            cli_row = cli_df.iloc[i]
            web_row = web_df.iloc[i]
            
            cli_code = cli_row['原始代码']
            web_code = web_row['原始代码']
            
            cli_status = cli_row['匹配状态']
            web_status = web_row['匹配状态']
            
            cli_name = cli_row.get('股票名称', 'N/A')
            web_name = web_row.get('股票名称', 'N/A')
            
            consistent = (cli_code == web_code and 
                         cli_status == web_status and 
                         cli_name == web_name)
            
            if consistent:
                consistent_count += 1
            
            status_icon = "✅" if consistent else "❌"
            
            print(f"{cli_code:<12} {cli_status:<8} {web_status:<8} {cli_name:<12} {web_name:<12} {status_icon}")
        
        # 全面一致性检查
        print(f"\n📈 全面一致性检查:")
        all_consistent = 0
        
        for i in range(total_count):
            cli_row = cli_df.iloc[i]
            web_row = web_df.iloc[i]
            
            if (cli_row['原始代码'] == web_row['原始代码'] and
                cli_row['匹配状态'] == web_row['匹配状态'] and
                cli_row.get('股票名称', '') == web_row.get('股票名称', '')):
                all_consistent += 1
        
        consistency_rate = (all_consistent / total_count) * 100 if total_count > 0 else 0
        print(f"一致性: {all_consistent}/{total_count} ({consistency_rate:.1f}%)")
        
        # 检查特定的问题股票代码
        print(f"\n🎯 检查您提到的问题股票代码:")
        problem_codes = ["'000037", "'000603", "'000798", "'000823", "'000970", "'000985"]
        
        for code in problem_codes:
            cli_match = cli_df[cli_df['原始代码'] == code]
            web_match = web_df[web_df['原始代码'] == code]
            
            if len(cli_match) > 0 and len(web_match) > 0:
                cli_result = cli_match.iloc[0]
                web_result = web_match.iloc[0]
                
                print(f"\n  {code}:")
                print(f"    CLI: {cli_result['匹配状态']} -> {cli_result.get('股票名称', 'N/A')}")
                print(f"    Web: {web_result['匹配状态']} -> {web_result.get('股票名称', 'N/A')}")
                print(f"    标准化代码 CLI: {cli_result.get('标准化代码', 'N/A')}")
                print(f"    标准化代码 Web: {web_result.get('标准化代码', 'N/A')}")
                
                if (cli_result['匹配状态'] == web_result['匹配状态'] and
                    cli_result.get('股票名称', '') == web_result.get('股票名称', '')):
                    print(f"    状态: ✅ 一致")
                else:
                    print(f"    状态: ❌ 不一致")
            else:
                print(f"  {code}: ❌ 在结果中未找到")
        
        # 总结
        print(f"\n🎉 验证总结:")
        if consistency_rate >= 99.0:
            print(f"✅ 系统工作正常！命令行和Web界面结果高度一致 ({consistency_rate:.1f}%)")
        elif consistency_rate >= 90.0:
            print(f"⚠️ 系统基本正常，但存在少量差异 ({consistency_rate:.1f}%)")
        else:
            print(f"❌ 系统存在问题，结果不一致 ({consistency_rate:.1f}%)")
        
        print("="*80)
        
    except Exception as e:
        logger.error(f"验证过程出错: {e}")

if __name__ == "__main__":
    verify_results()
