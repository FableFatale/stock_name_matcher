#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取器演示脚本
展示如何获取和使用离线股票数据
"""

import sys
import os
from stock_data_fetcher import StockDataFetcher
from local_stock_data import LocalStockData
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_fetch_stock_data():
    """演示获取股票数据"""
    print("🚀 股票数据获取器演示")
    print("=" * 50)
    
    # 创建数据获取器
    fetcher = StockDataFetcher()
    
    try:
        print("1️⃣ 获取股票基本信息...")
        basic_data = fetcher.get_stock_basic_info()
        
        if basic_data is not None:
            print(f"✅ 成功获取 {len(basic_data)} 只股票的基本信息")
            
            # 显示前几条数据
            print("\n📋 前5条数据预览:")
            print(basic_data.head().to_string(index=False))
            
            # 保存数据
            print("\n💾 保存数据...")
            filename = "demo_stock_list.csv"
            filepath = fetcher.save_stock_data(basic_data, filename)
            
            if filepath:
                print(f"✅ 数据已保存到: {filepath}")
                
                # 显示统计信息
                print("\n📊 数据统计:")
                stats = fetcher.get_statistics(basic_data)
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    else:
                        print(f"  {key}: {value}")
            
        else:
            print("❌ 获取股票数据失败")
            
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")

def demo_local_stock_data():
    """演示本地股票数据使用"""
    print("\n🏠 本地股票数据演示")
    print("=" * 50)
    
    try:
        # 使用离线数据
        print("1️⃣ 加载离线股票数据...")
        local_data = LocalStockData(use_offline_data=True)
        
        # 获取数据信息
        info = local_data.get_data_info()
        print(f"✅ 数据加载成功")
        print(f"  数据源: {info['数据源']}")
        print(f"  总股票数: {info['总股票数']}")
        
        # 搜索示例
        print("\n🔍 搜索演示:")
        
        # 按代码搜索
        print("  按代码搜索 '000001':")
        result = local_data.search_by_code('000001')
        if result is not None:
            print(f"    找到 {len(result)} 条结果")
            print(f"    {result[['代码', '名称']].to_string(index=False)}")
        
        # 按名称搜索
        print("\n  按名称搜索 '平安':")
        result = local_data.search_by_name('平安')
        if result is not None:
            print(f"    找到 {len(result)} 条结果")
            print(f"    {result[['代码', '名称']].head().to_string(index=False)}")
        
        # 按市场搜索
        print("\n  获取上海市场股票:")
        sh_stocks = local_data.get_stocks_by_market('上海')
        if sh_stocks is not None:
            print(f"    上海市场共有 {len(sh_stocks)} 只股票")
            print(f"    前3只: {sh_stocks[['代码', '名称']].head(3).to_string(index=False)}")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {str(e)}")

def demo_comparison():
    """演示数据对比"""
    print("\n🔄 数据对比演示")
    print("=" * 50)
    
    try:
        # 使用示例数据
        sample_data = LocalStockData(use_offline_data=False)
        sample_info = sample_data.get_data_info()
        
        # 使用离线数据
        offline_data = LocalStockData(use_offline_data=True)
        offline_info = offline_data.get_data_info()
        
        print("📊 数据源对比:")
        print(f"  示例数据: {sample_info['总股票数']} 只股票")
        print(f"  离线数据: {offline_info['总股票数']} 只股票")
        
        # 如果离线数据更多，说明获取成功
        if offline_info['总股票数'] > sample_info['总股票数']:
            print("✅ 离线数据包含更多股票，建议使用离线数据")
        else:
            print("ℹ️ 当前使用示例数据")
            
    except Exception as e:
        print(f"❌ 对比过程中发生错误: {str(e)}")

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示")
    print("=" * 50)
    
    local_data = LocalStockData(use_offline_data=True)
    
    while True:
        print("\n请选择操作:")
        print("1. 按股票代码搜索")
        print("2. 按股票名称搜索")
        print("3. 查看数据统计")
        print("4. 导出数据")
        print("0. 退出")
        
        try:
            choice = input("请输入选择 (0-4): ").strip()
            
            if choice == '0':
                print("👋 再见!")
                break
            elif choice == '1':
                code = input("请输入股票代码: ").strip()
                result = local_data.search_by_code(code)
                if result is not None:
                    print(f"找到 {len(result)} 条结果:")
                    print(result[['代码', '名称', '最新价']].to_string(index=False))
                else:
                    print("未找到匹配的股票")
            elif choice == '2':
                name = input("请输入股票名称关键词: ").strip()
                result = local_data.search_by_name(name)
                if result is not None:
                    print(f"找到 {len(result)} 条结果:")
                    print(result[['代码', '名称', '最新价']].head(10).to_string(index=False))
                    if len(result) > 10:
                        print(f"... 还有 {len(result) - 10} 条结果")
                else:
                    print("未找到匹配的股票")
            elif choice == '3':
                info = local_data.get_data_info()
                print("📊 数据统计:")
                for key, value in info.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    else:
                        print(f"  {key}: {value}")
            elif choice == '4':
                filename = input("请输入导出文件名 (默认: exported_data.csv): ").strip()
                if not filename:
                    filename = "exported_data.csv"
                success = local_data.export_to_csv(filename)
                if success:
                    print(f"✅ 数据已导出到: {filename}")
                else:
                    print("❌ 导出失败")
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 操作过程中发生错误: {str(e)}")

def main():
    """主函数"""
    print("🎯 股票数据获取器完整演示")
    print("=" * 60)
    
    # 检查是否有网络连接来获取数据
    print("ℹ️ 注意: 首次运行需要网络连接来获取股票数据")
    print("ℹ️ 获取完成后可以离线使用")
    
    try:
        # 演示获取数据
        demo_fetch_stock_data()
        
        # 演示本地数据使用
        demo_local_stock_data()
        
        # 演示数据对比
        demo_comparison()
        
        # 交互式演示
        choice = input("\n是否进入交互式演示? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_demo()
        
        print("\n🎉 演示完成!")
        
    except KeyboardInterrupt:
        print("\n👋 演示被中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()
