#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用TXT格式股票列表的演示脚本
展示如何使用 all_stocks_20250616.txt 文件进行股票匹配
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

def demonstrate_txt_usage():
    """演示TXT格式股票数据的使用"""
    print("=" * 70)
    print("📈 使用TXT格式股票列表演示")
    print("=" * 70)
    
    try:
        # 1. 初始化股票数据（会自动使用TXT文件如果没有CSV文件）
        print("\n🔧 1. 初始化股票数据")
        print("-" * 50)
        
        stock_data = LocalStockData(use_offline_data=True)
        info = stock_data.get_data_info()
        
        print(f"✅ 数据源: {info['数据源']}")
        print(f"✅ 总股票数: {info['总股票数']:,}")
        
        if '市场分布' in info:
            print("✅ 市场分布:")
            for market, count in info['市场分布'].items():
                print(f"   - {market}: {count:,} 只")
        
        # 2. 演示股票代码查询
        print("\n🔍 2. 股票代码查询演示")
        print("-" * 50)
        
        test_codes = ['000001', '000002', '600036', '600519', '300059', '688001']
        found_count = 0
        
        for code in test_codes:
            result = stock_data.search_by_code(code)
            if result is not None and not result.empty:
                name = result.iloc[0]['名称']
                print(f"✅ {code}: {name}")
                found_count += 1
            else:
                print(f"❌ {code}: 未找到")
        
        print(f"\n📊 查询结果: {found_count}/{len(test_codes)} 个代码找到匹配")
        
        # 3. 演示股票名称查询
        print("\n🏷️ 3. 股票名称查询演示")
        print("-" * 50)
        
        test_names = ['平安银行', '万科A', '招商银行', '贵州茅台', '中兴通讯', '比亚迪']
        found_count = 0
        
        for name in test_names:
            result = stock_data.search_by_name(name)
            if result is not None and not result.empty:
                code = result.iloc[0]['代码']
                matched_name = result.iloc[0]['名称']
                print(f"✅ {name}: {code} ({matched_name})")
                found_count += 1
            else:
                print(f"❌ {name}: 未找到")
        
        print(f"\n📊 查询结果: {found_count}/{len(test_names)} 个名称找到匹配")
        
        # 4. 演示模糊搜索
        print("\n🔎 4. 模糊搜索演示")
        print("-" * 50)
        
        fuzzy_patterns = ['00000', '60003', '30001']
        for pattern in fuzzy_patterns:
            result = stock_data.search_by_code_fuzzy(pattern)
            if result is not None and not result.empty:
                count = len(result)
                print(f"✅ 模式 '{pattern}': 找到 {count} 只股票")
                # 显示前3个结果
                for i, row in result.head(3).iterrows():
                    print(f"   - {row['代码']}: {row['名称']}")
                if count > 3:
                    print(f"   ... 还有 {count - 3} 只股票")
            else:
                print(f"❌ 模式 '{pattern}': 未找到匹配")
        
        # 5. 演示市场分类
        print("\n🏢 5. 市场分类演示")
        print("-" * 50)
        
        markets = ['沪市', '深市', '北交所']
        for market in markets:
            result = stock_data.get_stocks_by_market(market)
            if result is not None and not result.empty:
                count = len(result)
                print(f"✅ {market}: {count:,} 只股票")
                
                # 显示一些示例
                sample_size = min(5, count)
                print(f"   示例 ({sample_size} 只):")
                for i, row in result.head(sample_size).iterrows():
                    print(f"   - {row['代码']}: {row['名称']}")
            else:
                print(f"❌ {market}: 未找到股票")
        
        # 6. 演示数据导出
        print("\n💾 6. 数据导出演示")
        print("-" * 50)
        
        # 导出完整数据
        export_file = f"exported_stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        success = stock_data.export_to_csv(export_file)
        
        if success and os.path.exists(export_file):
            size = os.path.getsize(export_file)
            print(f"✅ 数据导出成功: {export_file}")
            print(f"✅ 文件大小: {size:,} 字节")
            
            # 清理导出文件
            os.remove(export_file)
            print(f"✅ 清理导出文件: {export_file}")
        else:
            print(f"❌ 数据导出失败")
        
        # 7. 显示文件信息
        print("\n📁 7. 可用数据文件信息")
        print("-" * 50)
        
        files_info = stock_data.get_available_data_files()
        
        print("📄 CSV文件:")
        if files_info['csv_files']:
            for file_info in files_info['csv_files']:
                size_mb = file_info['size'] / 1024 / 1024
                mod_time = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   - {file_info['name']} ({size_mb:.2f} MB, 修改时间: {mod_time})")
        else:
            print("   - 无CSV文件")
        
        print("\n📄 TXT文件:")
        if files_info['txt_files']:
            for file_info in files_info['txt_files']:
                size_mb = file_info['size'] / 1024 / 1024
                mod_time = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   - {file_info['name']} ({size_mb:.2f} MB, 修改时间: {mod_time})")
        else:
            print("   - 无TXT文件")
        
        if files_info['recommended']:
            rec_file = files_info['recommended']
            print(f"\n🎯 推荐使用: {rec_file['name']}")
        
        print("\n" + "=" * 70)
        print("🎉 TXT格式股票列表演示完成！")
        print("=" * 70)
        
        # 总结
        print(f"\n📋 总结:")
        print(f"   - 成功加载了 {info['总股票数']:,} 只股票")
        print(f"   - 数据源: {info['数据源']}")
        print(f"   - 支持代码查询、名称查询、模糊搜索、市场分类等功能")
        print(f"   - 可以导出为CSV格式供其他工具使用")
        
        return True
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {str(e)}")
        print(f"\n❌ 演示失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = demonstrate_txt_usage()
    
    if success:
        print("\n✅ 演示成功完成！")
        print("\n💡 提示:")
        print("   - 您的 all_stocks_20250616.txt 文件已被系统识别并可以使用")
        print("   - 可以在股票匹配器中直接使用这个数据源")
        print("   - 如需要，可以使用 convert_txt_to_csv() 方法转换为CSV格式")
        return 0
    else:
        print("\n❌ 演示失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
