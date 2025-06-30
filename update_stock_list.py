#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新股票列表脚本
从API获取最新的股票代码和名称，保存为离线数据
"""

import sys
import os
import argparse
from datetime import datetime
from stock_data_fetcher import StockDataFetcher
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_update.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='更新股票列表')
    parser.add_argument('--no-backup', action='store_true', help='不备份现有数据')
    parser.add_argument('--basic-only', action='store_true', help='只获取基本信息（代码和名称）')
    parser.add_argument('--by-market', action='store_true', help='按市场分别获取数据')
    parser.add_argument('--output', '-o', help='指定输出文件名')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    # 创建数据获取器
    fetcher = StockDataFetcher()
    
    try:
        logger.info("=" * 50)
        logger.info("开始更新股票列表")
        logger.info(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        if args.by_market:
            # 按市场分别获取
            logger.info("按市场分别获取股票数据...")
            markets_data = fetcher.fetch_stocks_by_market()
            
            for market, data in markets_data.items():
                if data is not None and not data.empty:
                    filename = f"stock_list_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    if args.output:
                        filename = f"{args.output}_{market}.csv"
                    
                    filepath = fetcher.save_stock_data(data, filename)
                    if filepath:
                        logger.info(f"{market}: 保存了 {len(data)} 只股票到 {filename}")
        
        elif args.basic_only:
            # 只获取基本信息
            logger.info("获取股票基本信息...")
            basic_data = fetcher.get_stock_basic_info()
            
            if basic_data is not None:
                filename = args.output if args.output else "stock_basic_info.csv"
                filepath = fetcher.save_stock_data(basic_data, filename)
                
                if filepath:
                    logger.info(f"基本信息: 保存了 {len(basic_data)} 只股票到 {filename}")
                    
                    # 显示统计信息
                    if args.stats:
                        stats = fetcher.get_statistics(basic_data)
                        print_statistics(stats)
            else:
                logger.error("获取股票基本信息失败")
                return 1
        
        else:
            # 标准更新流程
            success = fetcher.update_stock_list(save_backup=not args.no_backup)
            
            if success:
                logger.info("股票列表更新成功！")
                
                # 显示统计信息
                if args.stats:
                    stats = fetcher.get_statistics()
                    print_statistics(stats)
            else:
                logger.error("股票列表更新失败")
                return 1
        
        logger.info("=" * 50)
        logger.info("股票列表更新完成")
        logger.info("=" * 50)
        return 0
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"更新过程中发生错误: {str(e)}")
        return 1

def print_statistics(stats):
    """打印统计信息"""
    print("\n" + "=" * 30)
    print("📊 股票数据统计")
    print("=" * 30)
    
    print(f"📈 总股票数: {stats.get('总股票数', 0)}")
    print(f"🕒 更新时间: {stats.get('数据更新时间', '未知')}")
    
    # 市场分布
    market_dist = stats.get('市场分布', {})
    if market_dist:
        print("\n🏢 市场分布:")
        for market, count in market_dist.items():
            print(f"  {market}: {count} 只")
    
    # 类型分布
    type_dist = stats.get('类型分布', {})
    if type_dist:
        print("\n📋 类型分布:")
        for stock_type, count in type_dist.items():
            print(f"  {stock_type}: {count} 只")
    
    print("=" * 30)

def check_dependencies():
    """检查依赖"""
    try:
        import akshare
        import pandas
        logger.info("✅ 依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖: {e}")
        logger.error("请运行: pip install akshare pandas")
        return False

if __name__ == "__main__":
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行主程序
    exit_code = main()
    sys.exit(exit_code)
