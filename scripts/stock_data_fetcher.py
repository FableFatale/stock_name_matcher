#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取器 - 从API获取完整的股票列表
支持从多个数据源获取股票代码和名称，并保存为离线数据
"""

import akshare as ak
import pandas as pd
import logging
import time
import os
from datetime import datetime
import requests
from typing import Optional, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"创建数据目录: {self.data_dir}")
    
    def fetch_all_stocks_akshare(self) -> Optional[pd.DataFrame]:
        """
        使用AKShare获取所有A股股票列表
        返回包含股票代码、名称等信息的DataFrame
        """
        try:
            logger.info("开始从AKShare获取所有A股股票数据...")
            
            # 获取沪深京A股实时行情数据
            stock_data = ak.stock_zh_a_spot_em()
            
            if stock_data is None or stock_data.empty:
                logger.error("从AKShare获取的股票数据为空")
                return None
            
            logger.info(f"成功获取 {len(stock_data)} 只股票的数据")
            
            # 选择需要的列并重命名
            columns_mapping = {
                '代码': '股票代码',
                '名称': '股票名称',
                '最新价': '最新价',
                '涨跌幅': '涨跌幅',
                '涨跌额': '涨跌额',
                '成交量': '成交量',
                '成交额': '成交额',
                '市盈率-动态': '市盈率',
                '市净率': '市净率',
                '总市值': '总市值',
                '流通市值': '流通市值'
            }
            
            # 选择存在的列
            available_columns = [col for col in columns_mapping.keys() if col in stock_data.columns]
            selected_data = stock_data[available_columns].copy()
            
            # 重命名列
            rename_mapping = {col: columns_mapping[col] for col in available_columns}
            selected_data.rename(columns=rename_mapping, inplace=True)
            
            # 添加数据获取时间
            selected_data['数据更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 添加清理后的股票名称
            if '股票名称' in selected_data.columns:
                selected_data['清理名称'] = selected_data['股票名称'].apply(self._clean_stock_name)
            
            return selected_data
            
        except Exception as e:
            logger.error(f"从AKShare获取股票数据时发生错误: {str(e)}")
            return None
    
    def fetch_stocks_by_market(self) -> Dict[str, pd.DataFrame]:
        """
        分别获取不同市场的股票数据
        返回包含各市场股票数据的字典
        """
        markets_data = {}
        
        try:
            # 获取沪A股
            logger.info("获取沪A股数据...")
            sh_data = ak.stock_sh_a_spot_em()
            if sh_data is not None and not sh_data.empty:
                sh_data['市场'] = '沪A'
                markets_data['沪A'] = sh_data
                logger.info(f"沪A股: {len(sh_data)} 只")
            
            time.sleep(1)  # 避免请求过快
            
            # 获取深A股
            logger.info("获取深A股数据...")
            sz_data = ak.stock_sz_a_spot_em()
            if sz_data is not None and not sz_data.empty:
                sz_data['市场'] = '深A'
                markets_data['深A'] = sz_data
                logger.info(f"深A股: {len(sz_data)} 只")
            
            time.sleep(1)  # 避免请求过快
            
            # 获取京A股（北交所）
            logger.info("获取京A股数据...")
            bj_data = ak.stock_bj_a_spot_em()
            if bj_data is not None and not bj_data.empty:
                bj_data['市场'] = '京A'
                markets_data['京A'] = bj_data
                logger.info(f"京A股: {len(bj_data)} 只")
            
        except Exception as e:
            logger.error(f"获取分市场股票数据时发生错误: {str(e)}")
        
        return markets_data
    
    def _clean_stock_name(self, name: str) -> str:
        """
        清理股票名称，移除常见后缀
        """
        if pd.isna(name):
            return ""
        
        # 移除常见的后缀
        suffixes = ['股份有限公司', '有限公司', '集团', '控股', '股份', 'A', 'B', 'H']
        cleaned = str(name).strip()
        
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
        
        return cleaned.strip()
    
    def save_stock_data(self, data: pd.DataFrame, filename: str = None) -> str:
        """
        保存股票数据到CSV文件
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stock_list_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"股票数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存股票数据时发生错误: {str(e)}")
            return ""
    
    def load_stock_data(self, filename: str) -> Optional[pd.DataFrame]:
        """
        从CSV文件加载股票数据
        """
        filepath = os.path.join(self.data_dir, filename)

        try:
            if os.path.exists(filepath):
                data = pd.read_csv(filepath, encoding='utf-8-sig')
                logger.info(f"从 {filepath} 加载了 {len(data)} 条股票数据")
                return data
            else:
                logger.warning(f"文件不存在: {filepath}")
                return None
        except Exception as e:
            logger.error(f"加载股票数据时发生错误: {str(e)}")
            return None

    def get_stock_basic_info(self) -> Optional[pd.DataFrame]:
        """
        获取股票基本信息（仅代码和名称）
        适用于创建离线股票列表
        """
        try:
            # 获取完整数据
            full_data = self.fetch_all_stocks_akshare()
            if full_data is None:
                return None

            # 只保留基本信息
            basic_columns = ['股票代码', '股票名称', '清理名称', '数据更新时间']
            available_basic_columns = [col for col in basic_columns if col in full_data.columns]

            basic_info = full_data[available_basic_columns].copy()

            # 添加市场分类
            basic_info['市场'] = basic_info['股票代码'].apply(self._classify_market)

            # 添加股票类型分类
            basic_info['股票类型'] = basic_info['股票代码'].apply(self._classify_stock_type)

            return basic_info

        except Exception as e:
            logger.error(f"获取股票基本信息时发生错误: {str(e)}")
            return None

    def _classify_market(self, code: str) -> str:
        """
        根据股票代码分类市场
        """
        if not code:
            return "未知"

        code = str(code)
        if code.startswith(('600', '601', '603', '605', '688')):
            return "上海"
        elif code.startswith(('000', '001', '002', '003', '300')):
            return "深圳"
        elif code.startswith(('8', '4')):
            return "北京"
        else:
            return "其他"

    def _classify_stock_type(self, code: str) -> str:
        """
        根据股票代码分类股票类型
        """
        if not code:
            return "未知"

        code = str(code)
        if code.startswith('688'):
            return "科创板"
        elif code.startswith('300'):
            return "创业板"
        elif code.startswith(('000', '001')):
            return "深市主板"
        elif code.startswith('002'):
            return "中小板"
        elif code.startswith(('600', '601', '603', '605')):
            return "沪市主板"
        elif code.startswith(('8', '4')):
            return "北交所"
        else:
            return "其他"

    def update_stock_list(self, save_backup: bool = True) -> bool:
        """
        更新股票列表
        """
        try:
            logger.info("开始更新股票列表...")

            # 如果需要备份现有数据
            if save_backup:
                existing_files = [f for f in os.listdir(self.data_dir) if f.startswith('stock_list_') and f.endswith('.csv')]
                if existing_files:
                    latest_file = max(existing_files)
                    backup_name = f"backup_{latest_file}"
                    backup_path = os.path.join(self.data_dir, backup_name)
                    original_path = os.path.join(self.data_dir, latest_file)

                    import shutil
                    shutil.copy2(original_path, backup_path)
                    logger.info(f"已备份现有数据到: {backup_name}")

            # 获取新数据
            stock_data = self.get_stock_basic_info()
            if stock_data is None:
                logger.error("获取股票数据失败")
                return False

            # 保存新数据
            filename = "stock_list_latest.csv"
            filepath = self.save_stock_data(stock_data, filename)

            if filepath:
                logger.info(f"股票列表更新成功，共 {len(stock_data)} 只股票")
                return True
            else:
                logger.error("保存股票数据失败")
                return False

        except Exception as e:
            logger.error(f"更新股票列表时发生错误: {str(e)}")
            return False

    def get_statistics(self, data: pd.DataFrame = None) -> Dict:
        """
        获取股票数据统计信息
        """
        if data is None:
            data = self.load_stock_data("stock_list_latest.csv")
            if data is None:
                return {}

        stats = {
            "总股票数": len(data),
            "数据更新时间": data['数据更新时间'].iloc[0] if '数据更新时间' in data.columns else "未知"
        }

        # 按市场统计
        if '市场' in data.columns:
            market_stats = data['市场'].value_counts().to_dict()
            stats["市场分布"] = market_stats

        # 按股票类型统计
        if '股票类型' in data.columns:
            type_stats = data['股票类型'].value_counts().to_dict()
            stats["类型分布"] = type_stats

        return stats
