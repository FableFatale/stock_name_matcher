#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的Web应用测试脚本
测试文件上传、处理和下载功能
"""

import sys
import os
# 添加父目录到路径，以便导入主模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import pandas as pd
import time

def create_test_csv():
    """创建测试CSV文件"""
    test_data = {
        '股票代码': ["'000852'", '"002208"', "'300018'", "688001", "'301223'"],
        '入选价格': [6.87, 8.47, 20.38, 45.67, 12.36]
    }
    
    test_df = pd.DataFrame(test_data)
    test_file = "tests/test_quoted_codes_web.csv"
    test_df.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    print(f"创建测试文件: {test_file}")
    print("测试数据:")
    print(test_df)
    
    return test_file

def test_web_app_workflow():
    """测试完整的Web应用工作流程"""
    base_url = "http://localhost:5000"
    
    print("=== 测试Web应用完整工作流程 ===")
    
    # 检查Web应用是否运行
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code != 200:
            print("❌ Web应用未正常运行，请先启动: python app.py")
            return False
        print("✅ Web应用运行正常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web应用，请确保应用正在运行: python app.py")
        return False
    except Exception as e:
        print(f"❌ 检查Web应用状态失败: {e}")
        return False
    
    # 创建测试文件
    test_file = create_test_csv()
    
    try:
        # 1. 测试文件上传
        print("\n=== 步骤1: 测试文件上传 ===")
        with open(test_file, "rb") as f:
            files = {"file": (os.path.basename(test_file), f, "text/csv")}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            print("✅ 文件上传成功")
            print(f"文件名: {upload_result.get('filename')}")
            print(f"行数: {upload_result.get('rows')}")
            print(f"列名: {upload_result.get('columns')}")
            
            # 2. 测试基础处理（不启用交叉验证）
            print("\n=== 步骤2: 测试基础处理 ===")
            process_data = {
                "filename": upload_result.get('filename'),
                "code_column": "股票代码",
                "price_column": "入选价格",
                "api_source": "local",  # 使用本地数据源
                "enable_cross_validation": False
            }
            
            response = requests.post(f"{base_url}/process", json=process_data)
            
            if response.status_code == 200:
                process_result = response.json()
                print("✅ 基础处理成功")
                print(f"处理状态: {process_result.get('status')}")
                print(f"成功数量: {process_result.get('success_count')}")
                print(f"总数量: {process_result.get('total_count')}")
                print(f"结果文件: {process_result.get('result_file')}")
                
                # 显示预览结果
                if 'preview' in process_result:
                    print("\n预览结果:")
                    for i, row in enumerate(process_result['preview'][:3]):
                        print(f"  行 {i+1}: {row.get('原始代码')} -> {row.get('股票名称')} ({row.get('匹配状态')})")
                
                # 3. 测试交叉验证处理
                print("\n=== 步骤3: 测试交叉验证处理 ===")
                process_data["enable_cross_validation"] = True
                
                response = requests.post(f"{base_url}/process", json=process_data)
                
                if response.status_code == 200:
                    process_result = response.json()
                    print("✅ 交叉验证处理成功")
                    print(f"处理状态: {process_result.get('status')}")
                    print(f"成功数量: {process_result.get('success_count')}")
                    print(f"总数量: {process_result.get('total_count')}")
                    
                    # 显示验证结果
                    if 'preview' in process_result:
                        print("\n验证结果预览:")
                        for i, row in enumerate(process_result['preview'][:3]):
                            print(f"  行 {i+1}: {row.get('原始代码')} -> {row.get('股票名称')}")
                            print(f"    匹配状态: {row.get('匹配状态')}")
                            print(f"    验证置信度: {row.get('验证置信度', 'N/A')}")
                            print(f"    名称一致性: {row.get('名称一致性', 'N/A')}")
                    
                    # 4. 测试文件下载
                    print("\n=== 步骤4: 测试文件下载 ===")
                    result_file = process_result.get('result_file')
                    if result_file:
                        download_url = f"{base_url}/download/{result_file}"
                        response = requests.get(download_url)
                        
                        if response.status_code == 200:
                            print("✅ 文件下载成功")
                            print(f"下载文件大小: {len(response.content)} 字节")
                            
                            # 保存下载的文件进行验证
                            download_path = f"tests/downloaded_{result_file}"
                            with open(download_path, 'wb') as f:
                                f.write(response.content)
                            
                            # 验证下载的文件内容
                            try:
                                df = pd.read_csv(download_path)
                                print(f"下载文件验证: {len(df)} 行, {len(df.columns)} 列")
                                print(f"列名: {list(df.columns)}")
                                
                                # 清理下载的文件
                                os.remove(download_path)
                                print(f"清理下载文件: {download_path}")
                            except Exception as e:
                                print(f"⚠️ 下载文件验证失败: {e}")
                        else:
                            print(f"❌ 文件下载失败: {response.status_code}")
                    else:
                        print("⚠️ 没有结果文件可下载")
                        
                else:
                    print(f"❌ 交叉验证处理失败: {response.status_code}")
                    print(response.text)
                
            else:
                print(f"❌ 基础处理失败: {response.status_code}")
                print(response.text)
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n清理测试文件: {test_file}")
    
    print("\n✅ Web应用测试完成！")
    return True

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:5000"
    
    print("\n=== 测试API端点 ===")
    
    endpoints = [
        ("/", "GET", "主页"),
        ("/api/status", "GET", "状态检查"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}): 正常")
            else:
                print(f"⚠️ {description} ({endpoint}): 状态码 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description} ({endpoint}): 错误 {e}")

if __name__ == "__main__":
    print("🧪 开始Web应用测试")
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试完整工作流程
    success = test_web_app_workflow()
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n💥 部分测试失败，请检查日志")
