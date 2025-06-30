#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的API数据源
"""

from stock_name_matcher import StockNameMatcher
import time

def test_new_apis():
    """测试新增的API"""
    new_apis = ['netease', 'xueqiu']
    test_code = "'000001"
    
    print("🧪 测试新增API数据源")
    print("="*60)
    
    for api in new_apis:
        print(f"\n🔧 测试 {api.upper()} API...")
        try:
            start_time = time.time()
            matcher = StockNameMatcher(api_source=api)
            load_time = time.time() - start_time
            
            print(f"   📊 数据加载: {len(matcher.stock_list)} 只股票")
            print(f"   ⏱️ 加载时间: {load_time:.2f}秒")
            
            # 测试匹配功能
            result = matcher.match_stock_code(test_code)
            status = result.get('匹配状态', '未知')
            name = result.get('股票名称', 'N/A')
            price = result.get('当前价格', 0)
            
            if status == '匹配成功':
                print(f"   ✅ 匹配测试: {status}")
                print(f"   📈 股票信息: {name} - ¥{price}")
            else:
                print(f"   ❌ 匹配测试: {status}")
            
            # 显示前3只股票信息
            print(f"   📋 前3只股票:")
            for i, (_, row) in enumerate(matcher.stock_list.head(3).iterrows()):
                code = row.get('代码', 'N/A')
                name = row.get('名称', 'N/A')
                price = row.get('最新价', 0)
                print(f"      {i+1}. {code} - {name} - ¥{price}")
                
        except Exception as e:
            print(f"   ❌ {api.upper()} API 测试失败: {str(e)[:80]}...")

def test_all_apis_comparison():
    """对比所有API的性能"""
    print(f"\n{'='*60}")
    print("📊 所有API性能对比")
    print(f"{'='*60}")
    
    apis = ['akshare', 'sina', 'tencent', 'eastmoney', 'netease', 'xueqiu', 'local']
    test_code = "'000001"
    
    results = {}
    
    for api in apis:
        print(f"\n测试 {api.upper()}...")
        try:
            start_time = time.time()
            matcher = StockNameMatcher(api_source=api)
            load_time = time.time() - start_time
            
            # 测试匹配
            match_start = time.time()
            result = matcher.match_stock_code(test_code)
            match_time = time.time() - match_start
            
            results[api] = {
                'stock_count': len(matcher.stock_list),
                'load_time': load_time,
                'match_time': match_time,
                'match_success': result.get('匹配状态') == '匹配成功',
                'stock_name': result.get('股票名称', 'N/A'),
                'price': result.get('当前价格', 0)
            }
            
        except Exception as e:
            results[api] = {
                'error': str(e)[:50] + '...'
            }
    
    # 显示对比结果
    print(f"\n📊 性能对比结果:")
    print(f"{'API源':<12} {'股票数量':<8} {'加载时间':<8} {'匹配时间':<8} {'匹配成功':<8} {'股票名称'}")
    print("-" * 80)
    
    for api, result in results.items():
        if 'error' not in result:
            count = result['stock_count']
            load_time = f"{result['load_time']:.2f}s"
            match_time = f"{result['match_time']:.3f}s"
            success = "✅" if result['match_success'] else "❌"
            name = result['stock_name'][:10]
            
            print(f"{api.upper():<12} {count:<8} {load_time:<8} {match_time:<8} {success:<8} {name}")
        else:
            print(f"{api.upper():<12} {'ERROR':<8} {'-':<8} {'-':<8} {'❌':<8} {result['error'][:20]}")
    
    # 推荐最佳API
    print(f"\n💡 推荐排序:")
    working_apis = [(api, result) for api, result in results.items() 
                   if 'error' not in result and result['match_success']]
    
    if working_apis:
        # 按股票数量和加载时间排序
        working_apis.sort(key=lambda x: (-x[1]['stock_count'], x[1]['load_time']))
        
        for i, (api, result) in enumerate(working_apis[:5]):
            rank_icon = ["🏆", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            print(f"   {rank_icon} {api.upper()}: {result['stock_count']}只股票, {result['load_time']:.2f}s加载")

if __name__ == "__main__":
    test_new_apis()
    test_all_apis_comparison()
