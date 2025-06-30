#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票名称匹配器
从Excel文件读取股票名称，使用免费API获取最可能的股票信息
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import time
import re

try:
    import akshare as ak
    from fuzzywuzzy import fuzz, process
    import requests
    import json
    from local_stock_data import LocalStockData
except ImportError as e:
    print(f"缺少必要的依赖包: {e}")
    print("请运行: pip install akshare fuzzywuzzy python-Levenshtein requests")
    sys.exit(1)

# 配置日志
# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'stock_matcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockDataAPI:
    """股票数据API管理类，支持多个数据源"""

    def __init__(self, api_source='akshare'):
        """
        初始化API管理器

        Args:
            api_source: API数据源 ('akshare', 'sina', 'tencent', 'eastmoney', 'local')
        """
        self.api_source = api_source
        self.stock_list = None

    def load_stock_list(self):
        """根据选择的API源加载股票列表"""
        if self.api_source == 'akshare':
            return self._load_from_akshare()
        elif self.api_source == 'sina':
            return self._load_from_sina()
        elif self.api_source == 'tencent':
            return self._load_from_tencent()
        elif self.api_source == 'eastmoney':
            return self._load_from_eastmoney()
        elif self.api_source == 'netease':
            return self._load_from_netease()
        elif self.api_source == 'xueqiu':
            return self._load_from_xueqiu()
        elif self.api_source == 'local':
            return self._load_from_local()
        else:
            logger.warning(f"不支持的API源: {self.api_source}，使用默认的akshare")
            return self._load_from_akshare()

    def _load_from_akshare(self):
        """从AKShare加载股票数据"""
        try:
            logger.info("正在从AKShare加载A股股票列表...")
            stock_list = ak.stock_zh_a_spot_em()
            logger.info(f"AKShare成功加载 {len(stock_list)} 只股票信息")
            return stock_list
        except Exception as e:
            logger.error(f"AKShare加载失败: {e}")
            raise

    def _load_from_sina(self):
        """从新浪财经加载股票数据"""
        try:
            logger.info("正在从新浪财经加载A股股票列表...")
            import requests
            import time

            # 新浪财经股票列表API
            # 获取沪深A股列表
            all_stocks = []

            # 沪市A股代码范围
            sh_prefixes = ['600', '601', '603', '605', '688']  # 包括科创板
            # 深市A股代码范围
            sz_prefixes = ['000', '001', '002', '003', '300', '301']  # 包括创业板

            logger.info("正在获取股票代码列表...")

            # 从本地数据获取股票代码列表作为基础
            local_data = LocalStockData()
            local_stock_list = local_data.get_stock_list()
            stock_codes = local_stock_list['代码'].tolist()

            logger.info(f"获取到 {len(stock_codes)} 个股票代码，开始从新浪获取实时数据...")

            # 分批获取股票数据（新浪API一次最多获取约800只股票）
            batch_size = 800
            for i in range(0, len(stock_codes), batch_size):
                batch_codes = stock_codes[i:i+batch_size]

                # 构建新浪API请求URL
                sina_codes = []
                for code in batch_codes:
                    if code.startswith(('600', '601', '603', '605', '688')):
                        sina_codes.append(f"sh{code}")
                    else:
                        sina_codes.append(f"sz{code}")

                url = f"http://hq.sinajs.cn/list={','.join(sina_codes)}"

                try:
                    response = requests.get(url, timeout=10)
                    response.encoding = 'gbk'

                    if response.status_code == 200:
                        lines = response.text.strip().split('\n')
                        for line in lines:
                            if 'hq_str_' in line and '=""' not in line:
                                # 解析新浪数据格式
                                stock_data = self._parse_sina_data(line)
                                if stock_data:
                                    all_stocks.append(stock_data)

                    # 避免请求过快
                    time.sleep(0.1)

                except Exception as e:
                    logger.warning(f"获取批次 {i//batch_size + 1} 数据失败: {e}")
                    continue

                if (i // batch_size + 1) % 10 == 0:
                    logger.info(f"已处理 {i + len(batch_codes)} / {len(stock_codes)} 只股票")

            if all_stocks:
                df = pd.DataFrame(all_stocks)
                logger.info(f"新浪财经成功加载 {len(df)} 只股票信息")
                return df
            else:
                logger.warning("新浪财经未获取到有效数据，回退到本地数据源")
                return self._load_from_local()

        except Exception as e:
            logger.error(f"新浪财经加载失败: {e}")
            logger.info("回退到本地数据源")
            return self._load_from_local()

    def _load_from_tencent(self):
        """从腾讯财经加载股票数据"""
        try:
            logger.info("正在从腾讯财经加载A股股票列表...")
            import requests
            import json
            import time

            # 从本地数据获取股票代码列表作为基础
            local_data = LocalStockData()
            local_stock_list = local_data.get_stock_list()
            stock_codes = local_stock_list['代码'].tolist()

            logger.info(f"获取到 {len(stock_codes)} 个股票代码，开始从腾讯获取实时数据...")

            all_stocks = []

            # 分批获取股票数据（腾讯API一次最多获取约100只股票）
            batch_size = 100
            for i in range(0, len(stock_codes), batch_size):
                batch_codes = stock_codes[i:i+batch_size]

                # 构建腾讯API请求URL
                tencent_codes = []
                for code in batch_codes:
                    if code.startswith(('600', '601', '603', '605', '688')):
                        tencent_codes.append(f"sh{code}")
                    else:
                        tencent_codes.append(f"sz{code}")

                # 腾讯财经API
                url = f"http://qt.gtimg.cn/q={','.join(tencent_codes)}"

                try:
                    response = requests.get(url, timeout=10)
                    response.encoding = 'gbk'

                    if response.status_code == 200:
                        lines = response.text.strip().split('\n')
                        for line in lines:
                            if 'v_' in line and '=""' not in line:
                                # 解析腾讯数据格式
                                stock_data = self._parse_tencent_data(line)
                                if stock_data:
                                    all_stocks.append(stock_data)

                    # 避免请求过快
                    time.sleep(0.1)

                except Exception as e:
                    logger.warning(f"获取批次 {i//batch_size + 1} 数据失败: {e}")
                    continue

                if (i // batch_size + 1) % 10 == 0:
                    logger.info(f"已处理 {i + len(batch_codes)} / {len(stock_codes)} 只股票")

            if all_stocks:
                df = pd.DataFrame(all_stocks)
                logger.info(f"腾讯财经成功加载 {len(df)} 只股票信息")
                return df
            else:
                logger.warning("腾讯财经未获取到有效数据，回退到本地数据源")
                return self._load_from_local()

        except Exception as e:
            logger.error(f"腾讯财经加载失败: {e}")
            logger.info("回退到本地数据源")
            return self._load_from_local()

    def _load_from_eastmoney(self):
        """从东方财富加载股票数据"""
        try:
            logger.info("正在从东方财富加载A股股票列表...")
            import requests
            import json

            # 东方财富API - 获取沪深A股数据
            # 这个API可以直接获取所有A股的基本信息
            url = "http://82.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 6000,  # 增加每页数量
                'po': 1,
                'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23,m:1+t:13',  # 扩展沪深A股范围
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
            }

            try:
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()

                    if data.get('rc') == 0 and 'data' in data and 'diff' in data['data']:
                        stocks_data = data['data']['diff']

                        all_stocks = []
                        for stock in stocks_data:
                            try:
                                stock_info = {
                                    '代码': stock.get('f12', ''),
                                    '名称': stock.get('f14', ''),
                                    '最新价': float(stock.get('f2', 0)) / 100 if stock.get('f2') else 0.0,
                                    '涨跌幅': float(stock.get('f3', 0)) / 100 if stock.get('f3') else 0.0,
                                    '涨跌额': float(stock.get('f4', 0)) / 100 if stock.get('f4') else 0.0,
                                    '成交量': float(stock.get('f5', 0)) if stock.get('f5') else 0.0,
                                    '成交额': float(stock.get('f6', 0)) if stock.get('f6') else 0.0,
                                    '市盈率-动态': float(stock.get('f9', 0)) / 100 if stock.get('f9') else 0.0,
                                    '市净率': float(stock.get('f23', 0)) / 100 if stock.get('f23') else 0.0,
                                    '总市值': float(stock.get('f20', 0)) if stock.get('f20') else 0.0,
                                    '流通市值': float(stock.get('f21', 0)) if stock.get('f21') else 0.0
                                }

                                # 过滤掉无效数据
                                if stock_info['代码'] and stock_info['名称']:
                                    all_stocks.append(stock_info)

                            except Exception as e:
                                logger.debug(f"解析单只股票数据失败: {e}")
                                continue

                        if all_stocks:
                            df = pd.DataFrame(all_stocks)
                            logger.info(f"东方财富成功加载 {len(df)} 只股票信息")

                            # 如果数据量太少（少于1000只），可能是API限制，回退到本地数据源
                            if len(df) < 1000:
                                logger.warning(f"东方财富数据量较少({len(df)}只)，可能受API限制，回退到本地数据源")
                                return self._load_from_local()

                            return df
                        else:
                            logger.warning("东方财富未获取到有效数据")
                    else:
                        logger.warning(f"东方财富API返回错误: {data.get('rc', 'unknown')}")
                else:
                    logger.warning(f"东方财富API请求失败: {response.status_code}")

            except Exception as e:
                logger.error(f"东方财富API请求异常: {e}")

            # 如果API失败，回退到本地数据源
            logger.info("回退到本地数据源")
            return self._load_from_local()

        except Exception as e:
            logger.error(f"东方财富加载失败: {e}")
            logger.info("回退到本地数据源")
            return self._load_from_local()

    def _load_from_local(self):
        """从本地数据源加载股票数据"""
        try:
            logger.info("正在从本地数据源加载A股股票列表...")
            local_data = LocalStockData()
            stock_list = local_data.get_stock_list()
            logger.info(f"本地数据源成功加载 {len(stock_list)} 只股票信息")
            return stock_list
        except Exception as e:
            logger.error(f"本地数据源加载失败: {e}")
            raise

    def _load_from_netease(self):
        """从网易财经加载股票数据"""
        try:
            logger.info("正在从网易财经加载A股股票列表...")
            import requests
            import json
            import time

            # 从本地数据获取股票代码列表作为基础
            local_data = LocalStockData()
            local_stock_list = local_data.get_stock_list()
            stock_codes = local_stock_list['代码'].tolist()

            logger.info(f"获取到 {len(stock_codes)} 个股票代码，开始从网易获取实时数据...")

            all_stocks = []

            # 分批获取股票数据（网易API一次最多获取约200只股票）
            batch_size = 200
            for i in range(0, len(stock_codes), batch_size):
                batch_codes = stock_codes[i:i+batch_size]

                # 构建网易API请求URL
                netease_codes = []
                for code in batch_codes:
                    if code.startswith(('600', '601', '603', '605', '688')):
                        netease_codes.append(f"0{code}")  # 沪市前缀0
                    else:
                        netease_codes.append(f"1{code}")  # 深市前缀1

                url = f"http://api.money.126.net/data/feed/{','.join(netease_codes)}"

                try:
                    response = requests.get(url, timeout=10)
                    response.encoding = 'utf-8'

                    if response.status_code == 200:
                        # 网易API返回JSONP格式，需要处理
                        text = response.text
                        if text.startswith('_ntes_quote_callback(') and text.endswith(');'):
                            json_str = text[21:-2]  # 去掉JSONP包装
                            data = json.loads(json_str)

                            for code_key, stock_info in data.items():
                                if stock_info and isinstance(stock_info, dict):
                                    stock_data = self._parse_netease_data(code_key, stock_info)
                                    if stock_data:
                                        all_stocks.append(stock_data)

                    # 避免请求过快
                    time.sleep(0.2)

                except Exception as e:
                    logger.warning(f"获取批次 {i//batch_size + 1} 数据失败: {e}")
                    continue

                if (i // batch_size + 1) % 5 == 0:
                    logger.info(f"已处理 {i + len(batch_codes)} / {len(stock_codes)} 只股票")

            if all_stocks:
                df = pd.DataFrame(all_stocks)
                logger.info(f"网易财经成功加载 {len(df)} 只股票信息")
                return df
            else:
                logger.warning("网易财经未获取到有效数据，回退到本地数据源")
                return self._load_from_local()

        except Exception as e:
            logger.error(f"网易财经加载失败: {e}")
            logger.info("回退到本地数据源")
            return self._load_from_local()

    def _parse_netease_data(self, code_key: str, stock_info: dict) -> dict:
        """解析网易财经数据格式"""
        try:
            # 提取股票代码（去掉前缀）
            if code_key.startswith('0') or code_key.startswith('1'):
                code = code_key[1:]
            else:
                code = code_key

            # 网易API字段映射
            name = stock_info.get('name', '')
            price = float(stock_info.get('price', 0))
            percent = float(stock_info.get('percent', 0))
            change = float(stock_info.get('updown', 0))
            volume = float(stock_info.get('volume', 0))
            turnover = float(stock_info.get('turnover', 0))

            return {
                '代码': code,
                '名称': name,
                '最新价': price,
                '涨跌幅': percent,
                '涨跌额': change,
                '成交量': volume,
                '成交额': turnover,
                '市盈率-动态': 0.0,  # 网易API不直接提供，设为0
                '市净率': 0.0,      # 网易API不直接提供，设为0
                '总市值': 0.0,      # 网易API不直接提供，设为0
                '流通市值': 0.0     # 网易API不直接提供，设为0
            }

        except Exception as e:
            logger.debug(f"解析网易数据失败: {e}, 数据: {stock_info}")
            return None

    def _load_from_xueqiu(self):
        """从雪球网加载股票数据"""
        try:
            logger.info("正在从雪球网加载A股股票列表...")
            import requests
            import json
            import time

            # 从本地数据获取股票代码列表作为基础
            local_data = LocalStockData()
            local_stock_list = local_data.get_stock_list()
            stock_codes = local_stock_list['代码'].tolist()

            logger.info(f"获取到 {len(stock_codes)} 个股票代码，开始从雪球获取实时数据...")

            all_stocks = []

            # 雪球API需要设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://xueqiu.com/',
                'Accept': 'application/json, text/plain, */*'
            }

            # 分批获取股票数据（雪球API一次获取一只股票）
            for i, code in enumerate(stock_codes[:100]):  # 限制前100只股票，避免请求过多
                # 构建雪球API请求URL
                if code.startswith(('600', '601', '603', '605', '688')):
                    symbol = f"SH{code}"
                else:
                    symbol = f"SZ{code}"

                url = f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail"

                try:
                    response = requests.get(url, headers=headers, timeout=5)

                    if response.status_code == 200:
                        data = response.json()
                        if data.get('error_code') == 0 and 'data' in data:
                            stock_data = self._parse_xueqiu_data(code, data['data'])
                            if stock_data:
                                all_stocks.append(stock_data)

                    # 避免请求过快，雪球有较严格的限制
                    time.sleep(0.5)

                except Exception as e:
                    logger.debug(f"获取股票 {code} 数据失败: {e}")
                    continue

                if (i + 1) % 20 == 0:
                    logger.info(f"已处理 {i + 1} / {min(100, len(stock_codes))} 只股票")

            if all_stocks:
                df = pd.DataFrame(all_stocks)
                logger.info(f"雪球网成功加载 {len(df)} 只股票信息")
                return df
            else:
                logger.warning("雪球网未获取到有效数据，回退到本地数据源")
                return self._load_from_local()

        except Exception as e:
            logger.error(f"雪球网加载失败: {e}")
            logger.info("回退到本地数据源")
            return self._load_from_local()

    def _parse_xueqiu_data(self, code: str, stock_info: dict) -> dict:
        """解析雪球网数据格式"""
        try:
            # 雪球API字段映射
            quote = stock_info.get('quote', {})

            name = quote.get('name', '')
            price = float(quote.get('current', 0))
            percent = float(quote.get('percent', 0))
            change = float(quote.get('chg', 0))
            volume = float(quote.get('volume', 0))
            amount = float(quote.get('amount', 0))
            pe_ttm = float(quote.get('pe_ttm', 0))
            pb = float(quote.get('pb', 0))
            market_capital = float(quote.get('market_capital', 0))

            return {
                '代码': code,
                '名称': name,
                '最新价': price,
                '涨跌幅': percent,
                '涨跌额': change,
                '成交量': volume,
                '成交额': amount,
                '市盈率-动态': pe_ttm,
                '市净率': pb,
                '总市值': market_capital,
                '流通市值': market_capital  # 雪球API中总市值和流通市值相同
            }

        except Exception as e:
            logger.debug(f"解析雪球数据失败: {e}, 数据: {stock_info}")
            return None

    def _parse_sina_data(self, line: str) -> dict:
        """解析新浪财经数据格式"""
        try:
            # 新浪数据格式: var hq_str_sh600000="浦发银行,10.00,9.99,10.01,10.02,9.98,10.01,10.02,1000000,10010000.00,..."
            if 'hq_str_' not in line or '=""' in line:
                return None

            # 提取股票代码
            code_start = line.find('hq_str_') + 7
            code_end = line.find('="')
            if code_end == -1:
                return None

            full_code = line[code_start:code_end]
            if full_code.startswith('sh'):
                code = full_code[2:]
            elif full_code.startswith('sz'):
                code = full_code[2:]
            else:
                code = full_code

            # 提取数据部分
            data_start = line.find('="') + 2
            data_end = line.rfind('";')
            if data_end == -1:
                data_end = line.rfind('"')

            data_str = line[data_start:data_end]
            if not data_str or data_str == '':
                return None

            # 分割数据字段
            fields = data_str.split(',')
            if len(fields) < 6:
                return None

            # 解析字段
            name = fields[0] if len(fields) > 0 else ''
            current_price = float(fields[3]) if len(fields) > 3 and fields[3] != '' else 0.0
            prev_close = float(fields[2]) if len(fields) > 2 and fields[2] != '' else 0.0

            # 计算涨跌幅和涨跌额
            if prev_close > 0:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
            else:
                change = 0.0
                change_pct = 0.0

            # 其他字段
            volume = float(fields[8]) if len(fields) > 8 and fields[8] != '' else 0.0
            amount = float(fields[9]) if len(fields) > 9 and fields[9] != '' else 0.0

            return {
                '代码': code,
                '名称': name,
                '最新价': current_price,
                '涨跌幅': change_pct,
                '涨跌额': change,
                '成交量': volume,
                '成交额': amount,
                '市盈率-动态': 0.0,  # 新浪API不直接提供，设为0
                '市净率': 0.0,      # 新浪API不直接提供，设为0
                '总市值': 0.0,      # 新浪API不直接提供，设为0
                '流通市值': 0.0     # 新浪API不直接提供，设为0
            }

        except Exception as e:
            logger.debug(f"解析新浪数据失败: {e}, 数据: {line[:100]}...")
            return None

    def _parse_tencent_data(self, line: str) -> dict:
        """解析腾讯财经数据格式"""
        try:
            # 腾讯数据格式: v_sh600000="1~浦发银行~600000~10.00~10.01~9.99~1000000~500000~500000~10.02~..."
            if 'v_' not in line or '=""' in line:
                return None

            # 提取股票代码
            code_start = line.find('v_') + 2
            code_end = line.find('="')
            if code_end == -1:
                return None

            full_code = line[code_start:code_end]
            if full_code.startswith('sh'):
                code = full_code[2:]
            elif full_code.startswith('sz'):
                code = full_code[2:]
            else:
                code = full_code

            # 提取数据部分
            data_start = line.find('="') + 2
            data_end = line.rfind('";')
            if data_end == -1:
                data_end = line.rfind('"')

            data_str = line[data_start:data_end]
            if not data_str or data_str == '':
                return None

            # 分割数据字段
            fields = data_str.split('~')
            if len(fields) < 10:
                return None

            # 解析字段（腾讯API字段顺序）
            # 0: 未知, 1: 名称, 2: 代码, 3: 当前价格, 4: 昨收, 5: 今开, 6: 成交量, 7: 外盘, 8: 内盘, 9: 买一, 10: 买一量...
            name = fields[1] if len(fields) > 1 else ''
            current_price = float(fields[3]) if len(fields) > 3 and fields[3] != '' else 0.0
            prev_close = float(fields[4]) if len(fields) > 4 and fields[4] != '' else 0.0

            # 计算涨跌幅和涨跌额
            if prev_close > 0:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
            else:
                change = 0.0
                change_pct = 0.0

            # 成交量和成交额
            volume = float(fields[6]) if len(fields) > 6 and fields[6] != '' else 0.0
            # 腾讯API的成交额通常在后面的字段中，这里简化处理
            amount = volume * current_price if volume > 0 and current_price > 0 else 0.0

            return {
                '代码': code,
                '名称': name,
                '最新价': current_price,
                '涨跌幅': change_pct,
                '涨跌额': change,
                '成交量': volume,
                '成交额': amount,
                '市盈率-动态': 0.0,  # 腾讯API不直接提供，设为0
                '市净率': 0.0,      # 腾讯API不直接提供，设为0
                '总市值': 0.0,      # 腾讯API不直接提供，设为0
                '流通市值': 0.0     # 腾讯API不直接提供，设为0
            }

        except Exception as e:
            logger.debug(f"解析腾讯数据失败: {e}, 数据: {line[:100]}...")
            return None

class StockNameMatcher:
    """股票名称匹配器类 - 支持根据股票名称匹配代码，或根据股票代码补全名称"""

    def __init__(self, api_source='akshare'):
        """
        初始化匹配器

        Args:
            api_source: API数据源 ('akshare', 'sina', 'tencent', 'eastmoney')
        """
        self.api_source = api_source
        self.api_manager = StockDataAPI(api_source)
        self.stock_list = None
        self.load_stock_list()
        
    def load_stock_list(self):
        """加载股票列表"""
        try:
            logger.info(f"正在使用 {self.api_source} 加载A股股票列表...")
            # 使用API管理器加载股票列表
            self.stock_list = self.api_manager.load_stock_list()
            logger.info(f"成功加载 {len(self.stock_list)} 只股票信息")

            # 清理股票名称，去除特殊字符
            self.stock_list['清理名称'] = self.stock_list['名称'].apply(self._clean_stock_name)

        except Exception as e:
            logger.error(f"加载股票列表失败: {e}")
            # 如果当前API源失败，尝试使用本地数据源作为备用
            if self.api_source != 'local':
                logger.info("尝试使用本地数据源作为备用...")
                try:
                    self.api_source = 'local'  # 更新当前数据源
                    self.api_manager = StockDataAPI('local')
                    self.stock_list = self.api_manager.load_stock_list()
                    self.stock_list['清理名称'] = self.stock_list['名称'].apply(self._clean_stock_name)
                    logger.info(f"本地备用数据源成功加载 {len(self.stock_list)} 只股票信息")
                except Exception as backup_e:
                    logger.error(f"本地备用数据源也失败: {backup_e}")
                    raise
            else:
                raise
    
    def _clean_stock_name(self, name: str) -> str:
        """清理股票名称，去除特殊字符"""
        if pd.isna(name):
            return ""
        # 去除常见的前缀和后缀
        name = str(name).strip()
        # 去除ST、*ST等标记
        name = re.sub(r'^\*?ST\s*', '', name)
        # 去除A、B等后缀
        name = re.sub(r'[AB]$', '', name)
        return name.strip()
    
    def read_excel_file(self, file_path: str, name_column: str = None, price_column: str = None, code_column: str = None) -> pd.DataFrame:
        """
        读取Excel文件

        Args:
            file_path: Excel文件路径
            name_column: 股票名称列名
            price_column: 价格列名
            code_column: 股票代码列名

        Returns:
            DataFrame: 包含股票信息的数据框
        """
        try:
            logger.info(f"正在读取文件: {file_path}")

            # 智能检测文件格式
            def detect_file_format(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(8)
                    if header.startswith(b'\xd0\xcf\x11\xe0') or header.startswith(b'PK\x03\x04'):
                        return 'excel'
                    return 'csv'
                except:
                    return 'csv'

            file_format = detect_file_format(file_path)
            logger.info(f"检测到文件格式: {file_format}")

            # 读取文件
            if file_format == 'excel' or file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
                logger.info("Excel文件读取成功")
            else:
                # CSV文件或文本文件
                df = None
                encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
                separators = [',', '\t', ';', '|']

                for encoding in encodings:
                    for sep in separators:
                        try:
                            # 指定股票代码相关列为字符串类型，保留前导零
                            dtype_dict = {}
                            if code_column:
                                dtype_dict[code_column] = str
                            df = pd.read_csv(file_path, encoding=encoding, sep=sep, dtype=dtype_dict)
                            # 检查是否成功读取（至少有1列且有数据）
                            if len(df.columns) >= 1 and len(df) > 0:
                                logger.info(f"CSV文件读取成功: 编码={encoding}, 分隔符='{sep}'")
                                break
                        except Exception as e:
                            logger.debug(f"尝试读取失败: 编码={encoding}, 分隔符='{sep}', 错误={e}")
                            continue
                    if df is not None and len(df.columns) >= 1:
                        break

                if df is None:
                    raise ValueError("无法正确解析文件，请检查文件格式、编码或分隔符")
            
            logger.info(f"成功读取文件，共 {len(df)} 行数据")
            logger.info(f"列名: {list(df.columns)}")
            
            # 自动检测列名
            if name_column is None:
                name_column = self._detect_name_column(df.columns)
            if price_column is None:
                price_column = self._detect_price_column(df.columns)
            if code_column is None:
                code_column = self._detect_code_column(df.columns)

            logger.info(f"使用股票名称列: {name_column}")
            logger.info(f"使用价格列: {price_column}")
            logger.info(f"使用股票代码列: {code_column}")
            
            # 验证列是否存在
            if name_column not in df.columns:
                raise ValueError(f"未找到股票名称列: {name_column}")
            
            # 创建标准化的数据框
            result_df = pd.DataFrame()

            # 处理股票名称列（如果存在）
            if name_column and name_column in df.columns:
                result_df['原始名称'] = df[name_column]
                result_df['清理名称'] = result_df['原始名称'].apply(self._clean_stock_name)
            else:
                result_df['原始名称'] = None
                result_df['清理名称'] = None

            # 处理股票代码列（如果存在）
            if code_column and code_column in df.columns:
                result_df['股票代码'] = df[code_column].astype(str).str.strip()
            else:
                result_df['股票代码'] = None

            # 处理价格列
            if price_column and price_column in df.columns:
                result_df['参考价格'] = pd.to_numeric(df[price_column], errors='coerce')
            else:
                result_df['参考价格'] = None
                logger.warning("未找到价格列或价格列无效，将不使用价格进行匹配验证")

            # 判断处理模式
            has_names = name_column and name_column in df.columns and not result_df['原始名称'].isna().all()
            has_codes = code_column and code_column in df.columns and not result_df['股票代码'].isna().all()

            if has_codes:
                logger.info("检测到股票代码列，将使用代码补全模式")
                # 过滤掉空的股票代码
                result_df = result_df[result_df['股票代码'].notna() & (result_df['股票代码'] != '')]
            elif has_names:
                logger.info("检测到股票名称列，将使用名称匹配模式")
                # 过滤掉空的股票名称
                result_df = result_df[result_df['清理名称'].str.strip() != '']
            else:
                raise ValueError("未找到有效的股票名称列或股票代码列")
            
            logger.info(f"处理后有效数据: {len(result_df)} 行")
            return result_df
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
    
    def _detect_name_column(self, columns: List[str]) -> str:
        """自动检测股票名称列"""
        name_keywords = ['名称', '股票名称', '股票', '证券名称', '证券', 'name', 'stock', 'symbol_name']
        
        for keyword in name_keywords:
            for col in columns:
                if keyword in str(col).lower():
                    return col
        
        # 如果没有找到，返回第一列
        logger.warning("未能自动检测股票名称列，使用第一列")
        return columns[0]
    
    def _detect_price_column(self, columns: List[str]) -> Optional[str]:
        """自动检测价格列"""
        price_keywords = ['价格', '股价', '现价', '最新价', '收盘价', 'price', 'close', '元']

        for keyword in price_keywords:
            for col in columns:
                if keyword in str(col).lower():
                    return col

        logger.warning("未能自动检测价格列")
        return None

    def _detect_code_column(self, columns: List[str]) -> Optional[str]:
        """自动检测股票代码列"""
        code_keywords = ['代码', '股票代码', '证券代码', 'code', 'symbol', 'stock_code']

        for keyword in code_keywords:
            for col in columns:
                if keyword in str(col).lower():
                    return col

        logger.warning("未能自动检测股票代码列")
        return None

    def _normalize_stock_code(self, code: str) -> str:
        """标准化股票代码格式，自动补全前导零"""
        if not code or pd.isna(code):
            return ""

        code = str(code).strip()

        # 处理被单引号包裹的数字（如 '000037' -> 000037）
        if code.startswith("'"):
            code = code[1:].strip()

        # 处理被双引号包裹的数字（如 "000037" -> 000037）
        if code.startswith('"'):
            code = code[1:].strip()

        # 移除其他可能的非数字字符，但保留数字（保留前导零）
        import re
        # 只保留数字，但不移除前导零
        code = re.sub(r'[^\d]', '', code)

        # 如果处理后为空或不是纯数字，返回原始值
        if not code or not code.isdigit():
            return str(code).strip() if code else ""

        # 根据长度和规则补全前导零
        if len(code) == 6:
            # 已经是6位，直接返回
            return code
        elif len(code) == 3:
            # 3位数字，根据首位数字判断市场
            first_digit = code[0]
            if first_digit in ['6']:
                # 沪市，补全为600xxx
                return '600' + code
            elif first_digit in ['0', '1', '2', '3']:
                # 深市，补全前导零
                return code.zfill(6)
            else:
                # 其他情况，补全前导零
                return code.zfill(6)
        elif len(code) == 4:
            # 4位数字，根据前两位或首位判断
            first_digit = code[0]
            first_two = code[:2]

            if first_two in ['30']:
                # 创业板，补全为300xxx或301xxx
                if code.startswith('30'):
                    return '30' + code[2:].zfill(4)  # 补全为300xxx
                else:
                    return code.zfill(6)
            elif first_two in ['68']:
                # 科创板，补全为688xxx
                return '68' + code[2:].zfill(4)
            elif first_digit in ['0', '1', '2', '3']:
                # 深市，补全前导零
                return code.zfill(6)
            else:
                # 其他情况，补全前导零
                return code.zfill(6)
        elif len(code) == 5:
            # 5位数字，补全一个前导零
            return '0' + code
        else:
            # 其他长度，尝试补全到6位
            return code.zfill(6)

    def _validate_stock_code(self, code: str) -> bool:
        """验证股票代码格式"""
        if not code or pd.isna(code):
            return False

        # 先标准化代码
        normalized_code = self._normalize_stock_code(code)

        # A股代码格式验证（更完整的规则）
        # 沪市：600xxx, 601xxx, 603xxx, 605xxx
        # 科创板：688xxx
        # 深市：000xxx, 001xxx, 002xxx, 003xxx
        # 创业板：300xxx, 301xxx
        if len(normalized_code) == 6 and normalized_code.isdigit():
            first_three = normalized_code[:3]
            # 扩展创业板代码范围，包括301xxx
            valid_prefixes = [
                '600', '601', '603', '605',  # 沪市
                '688',                        # 科创板
                '000', '001', '002', '003',   # 深市
                '300', '301'                  # 创业板（包括新的301xxx）
            ]
            if first_three in valid_prefixes:
                return True

        return False
    
    def match_stock_name(self, input_name: str, use_price: bool = True, reference_price: float = None) -> List[Dict]:
        """
        匹配股票名称
        
        Args:
            input_name: 输入的股票名称
            use_price: 是否使用价格进行验证
            reference_price: 参考价格
            
        Returns:
            List[Dict]: 匹配结果列表
        """
        if not input_name or pd.isna(input_name):
            return []
        
        cleaned_input = self._clean_stock_name(str(input_name))
        if not cleaned_input:
            return []
        
        # 使用模糊匹配
        matches = []
        
        # 1. 精确匹配
        exact_matches = self.stock_list[
            (self.stock_list['名称'] == input_name) | 
            (self.stock_list['清理名称'] == cleaned_input)
        ]
        
        for _, row in exact_matches.iterrows():
            matches.append({
                '股票代码': row['代码'],
                '股票名称': row['名称'],
                '最新价': row['最新价'],
                '匹配类型': '精确匹配',
                '匹配度': 100,
                '价格差异': abs(row['最新价'] - reference_price) if reference_price else None
            })
        
        # 2. 模糊匹配
        if len(matches) < 5:  # 如果精确匹配结果少于5个，进行模糊匹配
            fuzzy_matches = process.extract(
                cleaned_input, 
                self.stock_list['清理名称'].tolist(), 
                limit=10,
                scorer=fuzz.ratio
            )
            
            for match_name, score in fuzzy_matches:
                if score >= 60:  # 匹配度阈值
                    matched_rows = self.stock_list[self.stock_list['清理名称'] == match_name]
                    for _, row in matched_rows.iterrows():
                        # 避免重复添加精确匹配的结果
                        if not any(m['股票代码'] == row['代码'] for m in matches):
                            matches.append({
                                '股票代码': row['代码'],
                                '股票名称': row['名称'],
                                '最新价': row['最新价'],
                                '匹配类型': '模糊匹配',
                                '匹配度': score,
                                '价格差异': abs(row['最新价'] - reference_price) if reference_price else None
                            })
        
        # 3. 包含匹配
        if len(matches) < 5:
            contains_matches = self.stock_list[
                self.stock_list['清理名称'].str.contains(cleaned_input, na=False) |
                self.stock_list['清理名称'].apply(lambda x: cleaned_input in str(x))
            ]
            
            for _, row in contains_matches.iterrows():
                if not any(m['股票代码'] == row['代码'] for m in matches):
                    matches.append({
                        '股票代码': row['代码'],
                        '股票名称': row['名称'],
                        '最新价': row['最新价'],
                        '匹配类型': '包含匹配',
                        '匹配度': 50,
                        '价格差异': abs(row['最新价'] - reference_price) if reference_price else None
                    })
        
        # 按匹配度和价格差异排序
        if use_price and reference_price:
            # 如果有参考价格，优先考虑价格接近的股票
            matches = [m for m in matches if m['价格差异'] is not None]
            matches.sort(key=lambda x: (x['价格差异'], -x['匹配度']))
        else:
            # 否则按匹配度排序
            matches.sort(key=lambda x: -x['匹配度'])
        
        return matches[:5]  # 返回前5个最佳匹配

    def cross_validate_stock_info(self, stock_code: str, stock_name: str) -> Dict:
        """
        使用多个数据源交叉验证股票信息

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            Dict: 验证结果
        """
        validation_results = {}
        api_sources = ['akshare', 'sina', 'tencent', 'eastmoney']

        for api_source in api_sources:
            try:
                logger.info(f"使用 {api_source} 验证股票信息: {stock_code}")

                # 创建临时API管理器
                temp_api = StockDataAPI(api_source)
                temp_stock_list = temp_api.load_stock_list()

                if temp_stock_list is not None:
                    # 查找匹配的股票
                    matched_stocks = temp_stock_list[temp_stock_list['代码'] == stock_code]

                    if len(matched_stocks) > 0:
                        stock_info = matched_stocks.iloc[0]
                        validation_results[api_source] = {
                            'found': True,
                            'name': stock_info['名称'],
                            'price': stock_info.get('最新价', None),
                            'name_match': stock_info['名称'] == stock_name
                        }
                    else:
                        validation_results[api_source] = {
                            'found': False,
                            'name': None,
                            'price': None,
                            'name_match': False
                        }
                else:
                    validation_results[api_source] = {
                        'found': False,
                        'name': None,
                        'price': None,
                        'name_match': False,
                        'error': 'API加载失败'
                    }

            except Exception as e:
                logger.warning(f"{api_source} 验证失败: {e}")
                validation_results[api_source] = {
                    'found': False,
                    'name': None,
                    'price': None,
                    'name_match': False,
                    'error': str(e)
                }

            # 添加延迟避免API限制
            time.sleep(0.5)

        # 分析验证结果
        found_count = sum(1 for result in validation_results.values() if result.get('found', False))
        name_match_count = sum(1 for result in validation_results.values() if result.get('name_match', False))

        # 获取最常见的股票名称
        names = [result['name'] for result in validation_results.values() if result.get('name')]
        most_common_name = max(set(names), key=names.count) if names else None

        return {
            'validation_results': validation_results,
            'found_count': found_count,
            'name_match_count': name_match_count,
            'most_common_name': most_common_name,
            'confidence_score': (found_count / len(api_sources)) * 100,
            'name_consistency': (name_match_count / found_count * 100) if found_count > 0 else 0
        }

    def match_stock_code(self, input_code: str, reference_price: float = None, enable_cross_validation: bool = False) -> Dict:
        """
        根据股票代码匹配股票信息

        Args:
            input_code: 输入的股票代码
            reference_price: 参考价格
            enable_cross_validation: 是否启用多数据源交叉验证

        Returns:
            Dict: 匹配结果
        """
        if not input_code or pd.isna(input_code):
            return {}

        original_code = str(input_code).strip()

        # 标准化股票代码
        normalized_code = self._normalize_stock_code(original_code)

        # 验证股票代码格式（使用标准化后的代码进行验证）
        if not self._validate_stock_code(normalized_code):
            logger.warning(f"股票代码格式无效: {original_code} -> {normalized_code}")
            return {
                '原始代码': input_code,
                '参考价格': reference_price,
                '匹配状态': '代码格式无效',
                '标准化代码': normalized_code,
                '股票名称': '',
                '当前价格': '',
                '价格差异': '',
                '匹配类型': '格式验证失败'
            }

        # 在股票列表中查找匹配的代码（使用标准化后的代码）
        matched_stocks = self.stock_list[self.stock_list['代码'] == normalized_code]

        if len(matched_stocks) == 0:
            logger.warning(f"未找到股票代码: {original_code} -> {normalized_code}")
            return {
                '原始代码': input_code,
                '参考价格': reference_price,
                '匹配状态': '未找到匹配',
                '标准化代码': normalized_code,
                '股票名称': '',
                '当前价格': '',
                '价格差异': '',
                '匹配类型': '代码不存在'
            }

        # 获取匹配的股票信息
        stock_info = matched_stocks.iloc[0]
        current_price = stock_info['最新价']

        # 计算价格差异
        price_diff = None
        if reference_price and not pd.isna(reference_price) and not pd.isna(current_price):
            price_diff = abs(float(current_price) - float(reference_price))

        # 判断匹配类型
        match_type = '代码精确匹配' if original_code == normalized_code else '代码标准化匹配'

        # 基础结果
        result = {
            '原始代码': input_code,
            '参考价格': reference_price,
            '匹配状态': '匹配成功',
            '标准化代码': normalized_code,
            '股票代码': stock_info['代码'],
            '股票名称': stock_info['名称'],
            '当前价格': current_price,
            '价格差异': price_diff,
            '匹配类型': match_type,
            '涨跌幅': stock_info.get('涨跌幅', ''),
            '涨跌额': stock_info.get('涨跌额', ''),
            '成交量': stock_info.get('成交量', ''),
            '成交额': stock_info.get('成交额', ''),
            '市盈率': stock_info.get('市盈率-动态', ''),
            '市净率': stock_info.get('市净率', '')
        }

        # 如果启用交叉验证，添加验证信息
        if enable_cross_validation:
            logger.info(f"开始交叉验证股票信息: {normalized_code} - {stock_info['名称']}")
            validation_result = self.cross_validate_stock_info(normalized_code, stock_info['名称'])

            result.update({
                '验证置信度': f"{validation_result['confidence_score']:.1f}%",
                '名称一致性': f"{validation_result['name_consistency']:.1f}%",
                '验证数据源数': validation_result['found_count'],
                '推荐名称': validation_result['most_common_name'],
                '验证详情': str(validation_result['validation_results'])
            })

            # 如果验证置信度较低，更新匹配状态
            if validation_result['confidence_score'] < 50:
                result['匹配状态'] = '匹配成功(低置信度)'
                result['匹配类型'] += ' - 建议人工确认'

        return result
    
    def process_excel_file(self, file_path: str, output_path: str = None,
                          name_column: str = None, price_column: str = None, code_column: str = None) -> str:
        """
        处理Excel文件，自动判断是进行股票名称匹配还是股票代码补全

        Args:
            file_path: 输入Excel文件路径
            output_path: 输出CSV文件路径
            name_column: 股票名称列名
            price_column: 价格列名
            code_column: 股票代码列名

        Returns:
            str: 输出文件路径
        """
        # 读取文件
        input_df = self.read_excel_file(file_path, name_column, price_column, code_column)

        # 判断处理模式
        has_names = '原始名称' in input_df.columns and not input_df['原始名称'].isna().all()
        has_codes = '股票代码' in input_df.columns and not input_df['股票代码'].isna().all()

        if has_codes:
            logger.info("检测到股票代码，使用代码补全模式")
            return self.process_stock_codes(file_path, output_path, code_column, price_column)
        elif has_names:
            logger.info("检测到股票名称，使用名称匹配模式")
            return self._process_stock_names(input_df, output_path)
        else:
            raise ValueError("未找到有效的股票名称或股票代码列")

    def _process_stock_names(self, input_df: pd.DataFrame, output_path: str = None) -> str:
        """
        处理股票名称匹配（原有功能）

        Args:
            input_df: 输入数据框
            output_path: 输出文件路径

        Returns:
            str: 输出文件路径
        """
        
        # 准备结果数据
        results = []
        
        logger.info("开始进行股票名称匹配...")
        
        for idx, row in input_df.iterrows():
            logger.info(f"处理第 {idx + 1}/{len(input_df)} 行: {row['原始名称']}")
            
            # 进行匹配
            matches = self.match_stock_name(
                row['原始名称'], 
                use_price=row['参考价格'] is not None,
                reference_price=row['参考价格']
            )
            
            if matches:
                # 取最佳匹配
                best_match = matches[0]
                results.append({
                    '原始名称': row['原始名称'],
                    '参考价格': row['参考价格'],
                    '匹配股票代码': best_match['股票代码'],
                    '匹配股票名称': best_match['股票名称'],
                    '当前价格': best_match['最新价'],
                    '匹配类型': best_match['匹配类型'],
                    '匹配度': best_match['匹配度'],
                    '价格差异': best_match['价格差异'],
                    '备选1_代码': matches[1]['股票代码'] if len(matches) > 1 else '',
                    '备选1_名称': matches[1]['股票名称'] if len(matches) > 1 else '',
                    '备选2_代码': matches[2]['股票代码'] if len(matches) > 2 else '',
                    '备选2_名称': matches[2]['股票名称'] if len(matches) > 2 else '',
                })
            else:
                results.append({
                    '原始名称': row['原始名称'],
                    '参考价格': row['参考价格'],
                    '匹配股票代码': '',
                    '匹配股票名称': '未找到匹配',
                    '当前价格': '',
                    '匹配类型': '',
                    '匹配度': 0,
                    '价格差异': '',
                    '备选1_代码': '',
                    '备选1_名称': '',
                    '备选2_代码': '',
                    '备选2_名称': '',
                })
            
            # 添加延迟避免API限制
            time.sleep(0.1)
        
        # 保存结果
        result_df = pd.DataFrame(results)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"stock_match_results_{timestamp}.csv"
        
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"匹配结果已保存到: {output_path}")
        
        # 打印统计信息
        total_count = len(result_df)
        matched_count = len(result_df[result_df['匹配股票代码'] != ''])
        exact_match_count = len(result_df[result_df['匹配类型'] == '精确匹配'])
        
        logger.info(f"匹配统计:")
        logger.info(f"  总数: {total_count}")
        logger.info(f"  成功匹配: {matched_count} ({matched_count/total_count*100:.1f}%)")
        logger.info(f"  精确匹配: {exact_match_count} ({exact_match_count/total_count*100:.1f}%)")
        
        return output_path

    def process_stock_codes(self, file_path: str, output_path: str = None,
                           code_column: str = None, price_column: str = None,
                           enable_cross_validation: bool = False, use_optimization: bool = True) -> str:
        """
        处理股票代码文件，补全股票名称

        Args:
            file_path: 输入文件路径
            output_path: 输出CSV文件路径
            code_column: 股票代码列名
            price_column: 价格列名
            enable_cross_validation: 是否启用多数据源交叉验证
            use_optimization: 是否使用性能优化

        Returns:
            str: 输出文件路径
        """
        # 读取文件
        input_df = self.read_excel_file(file_path, code_column=code_column, price_column=price_column)

        # 检查是否有股票代码列
        if '股票代码' not in input_df.columns or input_df['股票代码'].isna().all():
            raise ValueError("未找到有效的股票代码列，请检查文件格式或指定正确的列名")

        # 选择处理方式
        if use_optimization and len(input_df) > 10:
            logger.info("🚀 使用性能优化模式处理...")
            results = self._process_with_optimization(input_df, enable_cross_validation)
        else:
            logger.info("📝 使用标准模式处理...")
            results = self._process_standard(input_df, enable_cross_validation)

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

        # 验证保存的数据格式
        logger.info(f"验证保存的数据格式...")
        verify_df = pd.read_csv(output_path, dtype={'标准化代码': str, '股票代码': str})
        logger.info(f"验证结果 - 标准化代码样本: {verify_df['标准化代码'].head().tolist()}")
        logger.info(f"验证结果 - 股票代码样本: {verify_df['股票代码'].head().tolist()}")
        logger.info(f"代码补全结果已保存到: {output_path}")

        # 打印统计信息
        total_count = len(result_df)
        # 修复统计逻辑：包含所有成功匹配的情况（包括低置信度）
        success_count = len(result_df[result_df['匹配状态'].str.contains('匹配成功', na=False)])
        invalid_count = len(result_df[result_df['匹配状态'] == '代码格式无效'])
        not_found_count = len(result_df[result_df['匹配状态'] == '未找到匹配'])

        logger.info(f"补全统计:")
        logger.info(f"  总数: {total_count}")
        logger.info(f"  成功补全: {success_count} ({success_count/total_count*100:.1f}%)")
        logger.info(f"  格式无效: {invalid_count} ({invalid_count/total_count*100:.1f}%)")
        logger.info(f"  代码不存在: {not_found_count} ({not_found_count/total_count*100:.1f}%)")

        return output_path

    def _process_with_optimization(self, input_df: pd.DataFrame, enable_cross_validation: bool) -> list:
        """使用性能优化处理"""
        try:
            from performance_optimizer import PerformanceOptimizer
            optimizer = PerformanceOptimizer(self)
            return optimizer.optimize_stock_matching(input_df, enable_cross_validation)
        except ImportError:
            logger.warning("性能优化器不可用，回退到标准模式")
            return self._process_standard(input_df, enable_cross_validation)

    def _process_standard(self, input_df: pd.DataFrame, enable_cross_validation: bool) -> list:
        """标准处理模式"""
        results = []
        logger.info("开始进行股票代码补全...")

        for idx, row in input_df.iterrows():
            logger.info(f"处理第 {idx + 1}/{len(input_df)} 行: {row['股票代码']}")

            # 进行代码匹配
            match_result = self.match_stock_code(
                row['股票代码'],
                reference_price=row['参考价格'],
                enable_cross_validation=enable_cross_validation
            )

            results.append(match_result)

            # 减少延迟，提高处理速度
            if len(input_df) > 100:
                time.sleep(0.05)  # 大文件减少延迟
            elif len(input_df) > 50:
                time.sleep(0.08)  # 中等文件适中延迟
            else:
                time.sleep(0.1)   # 小文件保持原延迟

        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票名称匹配器 - 支持根据股票名称匹配代码，或根据股票代码补全名称')
    parser.add_argument('input_file', help='输入的Excel或CSV文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径')
    parser.add_argument('-n', '--name-column', help='股票名称列名')
    parser.add_argument('-p', '--price-column', help='价格列名')
    parser.add_argument('-c', '--code-column', help='股票代码列名')
    parser.add_argument('--mode', choices=['auto', 'name', 'code'], default='auto',
                       help='处理模式: auto(自动检测), name(名称匹配), code(代码补全)')
    parser.add_argument('--api', choices=['akshare', 'sina', 'tencent', 'eastmoney', 'netease', 'xueqiu', 'local'], default='akshare',
                       help='数据源API: akshare(默认), sina(新浪), tencent(腾讯), eastmoney(东方财富), netease(网易), xueqiu(雪球), local(本地)')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    try:
        # 创建匹配器，使用指定的API源
        matcher = StockNameMatcher(api_source=args.api)

        # 根据模式处理文件
        if args.mode == 'code':
            # 强制使用代码补全模式
            output_file = matcher.process_stock_codes(
                args.input_file,
                args.output,
                args.code_column,
                args.price_column
            )
        elif args.mode == 'name':
            # 强制使用名称匹配模式
            input_df = matcher.read_excel_file(args.input_file, args.name_column, args.price_column)
            output_file = matcher._process_stock_names(input_df, args.output)
        else:
            # 自动检测模式
            output_file = matcher.process_excel_file(
                args.input_file,
                args.output,
                args.name_column,
                args.price_column,
                args.code_column
            )

        print(f"\n处理完成！结果已保存到: {output_file}")

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
