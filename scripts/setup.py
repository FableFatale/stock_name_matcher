#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票名称匹配器一键安装脚本
"""

import os
import sys
import subprocess

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🔧 股票名称匹配器 - 一键安装")
    print("=" * 60)

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"\n📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}完成")
            return True
        else:
            print(f"❌ {description}失败")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}失败: {e}")
        return False

def check_python():
    """检查Python版本"""
    print("\n🐍 检查Python环境...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装依赖包...")
    
    # 升级pip
    print("升级pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip")
    
    # 安装依赖
    if os.path.exists("requirements.txt"):
        success = run_command(f"{sys.executable} -m pip install -r requirements.txt", "安装依赖包")
    else:
        # 手动安装核心依赖
        packages = [
            "pandas>=1.3.5",
            "numpy>=1.21.6", 
            "openpyxl>=3.1.5",
            "akshare>=1.16.98",
            "fuzzywuzzy>=0.18.0",
            "python-Levenshtein>=0.12.2",
            "requests>=2.28.1",
            "tqdm>=4.64.0"
        ]
        
        success = True
        for package in packages:
            if not run_command(f"{sys.executable} -m pip install {package}", f"安装 {package}"):
                success = False
    
    return success

def test_imports():
    """测试模块导入"""
    print("\n🧪 测试模块导入...")
    
    test_modules = [
        "pandas",
        "numpy", 
        "openpyxl",
        "akshare",
        "fuzzywuzzy",
        "requests"
    ]
    
    failed = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed.append(module)
    
    return len(failed) == 0

def create_directories():
    """创建必要目录"""
    print("\n📁 创建目录...")
    
    directories = ["logs", "results", "temp"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录 {directory}")
        except Exception as e:
            print(f"❌ 目录 {directory}: {e}")
            return False
    
    return True

def run_quick_test():
    """运行快速测试"""
    print("\n🚀 运行快速测试...")
    
    try:
        # 简单的功能测试
        import pandas as pd
        import akshare as ak
        from fuzzywuzzy import fuzz
        
        # 测试pandas
        df = pd.DataFrame({'test': [1, 2, 3]})
        
        # 测试fuzzywuzzy
        score = fuzz.ratio("test", "test")
        
        print("✅ 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python():
        input("按回车键退出...")
        return 1
    
    # 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败")
        input("按回车键退出...")
        return 1
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        input("按回车键退出...")
        return 1
    
    # 创建目录
    if not create_directories():
        print("\n❌ 目录创建失败")
        input("按回车键退出...")
        return 1
    
    # 运行测试
    if not run_quick_test():
        print("\n❌ 功能测试失败")
        input("按回车键退出...")
        return 1
    
    # 安装完成
    print("\n" + "=" * 60)
    print("🎉 安装完成！")
    print("=" * 60)
    print("\n📋 下一步:")
    print("1. 运行快速演示: python quick_start.py")
    print("2. 使用交互界面: python start.py")
    print("3. 直接使用: python stock_name_matcher.py your_file.xlsx")
    print("4. 查看文档: README.md")
    
    input("\n按回车键退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
