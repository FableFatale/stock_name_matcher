#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的TXT文件读取测试
"""

import os

def simple_txt_test():
    """简单测试TXT文件读取"""
    txt_file = "all_stocks_20250616.txt"
    
    print(f"🧪 测试TXT文件: {txt_file}")
    
    if not os.path.exists(txt_file):
        print(f"❌ 文件不存在: {txt_file}")
        return False
    
    try:
        # 获取文件信息
        size = os.path.getsize(txt_file)
        print(f"📁 文件大小: {size:,} 字节")
        
        # 读取前几行
        stock_count = 0
        valid_count = 0
        
        print("📊 读取文件内容...")
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                stock_count += 1
                
                # 解析股票代码和名称
                if ',' in line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        code = parts[0].strip()
                        name = parts[1].strip()
                        
                        # 验证股票代码格式
                        if len(code) == 6 and code.isdigit():
                            valid_count += 1
                            
                            # 显示前10个有效股票
                            if valid_count <= 10:
                                print(f"   {code}: {name}")
                
                # 限制读取行数以避免长时间等待
                if line_num > 100:
                    print(f"   ... (为节省时间，只读取前100行)")
                    break
        
        print(f"✅ 处理完成!")
        print(f"✅ 总行数: {line_num:,}")
        print(f"✅ 股票条目: {stock_count:,}")
        print(f"✅ 有效股票: {valid_count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取文件时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = simple_txt_test()
    if success:
        print("\n✅ 简单TXT测试成功!")
    else:
        print("\n❌ 简单TXT测试失败!")
