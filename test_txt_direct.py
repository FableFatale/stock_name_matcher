#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试TXT文件加载功能
"""

import sys
import os
import logging
from local_stock_data import LocalStockData

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_txt_loading():
    """直接测试TXT文件加载"""
    print("🧪 直接测试TXT文件加载")
    print("=" * 50)
    
    try:
        # 创建LocalStockData实例
        stock_data = LocalStockData()
        
        # 直接测试TXT文件加载
        txt_file = "all_stocks_20250616.txt"
        if os.path.exists(txt_file):
            print(f"📁 找到TXT文件: {txt_file}")
            
            # 直接调用TXT加载方法
            data = stock_data._load_txt_stock_data(txt_file)
            
            if data is not None and not data.empty:
                print(f"✅ TXT文件加载成功!")
                print(f"✅ 股票数量: {len(data):,}")
                print(f"✅ 数据列: {list(data.columns)}")
                
                # 显示前几只股票
                print("\n📊 前10只股票:")
                for i, row in data.head(10).iterrows():
                    print(f"   {row['代码']}: {row['名称']}")
                
                # 测试搜索功能
                print("\n🔍 测试搜索功能:")
                test_codes = ['000001', '600036', '300059']
                for code in test_codes:
                    result = data[data['代码'] == code]
                    if not result.empty:
                        name = result.iloc[0]['名称']
                        print(f"   ✅ {code}: {name}")
                    else:
                        print(f"   ❌ {code}: 未找到")
                
                # 市场分布统计
                print("\n📈 市场分布:")
                market_stats = {}
                for code in data['代码']:
                    code_str = str(code)
                    if code_str.startswith(('600', '601', '603', '605', '688')):
                        market_stats['沪市'] = market_stats.get('沪市', 0) + 1
                    elif code_str.startswith(('000', '001', '002', '003', '300')):
                        market_stats['深市'] = market_stats.get('深市', 0) + 1
                    elif code_str.startswith(('8', '4')) and len(code_str) == 6:
                        market_stats['北交所'] = market_stats.get('北交所', 0) + 1
                    else:
                        market_stats['其他'] = market_stats.get('其他', 0) + 1
                
                for market, count in market_stats.items():
                    print(f"   - {market}: {count:,} 只")
                
                return True
            else:
                print("❌ TXT文件加载失败")
                return False
        else:
            print(f"❌ 未找到TXT文件: {txt_file}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        logger.exception("详细错误信息:")
        return False

if __name__ == "__main__":
    success = test_direct_txt_loading()
    if success:
        print("\n✅ TXT文件加载测试成功!")
    else:
        print("\n❌ TXT文件加载测试失败!")
    sys.exit(0 if success else 1)
