#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
比较优化前后的处理速度
"""

import os
import sys
import time
import pandas as pd
import logging
from datetime import datetime
from stock_name_matcher import StockNameMatcher

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data(size: int = 50) -> str:
    """创建测试数据"""
    logger.info(f"创建 {size} 条测试数据...")
    
    # 常见的股票代码
    test_codes = [
        '000001', '000002', '000037', '000603', '000798',
        '600000', '600036', '600519', '600887', '601318',
        '002415', '002594', '002714', '300059', '300750'
    ]
    
    # 生成测试数据
    data = []
    for i in range(size):
        code = test_codes[i % len(test_codes)]
        # 添加一些变化，模拟真实数据
        if i % 3 == 0:
            code = f"'{code}"  # 带引号
        elif i % 5 == 0:
            code = f" {code} "  # 带空格
        
        data.append({
            '股票代码': code,
            '参考价格': 10.0 + (i % 20)  # 模拟价格
        })
    
    # 保存测试文件
    test_file = f'performance_test_{size}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df = pd.DataFrame(data)
    df.to_csv(test_file, index=False, encoding='utf-8-sig')
    
    logger.info(f"测试数据已保存到: {test_file}")
    return test_file

def test_performance(test_file: str, use_optimization: bool = True) -> dict:
    """测试性能"""
    mode_name = "优化模式" if use_optimization else "标准模式"
    logger.info(f"🧪 开始测试 {mode_name}...")
    
    start_time = time.time()
    
    try:
        # 创建匹配器
        matcher = StockNameMatcher(api_source='local')  # 使用本地数据避免网络延迟
        
        # 处理文件
        output_file = matcher.process_stock_codes(
            test_file,
            use_optimization=use_optimization
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 读取结果统计
        result_df = pd.read_csv(output_file)
        total_count = len(result_df)
        success_count = len(result_df[result_df['匹配状态'].str.contains('匹配成功', na=False)])
        
        # 清理输出文件
        if os.path.exists(output_file):
            os.remove(output_file)
        
        return {
            'mode': mode_name,
            'processing_time': processing_time,
            'total_count': total_count,
            'success_count': success_count,
            'success_rate': success_count / total_count * 100 if total_count > 0 else 0,
            'avg_time_per_record': processing_time / total_count if total_count > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"{mode_name} 测试失败: {e}")
        return {
            'mode': mode_name,
            'error': str(e)
        }

def run_performance_comparison():
    """运行性能对比测试"""
    print("🚀 股票匹配性能测试")
    print("=" * 50)
    
    # 测试不同数据量
    test_sizes = [20, 50, 100]
    
    for size in test_sizes:
        print(f"\n📊 测试数据量: {size} 条记录")
        print("-" * 30)
        
        # 创建测试数据
        test_file = create_test_data(size)
        
        try:
            # 测试标准模式
            standard_result = test_performance(test_file, use_optimization=False)
            
            # 测试优化模式
            optimized_result = test_performance(test_file, use_optimization=True)
            
            # 显示结果
            if 'error' not in standard_result and 'error' not in optimized_result:
                print(f"📈 性能对比结果:")
                print(f"  标准模式: {standard_result['processing_time']:.2f}秒 "
                      f"(平均 {standard_result['avg_time_per_record']:.3f}秒/条)")
                print(f"  优化模式: {optimized_result['processing_time']:.2f}秒 "
                      f"(平均 {optimized_result['avg_time_per_record']:.3f}秒/条)")
                
                if standard_result['processing_time'] > 0:
                    speedup = standard_result['processing_time'] / optimized_result['processing_time']
                    print(f"  🎯 性能提升: {speedup:.1f}x 倍")
                    
                    time_saved = standard_result['processing_time'] - optimized_result['processing_time']
                    print(f"  ⏱️  节省时间: {time_saved:.2f}秒")
                
                print(f"  ✅ 成功率: 标准模式 {standard_result['success_rate']:.1f}%, "
                      f"优化模式 {optimized_result['success_rate']:.1f}%")
            else:
                if 'error' in standard_result:
                    print(f"❌ 标准模式测试失败: {standard_result['error']}")
                if 'error' in optimized_result:
                    print(f"❌ 优化模式测试失败: {optimized_result['error']}")
        
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)

def test_optimization_features():
    """测试优化功能特性"""
    print("\n🔧 测试优化功能特性")
    print("-" * 30)
    
    try:
        from performance_optimizer import PerformanceOptimizer
        from stock_name_matcher import StockNameMatcher
        
        # 创建测试实例
        matcher = StockNameMatcher(api_source='local')
        optimizer = PerformanceOptimizer(matcher)
        
        print("✅ 性能优化器导入成功")
        print(f"📊 默认配置:")
        print(f"  - 批处理大小: {optimizer.batch_size}")
        print(f"  - 最大工作线程: {optimizer.max_workers}")
        print(f"  - 缓存状态: {optimizer.get_cache_stats()}")
        
        # 测试缓存功能
        test_data = pd.DataFrame([
            {'股票代码': '000001', '参考价格': 10.0},
            {'股票代码': '000001', '参考价格': 10.0},  # 重复数据测试缓存
            {'股票代码': '600000', '参考价格': 15.0}
        ])
        
        print("\n🧪 测试缓存功能...")
        start_time = time.time()
        results = optimizer.optimize_stock_matching(test_data, False)
        end_time = time.time()
        
        print(f"✅ 缓存测试完成，耗时: {end_time - start_time:.3f}秒")
        print(f"📊 缓存统计: {optimizer.get_cache_stats()}")
        print(f"📋 处理结果: {len(results)} 条记录")
        
    except ImportError:
        print("❌ 性能优化器不可用")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🎯 股票匹配性能测试工具")
    print("测试性能优化效果和功能特性")
    print("=" * 50)
    
    # 检查依赖
    try:
        import performance_optimizer
        print("✅ 性能优化器可用")
    except ImportError:
        print("⚠️  性能优化器不可用，将只测试标准模式")
    
    # 运行测试
    test_optimization_features()
    run_performance_comparison()
    
    print("\n🎉 性能测试完成！")
    print("\n💡 优化建议:")
    print("  - 对于大文件（>50条记录），建议启用性能优化")
    print("  - 性能优化在重复数据较多时效果更明显")
    print("  - 网络API调用时优化效果更显著")

if __name__ == '__main__':
    main()
