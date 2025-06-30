#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传模拟功能
"""

import sys
import os
# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
from datetime import datetime

def detect_file_format(filepath):
    """智能检测文件格式"""
    try:
        # 读取文件前几个字节来判断格式
        with open(filepath, 'rb') as f:
            header = f.read(8)

        # Excel文件的魔数
        if header.startswith(b'\xd0\xcf\x11\xe0') or header.startswith(b'PK\x03\x04'):
            return 'excel'

        # 尝试作为文本文件读取
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                f.read(100)
            return 'csv'
        except:
            try:
                with open(filepath, 'r', encoding='gbk') as f:
                    f.read(100)
                return 'csv'
            except:
                return 'unknown'
    except:
        return 'unknown'

def get_file_info(filepath):
    """获取文件基本信息"""
    try:
        # 智能检测文件格式
        file_format = detect_file_format(filepath)
        print(f"检测到文件格式: {file_format}")

        df = None
        encoding_used = None
        sep_used = None

        if file_format == 'excel' or filepath.endswith(('.xlsx', '.xls')):
            # Excel文件
            try:
                df = pd.read_excel(filepath, nrows=5)
                print("Excel文件读取成功")
            except Exception as e:
                print(f"Excel文件读取失败: {e}")
                raise ValueError(f"无法读取Excel文件: {e}")

        else:
            # CSV文件或文本文件
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
            separators = [',', '\t', ';', '|']

            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=5)
                        # 检查是否成功读取（至少有1列且有数据）
                        if len(df.columns) >= 1 and len(df) > 0:
                            # 进一步检查是否有合理的列数
                            if len(df.columns) >= 2 or (len(df.columns) == 1 and ',' in str(df.iloc[0, 0])):
                                encoding_used = encoding
                                sep_used = sep
                                print(f"CSV文件读取成功: 编码={encoding}, 分隔符='{sep}'")
                                break
                    except Exception as e:
                        print(f"尝试读取失败: 编码={encoding}, 分隔符='{sep}', 错误={e}")
                        continue
                if df is not None and len(df.columns) >= 1:
                    break

            if df is None:
                raise ValueError("无法正确解析文件，请检查文件格式、编码或分隔符")

        # 获取完整行数
        if file_format == 'excel' or filepath.endswith(('.xlsx', '.xls')):
            full_df = pd.read_excel(filepath)
            total_rows = len(full_df)
        else:
            full_df = pd.read_csv(filepath, encoding=encoding_used, sep=sep_used)
            total_rows = len(full_df)

        # 处理预览数据，确保可以JSON序列化
        preview_data = []
        for _, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                # 处理NaN值和特殊数值
                if pd.isna(val):
                    row_dict[col] = None
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    row_dict[col] = float(val) if isinstance(val, float) else int(val)
                else:
                    row_dict[col] = str(val)
            preview_data.append(row_dict)

        file_info = {
            'columns': list(df.columns),
            'rows': total_rows,
            'preview': preview_data,
            'file_format': file_format,
            'encoding': encoding_used,
            'separator': sep_used
        }
        
        return file_info
    except Exception as e:
        print(f"读取文件信息失败: {e}")
        return None

def test_json_serialization(file_info):
    """测试JSON序列化"""
    try:
        json_str = json.dumps(file_info, ensure_ascii=False, indent=2)
        print("JSON序列化成功")
        print(f"JSON长度: {len(json_str)} 字符")
        
        # 尝试解析
        parsed = json.loads(json_str)
        print("JSON解析成功")
        
        return True, json_str
    except Exception as e:
        print(f"JSON序列化/解析失败: {e}")
        return False, str(e)

def test_upload_simulation():
    """测试上传模拟"""
    file_path = "000852.csv"
    
    if not os.path.exists(file_path):
        print(f"测试文件 {file_path} 不存在，跳过测试")
        return
    
    print("=== 测试文件信息获取 ===")
    file_info = get_file_info(file_path)
    
    if file_info:
        print("\n=== 文件信息 ===")
        print(f"列数: {len(file_info['columns'])}")
        print(f"行数: {file_info['rows']}")
        print(f"列名: {file_info['columns']}")
        print(f"文件格式: {file_info['file_format']}")
        
        print("\n=== 预览数据 ===")
        for i, row in enumerate(file_info['preview']):
            print(f"行 {i+1}: {row}")
        
        print("\n=== 测试JSON序列化 ===")
        success, result = test_json_serialization(file_info)
        
        if not success:
            print(f"JSON错误: {result}")
        else:
            print("JSON序列化测试通过")
    else:
        print("文件信息获取失败")

if __name__ == "__main__":
    test_upload_simulation()
