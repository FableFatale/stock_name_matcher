#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载功能修复
检查下载端点和浏览器兼容性
"""

import os
import sys
import requests
import time
from datetime import datetime

def test_download_endpoint():
    """测试下载端点是否正常工作"""
    print("🔍 测试下载功能...")
    
    # 检查result文件夹中是否有文件
    result_folder = 'result'
    if not os.path.exists(result_folder):
        print("❌ result文件夹不存在")
        return False
    
    # 获取最新的结果文件
    result_files = [f for f in os.listdir(result_folder) if f.endswith('.csv')]
    if not result_files:
        print("❌ result文件夹中没有CSV文件")
        return False
    
    # 选择最新的文件
    latest_file = max(result_files, key=lambda f: os.path.getctime(os.path.join(result_folder, f)))
    print(f"📁 测试文件: {latest_file}")
    
    # 测试下载端点
    base_url = "http://localhost:5000"
    download_url = f"{base_url}/download/{latest_file}"
    
    try:
        print(f"🌐 请求URL: {download_url}")
        response = requests.get(download_url, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        if response.status_code == 200:
            print("✅ 下载端点工作正常")
            
            # 检查响应头
            content_disposition = response.headers.get('Content-Disposition', '')
            content_type = response.headers.get('Content-Type', '')
            content_length = response.headers.get('Content-Length', '')
            
            print(f"📄 Content-Type: {content_type}")
            print(f"📦 Content-Disposition: {content_disposition}")
            print(f"📏 Content-Length: {content_length}")
            
            # 检查是否设置了正确的下载头
            if 'attachment' in content_disposition:
                print("✅ 正确设置了attachment头")
            else:
                print("⚠️  未设置attachment头，可能不会弹出保存对话框")
            
            return True
        else:
            print(f"❌ 下载失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

def create_test_download_html():
    """创建测试下载的HTML页面"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>下载功能测试</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        .success { color: green; }
        .error { color: red; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1>下载功能测试页面</h1>
    
    <div class="test-section">
        <h3>测试不同的下载方法</h3>
        <button onclick="testMethod1()">方法1: 直接链接</button>
        <button onclick="testMethod2()">方法2: 创建临时链接</button>
        <button onclick="testMethod3()">方法3: Fetch + Blob</button>
        <button onclick="testMethod4()">方法4: 新窗口打开</button>
        <div id="status"></div>
    </div>

    <script>
        const resultFileName = 'stock_completion_20250618_151423.csv'; // 替换为实际文件名
        
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<p class="${type}">${message}</p>`;
        }
        
        function testMethod1() {
            showStatus('测试方法1: 直接链接跳转', 'info');
            window.location.href = `/download/${resultFileName}`;
        }
        
        function testMethod2() {
            showStatus('测试方法2: 创建临时链接', 'info');
            const link = document.createElement('a');
            link.href = `/download/${resultFileName}`;
            link.download = resultFileName;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            setTimeout(() => document.body.removeChild(link), 100);
        }
        
        function testMethod3() {
            showStatus('测试方法3: Fetch + Blob', 'info');
            fetch(`/download/${resultFileName}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.blob();
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = resultFileName;
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    setTimeout(() => {
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(url);
                    }, 100);
                    showStatus('方法3: 下载完成', 'success');
                })
                .catch(error => {
                    showStatus(`方法3: 下载失败 - ${error.message}`, 'error');
                });
        }
        
        function testMethod4() {
            showStatus('测试方法4: 新窗口打开', 'info');
            window.open(`/download/${resultFileName}`, '_blank');
        }
    </script>
</body>
</html>"""
    
    with open('test_download.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("📄 创建了测试页面: test_download.html")
    print("🌐 请在浏览器中打开此文件进行测试")

def main():
    print("🚀 开始下载功能诊断...")
    
    # 测试下载端点
    endpoint_ok = test_download_endpoint()
    
    if endpoint_ok:
        print("\n✅ 后端下载功能正常")
        print("🔧 问题可能在前端，创建测试页面...")
        create_test_download_html()
        
        print("\n📋 建议的修复步骤:")
        print("1. 打开 test_download.html 测试不同的下载方法")
        print("2. 检查浏览器控制台是否有错误信息")
        print("3. 确认浏览器下载设置（是否阻止了弹窗）")
        print("4. 尝试不同的浏览器进行测试")
        
    else:
        print("\n❌ 后端下载功能异常")
        print("🔧 请检查:")
        print("1. Flask应用是否正在运行")
        print("2. result文件夹中是否有文件")
        print("3. 下载路由是否正确配置")

if __name__ == '__main__':
    main()
