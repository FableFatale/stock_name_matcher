#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Web应用文件上传功能
"""

import sys
import os
# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_upload():
    """测试文件上传"""
    url = "http://localhost:5000/upload"
    
    # 检查测试文件是否存在
    test_file = "000852.csv"
    if not os.path.exists(test_file):
        print(f"测试文件 {test_file} 不存在，跳过测试")
        return None
    
    # 上传文件
    with open(test_file, "rb") as f:
        files = {"file": (test_file, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        print("正在上传文件...")
        try:
            response = requests.post(url, files=files)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {response.headers}")
            print(f"响应内容长度: {len(response.content)} 字节")
            
            # 打印原始响应内容
            print("\n=== 原始响应内容 ===")
            print(response.text[:1000])  # 只打印前1000个字符
            
            # 尝试解析JSON
            try:
                data = response.json()
                print("\n=== JSON解析成功 ===")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return data
            except json.JSONDecodeError as e:
                print(f"\n=== JSON解析失败 ===")
                print(f"错误: {e}")
                print(f"错误位置: 第{e.lineno}行, 第{e.colno}列")
                
                # 查看错误位置附近的内容
                if hasattr(e, 'pos'):
                    start = max(0, e.pos - 50)
                    end = min(len(response.text), e.pos + 50)
                    print(f"错误位置附近的内容:")
                    print(repr(response.text[start:end]))
                
                return None
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到Web应用，请确保应用正在运行 (python app.py)")
            return None
        except Exception as e:
            print(f"❌ 上传测试失败: {e}")
            return None

if __name__ == "__main__":
    test_upload()
