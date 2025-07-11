#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖安装脚本
自动安装股票名称匹配器所需的依赖包
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_package(package):
    """安装单个包"""
    print(f"正在安装 {package}...")
    success, stdout, stderr = run_command(f"pip install {package}")
    
    if success:
        print(f"✅ {package} 安装成功")
        return True
    else:
        print(f"❌ {package} 安装失败")
        print(f"错误信息: {stderr}")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    if os.path.exists("requirements.txt"):
        print("正在安装requirements.txt中的依赖...")
        success, stdout, stderr = run_command("pip install -r requirements.txt")
        
        if success:
            print("✅ requirements.txt 安装成功")
            return True
        else:
            print("❌ requirements.txt 安装失败")
            print(f"错误信息: {stderr}")
            return False
    else:
        print("未找到requirements.txt文件，手动安装核心依赖...")
        
        # 核心依赖列表
        core_packages = [
            "pandas>=1.3.5",
            "numpy>=1.21.6",
            "openpyxl>=3.1.5",
            "akshare>=1.16.98",
            "fuzzywuzzy>=0.18.0",
            "python-Levenshtein>=0.12.2",
            "requests>=2.28.1"
        ]
        
        failed_packages = []
        for package in core_packages:
            if not install_package(package):
                failed_packages.append(package)
        
        if failed_packages:
            print(f"❌ 以下包安装失败: {failed_packages}")
            return False
        else:
            print("✅ 所有核心依赖安装成功")
            return True

def test_imports():
    """测试关键模块导入"""
    print("\n测试关键模块导入...")
    
    test_modules = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("openpyxl", None),
        ("akshare", "ak"),
        ("fuzzywuzzy.fuzz", "fuzz"),
        ("requests", None)
    ]
    
    failed_imports = []
    
    for module_name, alias in test_modules:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"✅ {module_name} 导入成功")
        except ImportError as e:
            print(f"❌ {module_name} 导入失败: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ 以下模块导入失败: {failed_imports}")
        return False
    else:
        print("\n✅ 所有关键模块导入成功")
        return True

def create_directories():
    """创建必要的目录"""
    print("\n创建必要的目录...")
    
    directories = ["logs", "cache", "test_results"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录 {directory} 创建成功")
        except Exception as e:
            print(f"❌ 目录 {directory} 创建失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("股票名称匹配器依赖安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 安装依赖
    if not install_requirements():
        print("\n❌ 依赖安装失败，请手动安装")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入测试失败，请检查安装")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 创建目录
    if not create_directories():
        print("\n❌ 目录创建失败")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("\n可以开始使用股票名称匹配器了：")
    print("  python stock_name_matcher.py example_stocks.csv")
    print("  python test_stock_matcher.py")
    print("\n详细使用说明请查看：股票名称匹配器使用说明.md")

if __name__ == "__main__":
    main()
