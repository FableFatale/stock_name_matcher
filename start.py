#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票名称匹配器启动脚本
提供简单的交互式界面
"""

import os
import sys
import subprocess

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 股票名称匹配器")
    print("=" * 60)
    print("智能股票名称匹配工具")
    print("支持Excel/CSV文件，使用免费AKShare API")
    print("=" * 60)

def show_menu():
    """显示主菜单"""
    print("\n📋 请选择操作:")
    print("1. 🔧 检查环境配置")
    print("2. 📦 安装依赖包")
    print("3. 🎯 快速开始演示")
    print("4. 🧪 运行测试")
    print("5. 📊 匹配股票名称")
    print("6. 📖 查看帮助")
    print("7. 🚪 退出")
    print("-" * 40)

def run_command(command):
    """运行命令"""
    try:
        result = subprocess.run([sys.executable] + command.split(), 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行命令失败: {e}")
        return False

def get_file_path():
    """获取文件路径"""
    while True:
        file_path = input("\n📁 请输入Excel或CSV文件路径: ").strip()
        if not file_path:
            print("❌ 文件路径不能为空")
            continue
        
        # 去除引号
        file_path = file_path.strip('"\'')
        
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"❌ 文件不存在: {file_path}")
            retry = input("是否重新输入? (y/n): ").strip().lower()
            if retry != 'y':
                return None

def main():
    """主函数"""
    print_banner()
    
    while True:
        show_menu()
        choice = input("请输入选择 (1-7): ").strip()
        
        if choice == '1':
            print("\n🔧 检查环境配置...")
            run_command("check_setup.py")
            
        elif choice == '2':
            print("\n📦 安装依赖包...")
            run_command("install_dependencies.py")
            
        elif choice == '3':
            print("\n🎯 快速开始演示...")
            run_command("quick_start.py")
            
        elif choice == '4':
            print("\n🧪 运行测试...")
            run_command("test_stock_matcher.py")
            
        elif choice == '5':
            print("\n📊 匹配股票名称...")
            file_path = get_file_path()
            if file_path:
                print(f"正在处理文件: {file_path}")
                success = run_command(f"stock_name_matcher.py \"{file_path}\"")
                if success:
                    print("✅ 处理完成！")
                else:
                    print("❌ 处理失败，请检查错误信息")
            
        elif choice == '6':
            print("\n📖 帮助信息:")
            print("\n基本用法:")
            print("  python stock_name_matcher.py your_file.xlsx")
            print("\n指定输出文件:")
            print("  python stock_name_matcher.py your_file.xlsx -o results.csv")
            print("\n指定列名:")
            print("  python stock_name_matcher.py your_file.xlsx -n '股票名称' -p '价格'")
            print("\n更多信息请查看:")
            print("  README.md")
            print("  股票名称匹配器使用说明.md")
            
        elif choice == '7':
            print("\n👋 感谢使用股票名称匹配器！")
            break
            
        else:
            print("❌ 无效选择，请输入1-7")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见！")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        input("按回车键退出...")
