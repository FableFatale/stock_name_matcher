#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票匹配性能优化器
提供批量处理、缓存、并行处理等优化功能
"""

import os
import sys
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import threading
from functools import lru_cache

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, stock_matcher):
        self.matcher = stock_matcher
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.batch_size = 100
        self.max_workers = 4
        
    def optimize_stock_matching(self, input_df: pd.DataFrame, enable_cross_validation: bool = False) -> List[Dict]:
        """
        优化的股票匹配处理
        
        Args:
            input_df: 输入数据框
            enable_cross_validation: 是否启用交叉验证
            
        Returns:
            List[Dict]: 匹配结果列表
        """
        logger.info(f"🚀 开始优化处理 {len(input_df)} 条记录...")
        start_time = time.time()
        
        # 1. 预处理和去重
        processed_data = self._preprocess_data(input_df)
        
        # 2. 批量处理
        if len(processed_data) > self.batch_size:
            results = self._batch_process(processed_data, enable_cross_validation)
        else:
            results = self._parallel_process(processed_data, enable_cross_validation)
        
        # 3. 后处理
        final_results = self._postprocess_results(results, input_df)
        
        end_time = time.time()
        logger.info(f"✅ 优化处理完成，耗时: {end_time - start_time:.2f}秒")
        logger.info(f"📊 平均每条记录耗时: {(end_time - start_time) / len(input_df):.3f}秒")
        
        return final_results
    
    def _preprocess_data(self, input_df: pd.DataFrame) -> List[Tuple[int, str, float]]:
        """预处理数据，去重和标准化"""
        logger.info("📋 预处理数据...")
        
        processed_data = []
        seen_codes = set()
        
        for idx, row in input_df.iterrows():
            code = str(row['股票代码']).strip()
            price = row.get('参考价格', None)
            
            # 标准化代码
            normalized_code = self.matcher._normalize_stock_code(code)
            
            # 去重处理
            cache_key = (normalized_code, price)
            if cache_key not in seen_codes:
                seen_codes.add(cache_key)
                processed_data.append((idx, normalized_code, price))
            else:
                # 如果是重复的，直接从缓存获取
                processed_data.append((idx, normalized_code, price))
        
        logger.info(f"📊 预处理完成，去重后: {len(set(seen_codes))} 个唯一代码")
        return processed_data
    
    def _parallel_process(self, data: List[Tuple[int, str, float]], enable_cross_validation: bool) -> List[Dict]:
        """并行处理小批量数据"""
        logger.info(f"⚡ 并行处理 {len(data)} 条记录...")
        
        results = [None] * len(data)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_index = {}
            for i, (idx, code, price) in enumerate(data):
                future = executor.submit(self._process_single_with_cache, code, price, enable_cross_validation)
                future_to_index[future] = (i, idx)
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_index):
                result_idx, original_idx = future_to_index[future]
                try:
                    result = future.result()
                    result['原始索引'] = original_idx
                    results[result_idx] = result
                    completed += 1
                    
                    if completed % 50 == 0:
                        logger.info(f"📈 已完成: {completed}/{len(data)}")
                        
                except Exception as e:
                    logger.error(f"处理失败: {e}")
                    results[result_idx] = self._create_error_result(data[result_idx][1], data[result_idx][2], str(e))
        
        return [r for r in results if r is not None]
    
    def _batch_process(self, data: List[Tuple[int, str, float]], enable_cross_validation: bool) -> List[Dict]:
        """批量处理大量数据"""
        logger.info(f"📦 批量处理 {len(data)} 条记录...")
        
        all_results = []
        total_batches = (len(data) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(0, len(data), self.batch_size):
            batch_data = data[batch_idx:batch_idx + self.batch_size]
            batch_num = batch_idx // self.batch_size + 1
            
            logger.info(f"🔄 处理批次 {batch_num}/{total_batches} ({len(batch_data)} 条记录)")
            
            # 并行处理当前批次
            batch_results = self._parallel_process(batch_data, enable_cross_validation)
            all_results.extend(batch_results)
            
            # 批次间短暂休息，避免API限制
            if batch_num < total_batches:
                time.sleep(0.5)
        
        return all_results
    
    def _process_single_with_cache(self, code: str, price: float, enable_cross_validation: bool) -> Dict:
        """带缓存的单个股票处理"""
        cache_key = (code, price, enable_cross_validation)
        
        # 检查缓存
        with self.cache_lock:
            if cache_key in self.cache:
                return self.cache[cache_key].copy()
        
        # 处理股票
        try:
            result = self.matcher.match_stock_code(code, price, enable_cross_validation)
            
            # 缓存结果
            with self.cache_lock:
                self.cache[cache_key] = result.copy()
            
            return result
            
        except Exception as e:
            logger.error(f"处理股票 {code} 失败: {e}")
            return self._create_error_result(code, price, str(e))
    
    def _create_error_result(self, code: str, price: float, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            '原始代码': code,
            '参考价格': price,
            '匹配状态': '处理失败',
            '标准化代码': code,
            '股票名称': '',
            '当前价格': '',
            '价格差异': '',
            '匹配类型': f'错误: {error_msg}'
        }
    
    def _postprocess_results(self, results: List[Dict], original_df: pd.DataFrame) -> List[Dict]:
        """后处理结果，确保顺序正确"""
        logger.info("🔧 后处理结果...")
        
        # 创建结果映射
        result_map = {}
        for result in results:
            if '原始索引' in result:
                result_map[result['原始索引']] = result
                del result['原始索引']  # 移除临时字段
        
        # 按原始顺序重新排列
        final_results = []
        for idx in range(len(original_df)):
            if idx in result_map:
                final_results.append(result_map[idx])
            else:
                # 如果没有结果，创建默认结果
                row = original_df.iloc[idx]
                final_results.append(self._create_error_result(
                    str(row['股票代码']), 
                    row.get('参考价格', None), 
                    '未处理'
                ))
        
        return final_results
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        with self.cache_lock:
            return {
                'cache_size': len(self.cache),
                'cache_hit_potential': len(self.cache) > 0
            }
    
    def clear_cache(self):
        """清空缓存"""
        with self.cache_lock:
            self.cache.clear()
            logger.info("🗑️ 缓存已清空")


def apply_performance_optimization():
    """应用性能优化到现有的股票匹配器"""
    logger.info("🔧 应用性能优化...")
    
    # 这个函数将被用来修改现有的 stock_name_matcher.py
    optimization_code = '''
    # 性能优化代码将被注入到 StockNameMatcher 类中
    def process_stock_codes_optimized(self, file_path: str, output_path: str = None,
                                    code_column: str = None, price_column: str = None,
                                    enable_cross_validation: bool = False) -> str:
        """
        优化版本的股票代码处理
        """
        from performance_optimizer import PerformanceOptimizer
        
        # 读取文件
        input_df = self.read_excel_file(file_path, code_column=code_column, price_column=price_column)
        
        # 检查是否有股票代码列
        if '股票代码' not in input_df.columns or input_df['股票代码'].isna().all():
            raise ValueError("未找到有效的股票代码列，请检查文件格式或指定正确的列名")
        
        # 使用性能优化器
        optimizer = PerformanceOptimizer(self)
        results = optimizer.optimize_stock_matching(input_df, enable_cross_validation)
        
        # 保存结果
        result_df = pd.DataFrame(results)
        
        # 确保股票代码相关列保持字符串格式，保留前导零
        code_columns = ['标准化代码', '股票代码']
        for col in code_columns:
            if col in result_df.columns:
                result_df[col] = result_df[col].astype(str)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"stock_code_completion_{timestamp}.csv"
        
        # 保存CSV时指定数据类型，确保股票代码列保持字符串格式
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # 打印统计信息
        total_count = len(result_df)
        success_count = len(result_df[result_df['匹配状态'].str.contains('匹配成功', na=False)])
        
        logger.info(f"优化处理统计:")
        logger.info(f"  总数: {total_count}")
        logger.info(f"  成功补全: {success_count} ({success_count/total_count*100:.1f}%)")
        logger.info(f"  缓存统计: {optimizer.get_cache_stats()}")
        
        return output_path
    '''
    
    return optimization_code


if __name__ == '__main__':
    print("🚀 股票匹配性能优化器")
    print("📋 主要优化功能:")
    print("  - 并行处理")
    print("  - 智能缓存")
    print("  - 批量处理")
    print("  - 去重优化")
    print("  - 减少API调用延迟")
