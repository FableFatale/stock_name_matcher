#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有API数据源
"""

import logging
import time
from datetime import datetime
from stock_name_matcher import StockDataAPI

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_source(api_source):
    """测试单个API数据源"""
    print(f"\n{'='*60}")
    print(f"🧪 测试 {api_source.upper()} API")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        
        # 创建API管理器
        api_manager = StockDataAPI(api_source)
        
        # 加载股票数据
        stock_list = api_manager.load_stock_list()
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if stock_list is not None and len(stock_list) > 0:
            print(f"✅ {api_source.upper()} API 测试成功")
            print(f"   📊 股票数量: {len(stock_list)}")
            print(f"   ⏱️ 加载时间: {load_time:.2f}秒")
            print(f"   📋 列名: {list(stock_list.columns)}")
            
            # 显示前5只股票的信息
            print(f"\n   📈 前5只股票信息:")
            for i, (_, row) in enumerate(stock_list.head().iterrows()):
                code = row.get('代码', 'N/A')
                name = row.get('名称', 'N/A')
                price = row.get('最新价', 0)
                print(f"   {i+1}. {code} - {name} - ¥{price}")
            
            # 测试特定股票代码
            test_codes = ['000001', '000002', '600000', '600036', '300001']
            print(f"\n   🔍 测试特定股票代码:")
            found_count = 0
            for code in test_codes:
                matches = stock_list[stock_list['代码'] == code]
                if len(matches) > 0:
                    stock_info = matches.iloc[0]
                    print(f"   ✅ {code}: {stock_info['名称']} - ¥{stock_info.get('最新价', 0)}")
                    found_count += 1
                else:
                    print(f"   ❌ {code}: 未找到")
            
            print(f"\n   📊 测试结果: {found_count}/{len(test_codes)} 只股票找到")
            
            return {
                'status': 'success',
                'count': len(stock_list),
                'load_time': load_time,
                'found_test_stocks': found_count,
                'total_test_stocks': len(test_codes)
            }
        else:
            print(f"❌ {api_source.upper()} API 测试失败: 未获取到数据")
            return {
                'status': 'failed',
                'error': '未获取到数据',
                'load_time': load_time
            }
            
    except Exception as e:
        print(f"❌ {api_source.upper()} API 测试异常: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'load_time': 0
        }

def test_stock_matching():
    """测试股票匹配功能"""
    print(f"\n{'='*60}")
    print(f"🎯 测试股票匹配功能")
    print(f"{'='*60}")
    
    from stock_name_matcher import StockNameMatcher
    
    # 测试不同API源的匹配功能
    api_sources = ['akshare', 'sina', 'tencent', 'eastmoney', 'local']
    test_codes = ["'000037", "'000603", "'600000", "'600036"]
    
    results = {}
    
    for api_source in api_sources:
        print(f"\n🔧 使用 {api_source.upper()} 进行匹配测试...")
        try:
            matcher = StockNameMatcher(api_source=api_source)
            
            api_results = []
            for code in test_codes:
                result = matcher.match_stock_code(code)
                status = result.get('匹配状态', '未知')
                name = result.get('股票名称', 'N/A')
                print(f"   {code} -> {status} ({name})")
                api_results.append(status == '匹配成功')
            
            success_rate = sum(api_results) / len(api_results) * 100
            results[api_source] = {
                'success_rate': success_rate,
                'results': api_results
            }
            print(f"   成功率: {success_rate:.1f}%")
            
        except Exception as e:
            print(f"   ❌ {api_source} 匹配测试失败: {e}")
            results[api_source] = {
                'success_rate': 0,
                'error': str(e)
            }
    
    return results

def main():
    """主函数"""
    print("🚀 股票数据API全面测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试所有API数据源
    api_sources = ['akshare', 'sina', 'tencent', 'eastmoney', 'local']
    api_results = {}
    
    for api_source in api_sources:
        result = test_api_source(api_source)
        api_results[api_source] = result
        
        # 在API测试之间稍作停顿，避免请求过快
        if api_source != 'local':
            time.sleep(2)
    
    # 测试股票匹配功能
    matching_results = test_stock_matching()
    
    # 生成总结报告
    print(f"\n{'='*60}")
    print(f"📊 测试总结报告")
    print(f"{'='*60}")
    
    print(f"\n🔌 API数据源测试结果:")
    for api_source, result in api_results.items():
        status = result.get('status', 'unknown')
        if status == 'success':
            count = result.get('count', 0)
            load_time = result.get('load_time', 0)
            print(f"   ✅ {api_source.upper()}: {count} 只股票, {load_time:.2f}秒")
        else:
            error = result.get('error', '未知错误')
            print(f"   ❌ {api_source.upper()}: {error}")
    
    print(f"\n🎯 股票匹配测试结果:")
    for api_source, result in matching_results.items():
        if 'success_rate' in result:
            rate = result['success_rate']
            if rate >= 75:
                status_icon = "✅"
            elif rate >= 50:
                status_icon = "⚠️"
            else:
                status_icon = "❌"
            print(f"   {status_icon} {api_source.upper()}: {rate:.1f}% 成功率")
        else:
            print(f"   ❌ {api_source.upper()}: {result.get('error', '测试失败')}")
    
    # 推荐最佳API
    print(f"\n💡 推荐使用:")
    working_apis = [api for api, result in api_results.items() if result.get('status') == 'success']
    if working_apis:
        best_api = max(working_apis, key=lambda x: api_results[x].get('count', 0))
        print(f"   🏆 推荐: {best_api.upper()} (数据最完整)")
        
        if len(working_apis) > 1:
            print(f"   🔄 备选: {', '.join([api.upper() for api in working_apis if api != best_api])}")
    else:
        print(f"   ⚠️ 建议使用 LOCAL (本地数据源)")
    
    print(f"\n🎉 测试完成!")

if __name__ == "__main__":
    main()
