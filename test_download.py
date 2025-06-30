#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载功能
"""

import requests
import os
import time

def test_download_functionality():
    """测试下载功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试下载功能")
    print("="*50)
    
    # 1. 检查result文件夹中是否有文件
    result_folder = "result"
    if not os.path.exists(result_folder):
        print("❌ result文件夹不存在")
        return
    
    files = [f for f in os.listdir(result_folder) if f.endswith('.csv')]
    if not files:
        print("❌ result文件夹中没有CSV文件")
        print("💡 请先运行股票匹配生成一些结果文件")
        return
    
    test_file = files[0]
    print(f"📁 找到测试文件: {test_file}")
    
    # 2. 测试下载API
    download_url = f"{base_url}/download/{test_file}"
    print(f"🔗 下载URL: {download_url}")
    
    try:
        response = requests.get(download_url, stream=True)
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"📋 响应头:")
        for key, value in response.headers.items():
            if key.lower() in ['content-disposition', 'content-type', 'content-length']:
                print(f"   {key}: {value}")
        
        if response.status_code == 200:
            print("✅ 下载API工作正常")
            
            # 检查响应头是否正确设置
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print("✅ Content-Disposition 设置正确，应该会弹出保存对话框")
            else:
                print("⚠️ Content-Disposition 可能设置不正确")
            
            # 保存测试文件
            test_download_path = f"test_download_{test_file}"
            with open(test_download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"💾 测试下载完成: {test_download_path}")
            
            # 验证文件内容
            if os.path.exists(test_download_path):
                file_size = os.path.getsize(test_download_path)
                print(f"📏 下载文件大小: {file_size} bytes")
                
                # 清理测试文件
                os.remove(test_download_path)
                print("🧹 清理测试文件完成")
            
        else:
            print(f"❌ 下载失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    
    except Exception as e:
        print(f"❌ 下载测试异常: {e}")

def create_test_result_file():
    """创建一个测试结果文件"""
    print("\n🔧 创建测试结果文件...")
    
    import pandas as pd
    from datetime import datetime
    
    # 创建测试数据
    test_data = {
        '原始代码': ["'000001", "'000002", "'600000"],
        '参考价格': [11.73, 6.43, 12.73],
        '匹配状态': ['匹配成功', '匹配成功', '匹配成功'],
        '标准化代码': ['000001', '000002', '600000'],
        '股票代码': ['000001', '000002', '600000'],
        '股票名称': ['平安银行', '万科A', '浦发银行'],
        '当前价格': [11.73, 6.43, 12.73],
        '价格差异': [0.0, 0.0, 0.0],
        '匹配类型': ['代码标准化匹配', '代码标准化匹配', '代码标准化匹配']
    }
    
    df = pd.DataFrame(test_data)
    
    # 确保result文件夹存在
    result_folder = "result"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    
    # 保存测试文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_filename = f"download_test_{timestamp}.csv"
    test_filepath = os.path.join(result_folder, test_filename)
    
    df.to_csv(test_filepath, index=False, encoding='utf-8-sig')
    print(f"✅ 测试文件已创建: {test_filepath}")
    
    return test_filename

def test_browser_download():
    """测试浏览器下载行为"""
    print("\n🌐 浏览器下载测试指南")
    print("="*50)
    
    print("请按以下步骤测试下载功能:")
    print("1. 🚀 启动Web应用 (python app.py)")
    print("2. 🌐 打开浏览器访问 http://localhost:5000")
    print("3. 📁 上传一个CSV文件并处理")
    print("4. ⬇️ 点击'下载结果'按钮")
    print()
    print("预期行为:")
    print("✅ 应该弹出文件保存对话框")
    print("✅ 可以选择保存位置")
    print("✅ 文件名应该预填充")
    print()
    print("如果没有弹出保存对话框:")
    print("🔍 检查浏览器下载设置")
    print("🔍 查看浏览器下载历史")
    print("🔍 检查默认下载文件夹")
    print()
    print("不同浏览器行为:")
    print("• Chrome: 通常直接下载到默认文件夹")
    print("• Firefox: 通常会弹出保存对话框")
    print("• Edge: 行为类似Chrome")
    print("• Safari: 通常会弹出保存对话框")

def main():
    """主函数"""
    print("🧪 股票匹配系统 - 下载功能测试")
    print("="*60)
    
    # 创建测试文件
    test_filename = create_test_result_file()
    
    # 等待一下确保文件创建完成
    time.sleep(1)
    
    # 测试下载功能
    test_download_functionality()
    
    # 显示浏览器测试指南
    test_browser_download()
    
    print("\n🎯 总结:")
    print("1. 后端下载API已优化，设置了正确的响应头")
    print("2. 前端使用了多种下载方法，提高兼容性")
    print("3. 添加了下载状态提示，改善用户体验")
    print("4. 不同浏览器的下载行为可能不同")
    print()
    print("💡 建议:")
    print("- 在Firefox中测试，通常会弹出保存对话框")
    print("- 检查浏览器下载设置")
    print("- 查看浏览器控制台是否有错误信息")

if __name__ == "__main__":
    main()
