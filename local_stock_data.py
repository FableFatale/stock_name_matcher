#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地股票数据源 - 支持离线股票数据和示例数据
"""

import pandas as pd
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class LocalStockData:
    """本地股票数据管理器"""

    def __init__(self, use_offline_data: bool = True):
        """
        初始化本地股票数据

        Args:
            use_offline_data: 是否优先使用离线数据，如果False或离线数据不存在则使用示例数据
        """
        self.use_offline_data = use_offline_data
        self.stock_data = self._load_stock_data()

    def _load_stock_data(self) -> pd.DataFrame:
        """
        加载股票数据，优先使用离线数据，否则使用示例数据
        """
        if self.use_offline_data:
            # 尝试加载离线数据
            offline_data = self._load_offline_data()
            if offline_data is not None and not offline_data.empty:
                logger.info(f"使用离线股票数据，共 {len(offline_data)} 只股票")
                return offline_data
            else:
                logger.warning("离线数据不可用，使用示例数据")

        # 使用示例数据
        sample_data = self._create_sample_data()
        logger.info(f"使用示例股票数据，共 {len(sample_data)} 只股票")
        return sample_data

    def _load_offline_data(self) -> Optional[pd.DataFrame]:
        """
        加载离线股票数据，支持CSV和TXT格式
        """
        try:
            # 查找所有可能的股票数据CSV文件
            data_files = []

            # 优先检查stock_name_list目录
            if os.path.exists("stock_name_list"):
                for filename in os.listdir("stock_name_list"):
                    if filename.lower().endswith('.csv'):
                        filepath = os.path.join("stock_name_list", filename)
                        data_files.append(filepath)

            # 检查data目录
            if os.path.exists("data"):
                for filename in os.listdir("data"):
                    if self._is_stock_data_file(filename):
                        filepath = os.path.join("data", filename)
                        data_files.append(filepath)

            # 检查根目录的CSV文件
            for filename in os.listdir("."):
                if self._is_stock_data_file(filename):
                    data_files.append(filename)

            # 检查根目录的TXT格式股票列表文件
            txt_files = []
            for filename in os.listdir("."):
                if filename.startswith("all_stocks_") and filename.endswith(".txt"):
                    txt_files.append(filename)

            # 智能选择最佳的股票数据文件
            # 优先使用stock_name_list目录中的文件
            stock_name_list_files = [f for f in data_files if f.startswith("stock_name_list")]
            if stock_name_list_files:
                latest_file = self._select_best_data_file(stock_name_list_files)
                logger.info(f"优先使用stock_name_list目录中的文件: {latest_file}")
            else:
                latest_file = self._select_best_data_file(data_files)

            # 如果没有CSV文件，尝试使用TXT文件
            if latest_file is None and txt_files:
                latest_txt_file = max(txt_files, key=os.path.getmtime)
                logger.info(f"未找到CSV格式数据，尝试加载TXT格式股票数据: {latest_txt_file}")
                return self._load_txt_stock_data(latest_txt_file)

            if latest_file and os.path.exists(latest_file):
                logger.info(f"加载离线股票数据: {latest_file}")
                # 指定股票代码列为字符串类型，保留前导零
                # 支持不同的列名格式
                dtype_mapping = {'股票代码': str, 'code': str, '代码': str}
                data = pd.read_csv(latest_file, encoding='utf-8-sig', dtype=dtype_mapping)

                # 转换为标准格式
                return self._convert_to_standard_format(data)

        except Exception as e:
            logger.error(f"加载离线数据时发生错误: {str(e)}")

        return None

    def _load_txt_stock_data(self, txt_file: str) -> Optional[pd.DataFrame]:
        """
        加载TXT格式的股票数据文件
        支持格式: 股票代码,股票名称
        """
        try:
            logger.info(f"开始解析TXT格式股票数据: {txt_file}")

            stock_list = []
            with open(txt_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue

                    # 解析股票代码和名称
                    if ',' in line:
                        parts = line.split(',', 1)  # 只分割第一个逗号
                        if len(parts) == 2:
                            code = parts[0].strip()
                            name = parts[1].strip()

                            # 验证股票代码格式
                            if self._is_valid_stock_code(code):
                                stock_list.append({
                                    '代码': code,
                                    '名称': name,
                                    '最新价': 0.0,
                                    '涨跌幅': 0.0,
                                    '涨跌额': 0.0,
                                    '成交量': 0,
                                    '成交额': 0.0,
                                    '市盈率-动态': 0.0,
                                    '市净率': 0.0,
                                    '总市值': 0.0,
                                    '流通市值': 0.0
                                })
                            else:
                                logger.debug(f"第{line_num}行: 无效的股票代码格式 '{code}'")
                        else:
                            logger.debug(f"第{line_num}行: 格式错误，无法解析 '{line}'")
                    else:
                        logger.debug(f"第{line_num}行: 缺少逗号分隔符 '{line}'")

            if stock_list:
                df = pd.DataFrame(stock_list)
                # 添加清理名称列
                df['清理名称'] = df['名称'].apply(self._clean_stock_name)

                logger.info(f"TXT格式股票数据解析完成，共加载 {len(df)} 只股票")
                return df
            else:
                logger.warning(f"TXT文件 {txt_file} 中未找到有效的股票数据")
                return None

        except Exception as e:
            logger.error(f"解析TXT格式股票数据时发生错误: {str(e)}")
            return None

    def _is_valid_stock_code(self, code: str) -> bool:
        """
        验证股票代码格式是否有效
        """
        if not code or len(code) != 6:
            return False

        # 检查是否为数字
        if not code.isdigit():
            return False

        # 检查A股代码格式
        # 沪市: 600xxx, 601xxx, 603xxx, 605xxx, 688xxx
        # 深市: 000xxx, 001xxx, 002xxx, 003xxx, 300xxx
        # 北交所: 8xxxxx, 4xxxxx
        valid_prefixes = ['000', '001', '002', '003', '300', '600', '601', '603', '605', '688']

        # 检查前3位
        prefix = code[:3]
        if prefix in valid_prefixes:
            return True

        # 检查北交所代码（以8或4开头的6位数字）
        if code.startswith(('8', '4')):
            return True

        return False

    def _is_stock_data_file(self, filename: str) -> bool:
        """
        判断文件是否为股票数据文件
        支持多种命名规则：
        - stock_list_*.csv
        - all_stocks_*.csv
        - stocks_*.csv
        - 股票数据*.csv
        - 股票列表*.csv
        """
        if not filename.endswith('.csv'):
            return False

        # 支持的文件名模式
        patterns = [
            'stock_list_',
            'all_stocks_',
            'stocks_',
            '股票数据',
            '股票列表',
            'stock_data_',
            'stocklist_'
        ]

        filename_lower = filename.lower()
        for pattern in patterns:
            if filename_lower.startswith(pattern.lower()):
                return True

        return False

    def _select_best_data_file(self, data_files: list) -> str:
        """
        从候选文件中选择最佳的股票数据文件
        优先级：
        1. 包含'latest'的文件
        2. 文件名包含最新日期的文件
        3. 修改时间最新的文件
        4. 文件大小最大的文件
        """
        if not data_files:
            return None

        # 1. 优先使用包含'latest'的文件
        latest_files = [f for f in data_files if "latest" in os.path.basename(f).lower()]
        if latest_files:
            # 如果有多个latest文件，选择修改时间最新的
            best_file = max(latest_files, key=os.path.getmtime)
            logger.info(f"选择latest文件: {best_file}")
            return best_file

        # 2. 尝试从文件名中提取日期，选择最新的
        import re
        dated_files = []
        for filepath in data_files:
            filename = os.path.basename(filepath)
            # 匹配日期格式：YYYYMMDD 或 YYYY-MM-DD 或 YYYY_MM_DD
            date_match = re.search(r'(\d{4})[_-]?(\d{2})[_-]?(\d{2})', filename)
            if date_match:
                date_str = ''.join(date_match.groups())
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    dated_files.append((filepath, date_obj))
                except:
                    pass

        if dated_files:
            # 按日期排序，选择最新的
            best_file = max(dated_files, key=lambda x: x[1])[0]
            logger.info(f"选择最新日期文件: {best_file}")
            return best_file

        # 3. 按修改时间选择最新的文件
        try:
            best_file = max(data_files, key=os.path.getmtime)
            logger.info(f"选择修改时间最新文件: {best_file}")
            return best_file
        except:
            # 4. 如果获取修改时间失败，选择文件大小最大的
            try:
                best_file = max(data_files, key=os.path.getsize)
                logger.info(f"选择文件大小最大文件: {best_file}")
                return best_file
            except:
                # 5. 最后的备选方案，选择第一个文件
                logger.info(f"使用第一个可用文件: {data_files[0]}")
                return data_files[0]

    def _convert_to_standard_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        将离线数据转换为标准格式
        """
        try:
            # 创建标准格式的DataFrame
            standard_data = pd.DataFrame()

            # 映射列名
            column_mapping = {
                '股票代码': '代码',
                '代码': '代码',
                'code': '代码',  # 新增：支持英文列名
                '股票名称': '名称',
                '名称': '名称',
                'name': '名称',  # 新增：支持英文列名
                '最新价': '最新价',
                '涨跌幅': '涨跌幅',
                '涨跌额': '涨跌额',
                '成交量': '成交量',
                '成交额': '成交额',
                '市盈率': '市盈率-动态',
                '市盈率-动态': '市盈率-动态',
                '市净率': '市净率',
                '总市值': '总市值',
                '流通市值': '流通市值'
            }

            # 复制可用的列
            for source_col, target_col in column_mapping.items():
                if source_col in data.columns:
                    standard_data[target_col] = data[source_col]

            # 确保必需的列存在
            if '代码' not in standard_data.columns and '股票代码' in data.columns:
                standard_data['代码'] = data['股票代码'].astype(str)
            if '名称' not in standard_data.columns and '股票名称' in data.columns:
                standard_data['名称'] = data['股票名称']

            # 确保股票代码列为字符串类型，保留前导零
            if '代码' in standard_data.columns:
                standard_data['代码'] = standard_data['代码'].astype(str)
                logger.info(f"股票代码列转换完成，样本: {standard_data['代码'].head().tolist()}")

            # 添加清理名称列
            if '名称' in standard_data.columns:
                standard_data['清理名称'] = standard_data['名称'].apply(self._clean_stock_name)

            # 填充缺失的数值列
            numeric_columns = ['最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '市盈率-动态', '市净率', '总市值', '流通市值']
            for col in numeric_columns:
                if col not in standard_data.columns:
                    standard_data[col] = 0.0

            logger.info(f"数据转换完成，共 {len(standard_data)} 只股票，列名: {list(standard_data.columns)}")
            return standard_data

        except Exception as e:
            logger.error(f"转换数据格式时发生错误: {str(e)}")
            return data

    def _create_sample_data(self):
        """创建示例股票数据"""
        # 这里包含一些常见的股票数据，你可以根据需要扩展
        sample_stocks = [
            # 深市主板
            {'代码': '000001', '名称': '平安银行', '最新价': 10.50, '涨跌幅': 1.2, '涨跌额': 0.12, '成交量': 1000000, '成交额': 10500000, '市盈率-动态': 8.5, '市净率': 0.9},
            {'代码': '000002', '名称': '万科A', '最新价': 18.20, '涨跌幅': -0.5, '涨跌额': -0.09, '成交量': 800000, '成交额': 14560000, '市盈率-动态': 12.3, '市净率': 1.2},
            {'代码': '000823', '名称': '超声电子', '最新价': 15.80, '涨跌幅': 2.1, '涨跌额': 0.32, '成交量': 500000, '成交额': 7900000, '市盈率-动态': 25.6, '市净率': 2.1},
            {'代码': '000852', '名称': '石化机械', '最新价': 6.87, '涨跌幅': 0.8, '涨跌额': 0.05, '成交量': 300000, '成交额': 2061000, '市盈率-动态': 18.9, '市净率': 1.5},
            {'代码': '000905', '名称': '厦门港务', '最新价': 8.45, '涨跌幅': -1.2, '涨跌额': -0.10, '成交量': 200000, '成交额': 1690000, '市盈率-动态': 15.2, '市净率': 1.1},
            {'代码': '001368', '名称': '绿色动力', '最新价': 12.30, '涨跌幅': 3.5, '涨跌额': 0.42, '成交量': 150000, '成交额': 1845000, '市盈率-动态': 22.1, '市净率': 1.8},
            
            # 深市中小板
            {'代码': '002029', '名称': '七匹狼', '最新价': 9.80, '涨跌幅': 1.8, '涨跌额': 0.17, '成交量': 400000, '成交额': 3920000, '市盈率-动态': 16.5, '市净率': 1.3},
            {'代码': '002097', '名称': '山河智能', '最新价': 14.50, '涨跌幅': 4.2, '涨跌额': 0.58, '成交量': 600000, '成交额': 8700000, '市盈率-动态': 28.3, '市净率': 2.5},
            {'代码': '002208', '名称': '合肥城建', '最新价': 8.47, '涨跌幅': -0.8, '涨跌额': -0.07, '成交量': 250000, '成交额': 2117500, '市盈率-动态': 12.8, '市净率': 1.0},
            {'代码': '002339', '名称': '积成电子', '最新价': 11.20, '涨跌幅': 2.5, '涨跌额': 0.27, '成交量': 180000, '成交额': 2016000, '市盈率-动态': 35.2, '市净率': 2.8},
            {'代码': '002352', '名称': '顺丰控股', '最新价': 45.60, '涨跌幅': 1.5, '涨跌额': 0.67, '成交量': 900000, '成交额': 41040000, '市盈率-动态': 18.7, '市净率': 3.2},
            {'代码': '002952', '名称': '亚世光电', '最新价': 28.90, '涨跌幅': 5.8, '涨跌额': 1.58, '成交量': 120000, '成交额': 3468000, '市盈率-动态': 45.6, '市净率': 4.1},
            
            # 深市创业板
            {'代码': '300018', '名称': '中元股份', '最新价': 20.38, '涨跌幅': 3.2, '涨跌额': 0.63, '成交量': 350000, '成交额': 7133000, '市盈率-动态': 32.5, '市净率': 2.9},
            {'代码': '300099', '名称': '尤洛卡', '最新价': 16.75, '涨跌幅': -2.1, '涨跌额': -0.36, '成交量': 80000, '成交额': 1340000, '市盈率-动态': 28.9, '市净率': 2.2},
            {'代码': '300516', '名称': '久之洋', '最新价': 35.20, '涨跌幅': 6.8, '涨跌额': 2.24, '成交量': 200000, '成交额': 7040000, '市盈率-动态': 55.8, '市净率': 5.2},
            {'代码': '300564', '名称': '筑博设计', '最新价': 22.80, '涨跌幅': 1.9, '涨跌额': 0.42, '成交量': 90000, '成交额': 2052000, '市盈率-动态': 38.7, '市净率': 3.1},
            {'代码': '300930', '名称': '屹通新材', '最新价': 18.60, '涨跌幅': 4.5, '涨跌额': 0.80, '成交量': 110000, '成交额': 2046000, '市盈率-动态': 42.3, '市净率': 3.8},
            {'代码': '300941', '名称': '创识科技', '最新价': 25.40, '涨跌幅': 7.2, '涨跌额': 1.71, '成交量': 75000, '成交额': 1905000, '市盈率-动态': 48.9, '市净率': 4.5},
            
            # 创业板注册制
            {'代码': '301042', '名称': '安联锐视', '最新价': 32.10, '涨跌幅': 8.5, '涨跌额': 2.51, '成交量': 60000, '成交额': 1926000, '市盈率-动态': 65.2, '市净率': 6.1},
            {'代码': '301176', '名称': '昱能科技', '最新价': 78.50, '涨跌幅': 12.3, '涨跌额': 8.60, '成交量': 45000, '成交额': 3532500, '市盈率-动态': 89.7, '市净率': 8.9},
            {'代码': '301185', '名称': '鸿科股份', '最新价': 41.20, '涨跌幅': 5.6, '涨跌额': 2.18, '成交量': 35000, '成交额': 1442000, '市盈率-动态': 72.1, '市净率': 5.8},
            {'代码': '301192', '名称': '信德新材', '最新价': 28.70, '涨跌幅': 3.8, '涨跌额': 1.05, '成交量': 55000, '成交额': 1578500, '市盈率-动态': 58.3, '市净率': 4.2},
            {'代码': '301223', '名称': '中荣股份', '最新价': 12.36, '涨跌幅': 2.1, '涨跌额': 0.25, '成交量': 85000, '成交额': 1050600, '市盈率-动态': 35.8, '市净率': 2.7},
            {'代码': '301234', '名称': '康普化学', '最新价': 19.80, '涨跌幅': 4.7, '涨跌额': 0.89, '成交量': 70000, '成交额': 1386000, '市盈率-动态': 41.2, '市净率': 3.5},
            {'代码': '301338', '名称': '凯格精机', '最新价': 26.50, '涨跌幅': 6.2, '涨跌额': 1.55, '成交量': 40000, '成交额': 1060000, '市盈率-动态': 52.7, '市净率': 4.8},
            {'代码': '301380', '名称': '明月镜片', '最新价': 33.90, '涨跌幅': 9.1, '涨跌额': 2.83, '成交量': 95000, '成交额': 3220500, '市盈率-动态': 68.9, '市净率': 6.2},
            
            # 沪市主板
            {'代码': '600036', '名称': '招商银行', '最新价': 35.80, '涨跌幅': 0.8, '涨跌额': 0.28, '成交量': 2000000, '成交额': 71600000, '市盈率-动态': 9.2, '市净率': 1.1},
            {'代码': '600095', '名称': '哈高科', '最新价': 8.90, '涨跌幅': 1.5, '涨跌额': 0.13, '成交量': 150000, '成交额': 1335000, '市盈率-动态': 22.5, '市净率': 1.8},
            {'代码': '600111', '名称': '北方稀土', '最新价': 28.60, '涨跌幅': 3.8, '涨跌额': 1.05, '成交量': 800000, '成交额': 22880000, '市盈率-动态': 15.8, '市净率': 2.1},
            {'代码': '600458', '名称': '时代新材', '最新价': 7.20, '涨跌幅': -1.8, '涨跌额': -0.13, '成交量': 300000, '成交额': 2160000, '市盈率-动态': 18.9, '市净率': 1.2},
            {'代码': '600470', '名称': '六国化工', '最新价': 5.80, '涨跌幅': 2.5, '涨跌额': 0.14, '成交量': 400000, '成交额': 2320000, '市盈率-动态': 25.6, '市净率': 1.5},
            {'代码': '600549', '名称': '厦门钨业', '最新价': 18.90, '涨跌幅': 4.2, '涨跌额': 0.76, '成交量': 600000, '成交额': 11340000, '市盈率-动态': 28.7, '市净率': 2.8},
            {'代码': '600685', '名称': '中船防务', '最新价': 15.40, '涨跌幅': 5.8, '涨跌额': 0.84, '成交量': 500000, '成交额': 7700000, '市盈率-动态': 35.2, '市净率': 3.1},
            {'代码': '600727', '名称': '鲁北化工', '最新价': 9.60, '涨跌幅': 1.2, '涨跌额': 0.11, '成交量': 250000, '成交额': 2400000, '市盈率-动态': 19.8, '市净率': 1.6},
            {'代码': '600784', '名称': '鲁银投资', '最新价': 6.45, '涨跌幅': -0.8, '涨跌额': -0.05, '成交量': 180000, '成交额': 1161000, '市盈率-动态': 32.5, '市净率': 1.9},
            {'代码': '601059', '名称': '皖维高新', '最新价': 4.20, '涨跌幅': 3.2, '涨跌额': 0.13, '成交量': 350000, '成交额': 1470000, '市盈率-动态': 15.2, '市净率': 1.1},
            {'代码': '601555', '名称': '东吴证券', '最新价': 8.90, '涨跌幅': 2.8, '涨跌额': 0.24, '成交量': 700000, '成交额': 6230000, '市盈率-动态': 18.5, '市净率': 1.3},
            {'代码': '601788', '名称': '光大证券', '最新价': 12.80, '涨跌幅': 1.5, '涨跌额': 0.19, '成交量': 900000, '成交额': 11520000, '市盈率-动态': 22.1, '市净率': 1.8},
            {'代码': '601916', '名称': '浙商银行', '最新价': 3.85, '涨跌幅': 0.5, '涨跌额': 0.02, '成交量': 1200000, '成交额': 4620000, '市盈率-动态': 5.8, '市净率': 0.6},
            {'代码': '603619', '名称': '中曼石油', '最新价': 16.20, '涨跌幅': 6.8, '涨跌额': 1.03, '成交量': 300000, '成交额': 4860000, '市盈率-动态': 45.2, '市净率': 3.8},
            {'代码': '605056', '名称': '咸亨国际', '最新价': 22.50, '涨跌幅': 8.2, '涨跌额': 1.71, '成交量': 120000, '成交额': 2700000, '市盈率-动态': 58.9, '市净率': 5.1},
            {'代码': '605058', '名称': '澳弘电子', '最新价': 35.80, '涨跌幅': 12.5, '涨跌额': 3.98, '成交量': 80000, '成交额': 2864000, '市盈率-动态': 72.3, '市净率': 6.8},
            
            # 科创板
            {'代码': '688001', '名称': '华兴源创', '最新价': 45.67, '涨跌幅': 5.2, '涨跌额': 2.26, '成交量': 200000, '成交额': 9134000, '市盈率-动态': 68.9, '市净率': 5.8},
            {'代码': '688334', '名称': '西高院', '最新价': 28.90, '涨跌幅': 7.8, '涨跌额': 2.09, '成交量': 150000, '成交额': 4335000, '市盈率-动态': 55.2, '市净率': 4.9},
            {'代码': '688498', '名称': '源杰科技', '最新价': 52.30, '涨跌幅': 9.5, '涨跌额': 4.54, '成交量': 90000, '成交额': 4707000, '市盈率-动态': 89.7, '市净率': 7.2},
        ]
        
        df = pd.DataFrame(sample_stocks)
        
        # 添加清理名称列
        df['清理名称'] = df['名称'].apply(self._clean_stock_name)
        
        logger.info(f"本地股票数据加载完成，共 {len(df)} 只股票")
        return df
    
    def _clean_stock_name(self, name):
        """清理股票名称"""
        if pd.isna(name):
            return ""
        
        # 移除常见的后缀
        suffixes = ['股份有限公司', '有限公司', '集团', '控股', '股份', 'A', 'B', 'H']
        cleaned = str(name).strip()
        
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)]
        
        return cleaned.strip()
    
    def get_stock_list(self):
        """获取股票列表"""
        return self.stock_data.copy()
    
    def search_by_code(self, code):
        """根据代码搜索股票"""
        result = self.stock_data[self.stock_data['代码'] == code]
        return result.copy() if len(result) > 0 else None
    
    def search_by_name(self, name):
        """根据名称搜索股票"""
        cleaned_name = self._clean_stock_name(name)
        result = self.stock_data[
            (self.stock_data['名称'].str.contains(name, na=False)) |
            (self.stock_data['清理名称'].str.contains(cleaned_name, na=False))
        ]
        return result.copy() if len(result) > 0 else None

    def refresh_data(self):
        """刷新股票数据"""
        logger.info("刷新股票数据...")
        self.stock_data = self._load_stock_data()

    def get_data_info(self) -> dict:
        """获取数据信息"""
        # 检测数据源类型
        data_source = "示例数据"
        if self.use_offline_data:
            # 检查是否使用了TXT文件
            txt_files = [f for f in os.listdir(".") if f.startswith("all_stocks_") and f.endswith(".txt")]
            csv_files = []

            # 检查CSV文件
            if os.path.exists("data"):
                csv_files.extend([f for f in os.listdir("data") if self._is_stock_data_file(f)])
            csv_files.extend([f for f in os.listdir(".") if self._is_stock_data_file(f)])

            if csv_files:
                data_source = "离线CSV数据"
            elif txt_files:
                data_source = f"离线TXT数据 ({txt_files[0]})"
            else:
                data_source = "离线数据"

        info = {
            "总股票数": len(self.stock_data),
            "数据源": data_source,
            "包含列": list(self.stock_data.columns)
        }

        # 如果有市场信息
        if '市场' in self.stock_data.columns:
            info["市场分布"] = self.stock_data['市场'].value_counts().to_dict()
        else:
            # 根据股票代码统计市场分布
            market_stats = self._analyze_market_distribution()
            if market_stats:
                info["市场分布"] = market_stats

        return info

    def _analyze_market_distribution(self) -> dict:
        """
        根据股票代码分析市场分布
        """
        try:
            market_counts = {'沪市': 0, '深市': 0, '北交所': 0, '其他': 0}

            for code in self.stock_data['代码']:
                code_str = str(code)
                if code_str.startswith(('600', '601', '603', '605', '688')):
                    market_counts['沪市'] += 1
                elif code_str.startswith(('000', '001', '002', '003', '300')):
                    market_counts['深市'] += 1
                elif code_str.startswith(('8', '4')) and len(code_str) == 6:
                    market_counts['北交所'] += 1
                else:
                    market_counts['其他'] += 1

            # 移除计数为0的市场
            return {k: v for k, v in market_counts.items() if v > 0}
        except Exception as e:
            logger.error(f"分析市场分布时发生错误: {str(e)}")
            return {}

    def export_to_csv(self, filename: str = "exported_stock_data.csv") -> bool:
        """导出股票数据到CSV文件"""
        try:
            self.stock_data.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"股票数据已导出到: {filename}")
            return True
        except Exception as e:
            logger.error(f"导出数据时发生错误: {str(e)}")
            return False

    def search_by_code_fuzzy(self, code_pattern: str):
        """根据代码模糊搜索股票"""
        result = self.stock_data[
            self.stock_data['代码'].str.contains(code_pattern, na=False)
        ]
        return result.copy() if len(result) > 0 else None

    def get_stocks_by_market(self, market: str = None):
        """根据市场获取股票"""
        if market is None:
            return self.stock_data.copy()

        # 如果有市场列，直接使用
        if '市场' in self.stock_data.columns:
            if market.lower() in ['sh', '上海', '沪市']:
                result = self.stock_data[self.stock_data['市场'] == '上海']
            elif market.lower() in ['sz', '深圳', '深市']:
                result = self.stock_data[self.stock_data['市场'] == '深圳']
            elif market.lower() in ['bj', '北京', '北交所']:
                result = self.stock_data[self.stock_data['市场'] == '北京']
            else:
                result = pd.DataFrame()
        else:
            # 根据代码判断市场
            if market.lower() in ['sh', '上海', '沪市']:
                result = self.stock_data[
                    self.stock_data['代码'].astype(str).str.startswith(('600', '601', '603', '605', '688'), na=False)
                ]
            elif market.lower() in ['sz', '深圳', '深市']:
                result = self.stock_data[
                    self.stock_data['代码'].astype(str).str.startswith(('000', '001', '002', '003', '300'), na=False)
                ]
            elif market.lower() in ['bj', '北京', '北交所']:
                result = self.stock_data[
                    self.stock_data['代码'].astype(str).str.startswith(('8', '4'), na=False)
                ]
            else:
                result = pd.DataFrame()

        return result.copy() if len(result) > 0 else None

    def convert_txt_to_csv(self, txt_file: str, output_file: str = None) -> bool:
        """
        将TXT格式的股票列表转换为CSV格式

        Args:
            txt_file: TXT文件路径
            output_file: 输出CSV文件路径，如果为None则自动生成

        Returns:
            bool: 转换是否成功
        """
        try:
            # 加载TXT数据
            data = self._load_txt_stock_data(txt_file)
            if data is None or data.empty:
                logger.error(f"无法加载TXT文件: {txt_file}")
                return False

            # 生成输出文件名
            if output_file is None:
                base_name = os.path.splitext(os.path.basename(txt_file))[0]
                output_file = f"{base_name}_converted.csv"

            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 保存为CSV
            data.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"TXT文件已转换为CSV: {txt_file} -> {output_file}")
            logger.info(f"转换了 {len(data)} 只股票")

            return True

        except Exception as e:
            logger.error(f"转换TXT到CSV时发生错误: {str(e)}")
            return False

    def get_available_data_files(self) -> dict:
        """
        获取可用的数据文件列表

        Returns:
            dict: 包含CSV和TXT文件列表的字典
        """
        files_info = {
            'csv_files': [],
            'txt_files': [],
            'recommended': None
        }

        try:
            # 检查CSV文件
            if os.path.exists("data"):
                for filename in os.listdir("data"):
                    if filename.startswith("stock_list_") and filename.endswith(".csv"):
                        filepath = os.path.join("data", filename)
                        size = os.path.getsize(filepath)
                        mtime = os.path.getmtime(filepath)
                        files_info['csv_files'].append({
                            'path': filepath,
                            'name': filename,
                            'size': size,
                            'modified': mtime
                        })

            # 检查根目录的CSV文件
            for filename in os.listdir("."):
                if self._is_stock_data_file(filename):
                    size = os.path.getsize(filename)
                    mtime = os.path.getmtime(filename)
                    files_info['csv_files'].append({
                        'path': filename,
                        'name': filename,
                        'size': size,
                        'modified': mtime
                    })

            # 检查TXT文件
            for filename in os.listdir("."):
                if filename.startswith("all_stocks_") and filename.endswith(".txt"):
                    size = os.path.getsize(filename)
                    mtime = os.path.getmtime(filename)
                    files_info['txt_files'].append({
                        'path': filename,
                        'name': filename,
                        'size': size,
                        'modified': mtime
                    })

            # 确定推荐文件
            all_files = files_info['csv_files'] + files_info['txt_files']
            if all_files:
                # 优先推荐latest文件
                latest_files = [f for f in files_info['csv_files'] if 'latest' in f['name']]
                if latest_files:
                    files_info['recommended'] = latest_files[0]
                else:
                    # 推荐最新的文件
                    files_info['recommended'] = max(all_files, key=lambda x: x['modified'])

        except Exception as e:
            logger.error(f"获取数据文件列表时发生错误: {str(e)}")

        return files_info
