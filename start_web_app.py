#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票代码名称补全Web应用启动脚本
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:5000')

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 股票代码名称补全Web应用")
    print("=" * 60)
    print()
    print("📋 功能特点:")
    print("  ✅ 支持CSV/Excel文件上传")
    print("  ✅ 自动检测股票代码和价格列")
    print("  ✅ 智能补全股票名称")
    print("  ✅ 提供详细的市场数据")
    print("  ✅ 100%成功率的代码标准化")
    print("  ✅ 实时结果预览和下载")
    print()
    print("📁 文件夹结构:")
    print("  📂 uploads/  - 上传文件存储")
    print("  📂 result/   - 处理结果存储")
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("📱 支持手机和电脑访问")
    print()
    print("正在启动服务器...")
    
    # 延迟打开浏览器
    Timer(2.0, open_browser).start()
    
    # 启动Flask应用
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n🔧 解决方案:")
        print("  1. 确保已安装所有依赖: pip install flask pandas akshare fuzzywuzzy")
        print("  2. 检查端口5000是否被占用")
        print("  3. 尝试以管理员权限运行")

if __name__ == '__main__':
    main()
