#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境配置检查脚本
检查股票名称匹配器运行环境是否正确配置
"""

import sys
import os
import importlib
from datetime import datetime

def print_header():
    """打印标题"""
    print("=" * 60)
    print("🔧 股票名称匹配器 - 环境配置检查")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("\n📋 Python环境检查")
    print("-" * 30)
    
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    print(f"Python路径: {sys.executable}")
    
    if version.major < 3:
        print("❌ 需要Python 3.x版本")
        return False
    elif version.major == 3 and version.minor < 7:
        print("⚠️  建议使用Python 3.7或更高版本")
        return True
    else:
        print("✅ Python版本符合要求")
        return True

def check_required_modules():
    """检查必需模块"""
    print("\n📦 依赖模块检查")
    print("-" * 30)
    
    required_modules = {
        'pandas': '数据处理',
        'numpy': '数值计算',
        'openpyxl': 'Excel文件支持',
        'akshare': '股票数据API',
        'fuzzywuzzy': '模糊匹配',
        'Levenshtein': '字符串相似度计算',
        'requests': 'HTTP请求'
    }
    
    all_ok = True
    
    for module_name, description in required_modules.items():
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {module_name:<15} {version:<10} - {description}")
        except ImportError:
            print(f"❌ {module_name:<15} {'未安装':<10} - {description}")
            all_ok = False
    
    return all_ok

def check_optional_modules():
    """检查可选模块"""
    print("\n🔧 可选模块检查")
    print("-" * 30)
    
    optional_modules = {
        'matplotlib': '图表绘制',
        'tqdm': '进度条显示',
        'psycopg2': 'PostgreSQL数据库连接',
        'sqlalchemy': 'SQL工具包'
    }
    
    for module_name, description in optional_modules.items():
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {module_name:<15} {version:<10} - {description}")
        except ImportError:
            print(f"⚪ {module_name:<15} {'未安装':<10} - {description} (可选)")

def check_files():
    """检查必要文件"""
    print("\n📁 文件检查")
    print("-" * 30)
    
    required_files = [
        'stock_name_matcher.py',
        'requirements.txt'
    ]
    
    optional_files = [
        'test_stock_matcher.py',
        'example_stocks.csv',
        'quick_start.py',
        'install_dependencies.py',
        '股票名称匹配器使用说明.md'
    ]
    
    all_required_exist = True
    
    print("必需文件:")
    for file_name in required_files:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            print(f"✅ {file_name:<25} ({size} 字节)")
        else:
            print(f"❌ {file_name:<25} (缺失)")
            all_required_exist = False
    
    print("\n可选文件:")
    for file_name in optional_files:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            print(f"✅ {file_name:<25} ({size} 字节)")
        else:
            print(f"⚪ {file_name:<25} (缺失)")
    
    return all_required_exist

def check_directories():
    """检查目录结构"""
    print("\n📂 目录结构检查")
    print("-" * 30)
    
    required_dirs = ['logs']
    optional_dirs = ['cache', 'test_results', 'config', 'utils']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name}/ (存在)")
        else:
            print(f"⚪ {dir_name}/ (不存在，将自动创建)")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ {dir_name}/ (已创建)")
            except Exception as e:
                print(f"❌ {dir_name}/ (创建失败: {e})")
    
    for dir_name in optional_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ {dir_name}/ (存在)")
        else:
            print(f"⚪ {dir_name}/ (不存在)")

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 基本功能测试")
    print("-" * 30)
    
    try:
        # 测试pandas
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        print("✅ pandas 基本功能正常")
        
        # 测试akshare (不实际调用API)
        import akshare as ak
        print("✅ akshare 模块导入正常")
        
        # 测试fuzzywuzzy
        from fuzzywuzzy import fuzz
        score = fuzz.ratio("test", "test")
        print("✅ fuzzywuzzy 基本功能正常")
        
        # 测试openpyxl
        import openpyxl
        print("✅ openpyxl 模块导入正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

def provide_recommendations():
    """提供建议"""
    print("\n💡 建议和下一步")
    print("-" * 30)
    
    print("1. 如果有模块缺失，请运行:")
    print("   python install_dependencies.py")
    print("   或者: pip install -r requirements.txt")
    
    print("\n2. 快速开始:")
    print("   python quick_start.py")
    
    print("\n3. 运行测试:")
    print("   python test_stock_matcher.py")
    
    print("\n4. 使用股票匹配器:")
    print("   python stock_name_matcher.py your_file.xlsx")
    
    print("\n5. 查看详细文档:")
    print("   股票名称匹配器使用说明.md")

def main():
    """主函数"""
    print_header()
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查必需模块
    modules_ok = check_required_modules()
    
    # 检查可选模块
    check_optional_modules()
    
    # 检查文件
    files_ok = check_files()
    
    # 检查目录
    check_directories()
    
    # 测试基本功能
    if modules_ok:
        functionality_ok = test_basic_functionality()
    else:
        functionality_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 检查结果总结")
    print("=" * 60)
    
    print(f"Python环境: {'✅ 正常' if python_ok else '❌ 异常'}")
    print(f"依赖模块: {'✅ 完整' if modules_ok else '❌ 缺失'}")
    print(f"必需文件: {'✅ 完整' if files_ok else '❌ 缺失'}")
    print(f"基本功能: {'✅ 正常' if functionality_ok else '❌ 异常'}")
    
    if all([python_ok, modules_ok, files_ok, functionality_ok]):
        print("\n🎉 环境配置完整，可以正常使用股票名称匹配器！")
        status = 0
    else:
        print("\n⚠️  环境配置不完整，请根据上述检查结果进行修复。")
        status = 1
    
    # 提供建议
    provide_recommendations()
    
    return status

if __name__ == "__main__":
    sys.exit(main())
