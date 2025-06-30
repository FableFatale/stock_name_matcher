#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件格式检测功能
"""

import sys
import os
# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

def test_file_format_detection():
    """测试文件格式检测"""
    print("=== 测试文件格式检测 ===")
    
    # 检查文件
    file_path = '000852.csv'
    print(f'文件存在: {os.path.exists(file_path)}')
    
    if not os.path.exists(file_path):
        print("测试文件不存在，跳过测试")
        return
    
    # 读取文件头部
    with open(file_path, 'rb') as f:
        header = f.read(8)
        print(f'文件头部: {header}')
        print(f'是否为Excel格式: {header.startswith(b"PK")}')
    
    # 尝试作为Excel读取
    try:
        df = pd.read_excel(file_path)
        print(f'Excel读取成功，行数: {len(df)}, 列数: {len(df.columns)}')
        print(f'列名: {list(df.columns)}')
        print('前5行数据:')
        print(df.head())
    except Exception as e:
        print(f'Excel读取失败: {e}')
    
    # 尝试作为CSV读取
    try:
        df = pd.read_csv(file_path)
        print(f'CSV读取成功，行数: {len(df)}, 列数: {len(df.columns)}')
    except Exception as e:
        print(f'CSV读取失败: {e}')

if __name__ == "__main__":
    test_file_format_detection()
