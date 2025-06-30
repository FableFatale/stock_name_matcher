#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强功能：
1. 处理被引号包裹的股票代码
2. 多数据源交叉验证
"""

import sys
import os
# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from stock_name_matcher import StockNameMatcher

def test_quoted_codes():
    """测试被引号包裹的股票代码处理"""
    print("=== 测试被引号包裹的股票代码处理 ===")
    
    # 创建测试数据
    test_data = {
        '股票代码': ["'852'", '"2208"', "'3018'", "688001", "'301223'"],
        '入选价格': [6.87, 8.47, 20.38, 45.67, 12.36]
    }
    
    test_df = pd.DataFrame(test_data)
    test_file = "test_quoted_codes.csv"
    test_df.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    print(f"创建测试文件: {test_file}")
    print("测试数据:")
    print(test_df)
    
    # 测试匹配器
    matcher = StockNameMatcher(api_source='local')  # 使用本地数据源
    
    print("\n=== 测试代码标准化 ===")
    for code in test_data['股票代码']:
        normalized = matcher._normalize_stock_code(code)
        valid = matcher._validate_stock_code(normalized)  # 使用标准化后的代码验证
        print(f"原始: {code:10} -> 标准化: {normalized:6} -> 有效: {valid}")
    
    return test_file

def test_cross_validation():
    """测试多数据源交叉验证"""
    print("\n=== 测试多数据源交叉验证 ===")
    
    matcher = StockNameMatcher(api_source='local')
    
    # 测试几个知名股票代码
    test_codes = ['000001', '600036', '000852']
    
    for code in test_codes:
        print(f"\n测试股票代码: {code}")
        
        # 先获取基础信息
        basic_result = matcher.match_stock_code(code, enable_cross_validation=False)
        if basic_result.get('匹配状态') == '匹配成功':
            stock_name = basic_result['股票名称']
            print(f"基础匹配: {stock_name}")
            
            # 进行交叉验证
            print("开始交叉验证...")
            validation_result = matcher.cross_validate_stock_info(code, stock_name)
            
            print(f"验证结果:")
            print(f"  置信度: {validation_result['confidence_score']:.1f}%")
            print(f"  名称一致性: {validation_result['name_consistency']:.1f}%")
            print(f"  找到的数据源数: {validation_result['found_count']}")
            print(f"  推荐名称: {validation_result['most_common_name']}")
            
            # 显示各数据源的验证结果
            for api_source, result in validation_result['validation_results'].items():
                status = "✓" if result.get('found', False) else "✗"
                name_match = "✓" if result.get('name_match', False) else "✗"
                error = f" (错误: {result.get('error', '')})" if result.get('error') else ""
                print(f"  {api_source:10}: {status} 找到 | {name_match} 名称匹配{error}")
        else:
            print(f"基础匹配失败: {basic_result.get('匹配状态')}")

def test_full_workflow():
    """测试完整工作流程"""
    print("\n=== 测试完整工作流程 ===")
    
    # 使用之前创建的测试文件
    test_file = test_quoted_codes()
    
    matcher = StockNameMatcher(api_source='local')
    
    # 不启用交叉验证的处理
    print("\n--- 不启用交叉验证 ---")
    output_file1 = matcher.process_stock_codes(
        test_file,
        "test_result_basic.csv",
        enable_cross_validation=False
    )

    # 启用交叉验证的处理
    print("\n--- 启用交叉验证 ---")
    output_file2 = matcher.process_stock_codes(
        test_file,
        "test_result_validated.csv",
        enable_cross_validation=True
    )
    
    # 比较结果
    print("\n=== 结果比较 ===")
    
    df1 = pd.read_csv(output_file1)
    df2 = pd.read_csv(output_file2)
    
    print("基础处理结果列:")
    print(list(df1.columns))
    
    print("\n验证处理结果列:")
    print(list(df2.columns))
    
    print("\n基础处理结果:")
    print(df1[['原始代码', '标准化代码', '股票名称', '匹配状态']].to_string(index=False))
    
    if '验证置信度' in df2.columns:
        print("\n验证处理结果:")
        print(df2[['原始代码', '标准化代码', '股票名称', '匹配状态', '验证置信度', '名称一致性']].to_string(index=False))
    
    # 清理测试文件
    for file in [test_file, output_file1, output_file2]:
        if os.path.exists(file):
            os.remove(file)
            print(f"清理文件: {file}")

if __name__ == "__main__":
    try:
        # 测试被引号包裹的代码处理
        test_quoted_codes()
        
        # 测试交叉验证（注意：这会比较慢）
        # test_cross_validation()
        
        # 测试完整工作流程
        test_full_workflow()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
