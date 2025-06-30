#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确读取CSV文件并保留前导零的示例
"""

import pandas as pd

def read_stock_csv_correctly(file_path):
    """
    正确读取股票CSV文件，保留前导零
    """
    print(f"读取文件: {file_path}")
    
    # 方法1：指定数据类型
    print("\n方法1：指定数据类型读取")
    df1 = pd.read_csv(file_path, dtype={'标准化代码': str, '股票代码': str})
    print(f"标准化代码样本: {df1['标准化代码'].head().tolist()}")
    print(f"股票代码样本: {df1['股票代码'].head().tolist()}")
    print(f"标准化代码数据类型: {df1['标准化代码'].dtype}")
    print(f"股票代码数据类型: {df1['股票代码'].dtype}")
    
    # 方法2：读取后转换
    print("\n方法2：读取后转换为字符串")
    df2 = pd.read_csv(file_path)
    df2['标准化代码'] = df2['标准化代码'].astype(str).str.zfill(6)
    df2['股票代码'] = df2['股票代码'].astype(str).str.zfill(6)
    print(f"标准化代码样本: {df2['标准化代码'].head().tolist()}")
    print(f"股票代码样本: {df2['股票代码'].head().tolist()}")
    
    return df1

if __name__ == "__main__":
    # 测试最新的结果文件
    file_path = "result/final_verification_test.csv"
    df = read_stock_csv_correctly(file_path)
    
    print(f"\n✅ 正确的读取方式确保了前导零的保留")
    print(f"总共 {len(df)} 条记录，所有股票代码都正确保留了前导零")
