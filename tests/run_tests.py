#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器 - 运行所有测试
"""

import sys
import os
import subprocess
import time

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test(test_file, description):
    """运行单个测试"""
    print(f"\n{'='*60}")
    print(f"🧪 运行测试: {description}")
    print(f"📁 文件: {test_file}")
    print('='*60)
    
    try:
        # 运行测试
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=120)
        
        if result.returncode == 0:
            print("✅ 测试通过")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("❌ 测试失败")
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时")
        return False
    except Exception as e:
        print(f"💥 运行测试时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 股票代码补全系统 - 测试套件")
    print("=" * 60)
    
    # 测试列表
    tests = [
        ("tests/test_file_format.py", "文件格式检测测试"),
        ("tests/test_upload_simulation.py", "文件上传模拟测试"),
        ("tests/test_enhanced_features.py", "增强功能测试"),
        ("tests/test_upload_request.py", "Web上传请求测试"),
        ("tests/test_web_app.py", "完整Web应用测试"),
    ]
    
    # 检查测试文件是否存在
    available_tests = []
    for test_file, description in tests:
        if os.path.exists(test_file):
            available_tests.append((test_file, description))
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
    
    if not available_tests:
        print("❌ 没有找到可运行的测试文件")
        return
    
    print(f"\n📋 找到 {len(available_tests)} 个测试")
    
    # 运行测试
    passed = 0
    failed = 0
    
    for test_file, description in available_tests:
        success = run_test(test_file, description)
        if success:
            passed += 1
        else:
            failed += 1
        
        # 测试间隔
        time.sleep(1)
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print('='*60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！")
    else:
        print(f"\n💥 有 {failed} 个测试失败")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
