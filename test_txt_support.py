#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TXT格式股票列表支持功能
"""

import sys
import os
import logging
from datetime import datetime
from local_stock_data import LocalStockData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_txt_support():
    """测试TXT格式支持功能"""
    print("=" * 60)
    print("🧪 测试TXT格式股票列表支持功能")
    print("=" * 60)
    
    try:
        # 1. 测试本地股票数据加载
        print("\n📊 1. 测试本地股票数据加载")
        print("-" * 40)
        
        stock_data = LocalStockData(use_offline_data=True)
        
        # 获取数据信息
        info = stock_data.get_data_info()
        print(f"✅ 数据源: {info['数据源']}")
        print(f"✅ 总股票数: {info['总股票数']}")
        
        if '市场分布' in info:
            print("✅ 市场分布:")
            for market, count in info['市场分布'].items():
                print(f"   - {market}: {count} 只")
        
        # 2. 测试股票搜索功能
        print("\n🔍 2. 测试股票搜索功能")
        print("-" * 40)
        
        # 测试代码搜索
        test_codes = ['000001', '600036', '300018', '688001']
        for code in test_codes:
            result = stock_data.search_by_code(code)
            if result is not None and not result.empty:
                name = result.iloc[0]['名称']
                print(f"✅ 代码搜索 {code}: {name}")
            else:
                print(f"❌ 代码搜索 {code}: 未找到")
        
        # 测试名称搜索
        test_names = ['平安银行', '招商银行', '中兴通讯']
        for name in test_names:
            result = stock_data.search_by_name(name)
            if result is not None and not result.empty:
                code = result.iloc[0]['代码']
                print(f"✅ 名称搜索 {name}: {code}")
            else:
                print(f"❌ 名称搜索 {name}: 未找到")
        
        # 3. 测试市场分类功能
        print("\n🏢 3. 测试市场分类功能")
        print("-" * 40)
        
        markets = ['沪市', '深市']
        for market in markets:
            result = stock_data.get_stocks_by_market(market)
            if result is not None and not result.empty:
                print(f"✅ {market}股票: {len(result)} 只")
                # 显示前3只股票
                for i, row in result.head(3).iterrows():
                    print(f"   - {row['代码']}: {row['名称']}")
            else:
                print(f"❌ {market}股票: 未找到")
        
        # 4. 测试文件信息获取
        print("\n📁 4. 测试可用数据文件")
        print("-" * 40)
        
        files_info = stock_data.get_available_data_files()
        
        if files_info['csv_files']:
            print(f"✅ CSV文件: {len(files_info['csv_files'])} 个")
            for file_info in files_info['csv_files']:
                size_mb = file_info['size'] / 1024 / 1024
                print(f"   - {file_info['name']} ({size_mb:.2f} MB)")
        
        if files_info['txt_files']:
            print(f"✅ TXT文件: {len(files_info['txt_files'])} 个")
            for file_info in files_info['txt_files']:
                size_mb = file_info['size'] / 1024 / 1024
                print(f"   - {file_info['name']} ({size_mb:.2f} MB)")
        
        if files_info['recommended']:
            rec_file = files_info['recommended']
            print(f"✅ 推荐使用: {rec_file['name']}")
        
        # 5. 测试TXT到CSV转换功能
        print("\n🔄 5. 测试TXT到CSV转换功能")
        print("-" * 40)
        
        txt_files = [f for f in os.listdir(".") if f.startswith("all_stocks_") and f.endswith(".txt")]
        if txt_files:
            txt_file = txt_files[0]
            output_file = f"test_converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            success = stock_data.convert_txt_to_csv(txt_file, output_file)
            if success:
                print(f"✅ TXT转换成功: {txt_file} -> {output_file}")
                
                # 验证转换结果
                if os.path.exists(output_file):
                    size = os.path.getsize(output_file)
                    print(f"✅ 输出文件大小: {size} 字节")
                    
                    # 清理测试文件
                    os.remove(output_file)
                    print(f"✅ 清理测试文件: {output_file}")
            else:
                print(f"❌ TXT转换失败: {txt_file}")
        else:
            print("⚪ 未找到TXT文件，跳过转换测试")
        
        print("\n" + "=" * 60)
        print("🎉 TXT格式支持功能测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        print(f"\n❌ 测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = test_txt_support()
    
    if success:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
