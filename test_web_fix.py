#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web应用的股票匹配功能
"""

import requests
import json
import os
import time

def test_web_app():
    """测试Web应用"""
    base_url = "http://localhost:5000"
    
    # 1. 测试API状态
    print("1. 测试API状态...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ API状态正常，股票数量: {status_data.get('stock_count', 0)}")
        else:
            print(f"❌ API状态异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到Web应用: {e}")
        return
    
    # 2. 上传测试文件
    print("\n2. 上传测试文件...")
    test_file_path = "20250617171501.csv"
    
    if not os.path.exists(test_file_path):
        print(f"❌ 测试文件不存在: {test_file_path}")
        return
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/csv')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ 文件上传成功: {upload_data.get('filename')}")
            filename = upload_data.get('filename')
            file_info = upload_data.get('file_info', {})
            print(f"   文件行数: {file_info.get('rows', 0)}")
            print(f"   文件列数: {len(file_info.get('columns', []))}")
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return
    
    # 3. 处理文件
    print("\n3. 处理股票代码...")
    try:
        process_data = {
            'filename': filename,
            'code_column': '股票代码',
            'price_column': '买入价格',
            'api_source': 'akshare',
            'enable_cross_validation': False
        }
        
        response = requests.post(
            f"{base_url}/process",
            json=process_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"✅ 处理成功!")
            
            stats = result_data.get('statistics', {})
            print(f"   总数: {stats.get('total', 0)}")
            print(f"   成功: {stats.get('success', 0)}")
            print(f"   失败: {stats.get('not_found', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0)}%")
            
            # 显示前几个结果
            preview = result_data.get('preview', [])
            print(f"\n   前5个结果:")
            for i, row in enumerate(preview[:5]):
                original_code = row.get('原始代码', '')
                stock_name = row.get('股票名称', '')
                match_status = row.get('匹配状态', '')
                print(f"   {i+1}. {original_code} -> {stock_name} ({match_status})")
                
        else:
            print(f"❌ 处理失败: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        return
    
    print("\n🎉 Web应用测试完成!")

if __name__ == "__main__":
    test_web_app()
