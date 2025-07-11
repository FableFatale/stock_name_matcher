#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票代码名称补全Web应用
支持上传CSV/Excel文件，自动补全股票名称
"""

import os
import sys
import logging
import json
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from stock_name_matcher import StockNameMatcher
from auto_file_manager import AutoFileManager
from config_manager import config_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 自定义JSON编码器，处理NaN值
class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            # 递归处理字典
            new_obj = {}
            for key, value in obj.items():
                new_obj[key] = self._convert_value(value)
            obj = new_obj
        elif isinstance(obj, list):
            # 递归处理列表
            obj = [self._convert_value(item) for item in obj]
        else:
            obj = self._convert_value(obj)
        return super().encode(obj)

    def _convert_value(self, value):
        """转换值，处理NaN和特殊类型"""
        if pd.isna(value):
            return None
        elif isinstance(value, np.integer):
            return int(value)
        elif isinstance(value, np.floating):
            if np.isnan(value):
                return None
            return float(value)
        elif isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_value(item) for item in value]
        else:
            return value

# Flask应用配置
app = Flask(__name__)
app.secret_key = 'stock_matcher_secret_key_2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.json_encoder = CustomJSONEncoder

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'result'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_file_format(filepath):
    """智能检测文件格式"""
    try:
        # 读取文件前几个字节来判断格式
        with open(filepath, 'rb') as f:
            header = f.read(8)

        # Excel文件的魔数
        if header.startswith(b'\xd0\xcf\x11\xe0') or header.startswith(b'PK\x03\x04'):
            return 'excel'

        # 尝试作为文本文件读取
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                f.read(100)
            return 'csv'
        except:
            try:
                with open(filepath, 'r', encoding='gbk') as f:
                    f.read(100)
                return 'csv'
            except:
                return 'unknown'
    except:
        return 'unknown'

def get_file_info(filepath):
    """获取文件基本信息"""
    try:
        # 智能检测文件格式
        file_format = detect_file_format(filepath)
        logger.info(f"检测到文件格式: {file_format}")

        df = None
        encoding_used = None
        sep_used = None

        if file_format == 'excel' or filepath.endswith(('.xlsx', '.xls')):
            # Excel文件
            try:
                df = pd.read_excel(filepath, nrows=5)
                logger.info("Excel文件读取成功")
            except Exception as e:
                logger.error(f"Excel文件读取失败: {e}")
                raise ValueError(f"无法读取Excel文件: {e}")

        else:
            # CSV文件或文本文件
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin1']
            separators = [',', '\t', ';', '|']

            for encoding in encodings:
                for sep in separators:
                    try:
                        # 尝试检测股票代码列并指定为字符串类型
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=5, dtype=str)
                        # 检查是否成功读取（至少有1列且有数据）
                        if len(df.columns) >= 1 and len(df) > 0:
                            # 进一步检查是否有合理的列数
                            if len(df.columns) >= 2 or (len(df.columns) == 1 and ',' in str(df.iloc[0, 0])):
                                encoding_used = encoding
                                sep_used = sep
                                logger.info(f"CSV文件读取成功: 编码={encoding}, 分隔符='{sep}'")
                                break
                    except Exception as e:
                        logger.debug(f"尝试读取失败: 编码={encoding}, 分隔符='{sep}', 错误={e}")
                        continue
                if df is not None and len(df.columns) >= 1:
                    break

            if df is None:
                raise ValueError("无法正确解析文件，请检查文件格式、编码或分隔符")

        # 获取完整行数
        if file_format == 'excel' or filepath.endswith(('.xlsx', '.xls')):
            full_df = pd.read_excel(filepath)
            total_rows = len(full_df)
        else:
            # 指定所有列为字符串类型，保留前导零
            full_df = pd.read_csv(filepath, encoding=encoding_used, sep=sep_used, dtype=str)
            total_rows = len(full_df)

        # 处理预览数据，确保可以JSON序列化
        preview_data = []
        for _, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                # 处理NaN值和特殊数值
                if pd.isna(val):
                    row_dict[col] = None
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    row_dict[col] = float(val) if isinstance(val, float) else int(val)
                else:
                    row_dict[col] = str(val)
            preview_data.append(row_dict)

        return {
            'columns': list(df.columns),
            'rows': total_rows,
            'preview': preview_data,
            'file_format': file_format,
            'encoding': encoding_used,
            'separator': sep_used
        }
    except Exception as e:
        logger.error(f"读取文件信息失败: {e}")
        return None

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式，请上传CSV或Excel文件'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 获取文件信息
        file_info = get_file_info(filepath)
        if not file_info:
            return jsonify({'error': '文件读取失败，请检查文件格式'}), 400
        
        return jsonify({
            'success': True,
            'filename': filename,
            'file_info': file_info
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_file():
    """处理股票代码名称补全"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        code_column = data.get('code_column')
        price_column = data.get('price_column')
        api_source = data.get('api_source', 'akshare')
        enable_cross_validation = data.get('enable_cross_validation', False)
        use_optimization = data.get('use_optimization', True)  # 默认启用优化

        if not filename:
            return jsonify({'error': '文件名不能为空'}), 400

        # 文件路径
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(input_path):
            return jsonify({'error': '文件不存在'}), 400

        # 创建匹配器
        logger.info(f"开始处理文件: {filename}")
        logger.info(f"使用API源: {api_source}")
        logger.info(f"代码列: {code_column}, 价格列: {price_column}")

        # 临时禁用进度条输出，避免干扰JSON响应
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr

        # 捕获所有输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # 强制重新加载模块以确保使用最新的修复
            import importlib
            import stock_name_matcher
            import local_stock_data
            importlib.reload(local_stock_data)
            importlib.reload(stock_name_matcher)

            # 创建本地数据管理器并确保数据正确加载
            local_data_manager = local_stock_data.LocalStockData()
            stock_list = local_data_manager.get_stock_list()

            logger.info(f"Web应用加载股票数据: {len(stock_list) if stock_list is not None else 0} 只股票")

            # 验证关键股票代码
            if stock_list is not None and len(stock_list) > 0:
                test_codes = ['000037', '000603', '000798']
                for code in test_codes:
                    matches = stock_list[stock_list['代码'] == code]
                    if len(matches) > 0:
                        logger.info(f"Web应用验证成功: {code} -> {matches.iloc[0]['名称']}")
                    else:
                        logger.warning(f"Web应用验证失败: {code} 未找到")

            # 创建匹配器并传入正确的股票数据
            matcher = stock_name_matcher.StockNameMatcher(api_source=api_source)

            # 确保匹配器使用正确的股票数据
            if stock_list is not None:
                matcher.stock_list = stock_list
                logger.info(f"Web应用匹配器股票数据已更新: {len(matcher.stock_list)} 只股票")

            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"stock_completion_{timestamp}.csv"
            output_path = os.path.join(RESULT_FOLDER, output_filename)

            # 处理文件
            result_path = matcher.process_stock_codes(
                input_path,
                output_path,
                code_column=code_column,
                price_column=price_column,
                enable_cross_validation=enable_cross_validation,
                use_optimization=use_optimization
            )

        # 读取结果统计
        result_df = pd.read_csv(result_path)
        total_count = len(result_df)
        # 修复统计逻辑：包含所有成功匹配的情况（包括低置信度）
        success_count = len(result_df[result_df['匹配状态'].str.contains('匹配成功', na=False)])
        invalid_count = len(result_df[result_df['匹配状态'] == '代码格式无效'])
        not_found_count = len(result_df[result_df['匹配状态'] == '未找到匹配'])

        # 获取结果预览，确保数据可以JSON序列化
        preview_data = []
        for _, row in result_df.head(10).iterrows():
            row_dict = {}
            for col, val in row.items():
                # 处理NaN值和特殊数值
                if pd.isna(val):
                    row_dict[col] = None
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    row_dict[col] = float(val) if isinstance(val, float) else int(val)
                else:
                    row_dict[col] = str(val)
            preview_data.append(row_dict)

        response_data = {
            'success': True,
            'result_file': output_filename,
            'statistics': {
                'total': int(total_count),
                'success': int(success_count),
                'invalid': int(invalid_count),
                'not_found': int(not_found_count),
                'success_rate': round(float(success_count) / float(total_count) * 100, 1) if total_count > 0 else 0.0
            },
            'preview': preview_data
        }

        logger.info(f"处理完成: {success_count}/{total_count} 成功")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"文件处理失败: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载结果文件"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"检测到不安全的文件名: {filename}")
            return jsonify({'error': '无效的文件名'}), 400

        file_path = os.path.join(RESULT_FOLDER, filename)
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            return jsonify({'error': '文件不存在'}), 404

        # 获取文件信息
        file_size = os.path.getsize(file_path)
        logger.info(f"准备下载文件: {filename} ({file_size} bytes)")

        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # 创建响应
        from flask import Response
        response = Response(
            file_data,
            mimetype='text/csv',  # 明确指定CSV类型
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(file_size),
                'Content-Type': 'text/csv; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Access-Control-Allow-Origin': '*',  # 允许跨域
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET'
            }
        )

        logger.info(f"文件下载成功: {filename}")
        return response

    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """API状态检查"""
    try:
        # 简单的健康检查
        matcher = StockNameMatcher()
        return jsonify({
            'status': 'ok',
            'stock_count': len(matcher.stock_list) if matcher.stock_list is not None else 0,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test_download')
def test_download():
    """测试下载功能"""
    try:
        # 检查result文件夹
        result_files = []
        if os.path.exists(RESULT_FOLDER):
            result_files = [f for f in os.listdir(RESULT_FOLDER) if f.endswith('.csv')]

        return jsonify({
            'status': 'ok',
            'result_folder_exists': os.path.exists(RESULT_FOLDER),
            'result_files': result_files,
            'total_files': len(result_files),
            'latest_file': max(result_files, key=lambda f: os.path.getctime(os.path.join(RESULT_FOLDER, f))) if result_files else None
        })
    except Exception as e:
        logger.error(f"测试下载功能失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/test_match/<code>')
def test_match(code):
    """测试单个股票代码匹配"""
    try:
        # 强制重新加载模块
        import importlib
        import stock_name_matcher
        import local_stock_data
        importlib.reload(local_stock_data)
        importlib.reload(stock_name_matcher)

        matcher = stock_name_matcher.StockNameMatcher()

        # 测试匹配
        result = matcher.match_stock_code(code)

        # 额外调试信息
        normalized = matcher._normalize_stock_code(code)
        stock_list_info = {
            'total_stocks': len(matcher.stock_list) if matcher.stock_list is not None else 0,
            'has_code_column': '代码' in matcher.stock_list.columns if matcher.stock_list is not None else False,
            'sample_codes': matcher.stock_list['代码'].head().tolist() if matcher.stock_list is not None and '代码' in matcher.stock_list.columns else []
        }

        return jsonify({
            'original_code': code,
            'normalized_code': normalized,
            'match_result': result,
            'stock_list_info': stock_list_info
        })
    except Exception as e:
        logger.error(f"测试匹配失败: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/upload_stock_data', methods=['POST'])
def upload_stock_data():
    """上传新的股票数据文件"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 检查文件类型
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': '只支持CSV格式的股票数据文件'}), 400

        # 创建自动文件管理器
        manager = AutoFileManager()

        # 保存文件到监控目录
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 如果文件名不符合规范，自动重命名
        if not manager.is_stock_data_file(filename):
            name, ext = os.path.splitext(filename)
            filename = f"stock_data_{timestamp}_{name}{ext}"

        filepath = os.path.join(manager.watch_directory, filename)
        file.save(filepath)

        # 验证文件
        validation = manager.validate_stock_file(filepath)
        if not validation['valid']:
            # 删除无效文件
            os.remove(filepath)
            return jsonify({'error': f'文件验证失败: {validation["error"]}'}), 400

        # 自动处理文件
        result = manager.auto_update()

        if result['updated']:
            return jsonify({
                'success': True,
                'message': f'股票数据文件上传成功',
                'filename': filename,
                'file_info': validation['info'],
                'processed_files': result['new_files']
            })
        else:
            return jsonify({
                'success': False,
                'message': '文件上传成功但处理失败',
                'errors': result['errors']
            }), 500

    except Exception as e:
        logger.error(f"股票数据文件上传失败: {e}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/api/stock_data_status')
def stock_data_status():
    """获取股票数据文件状态"""
    try:
        manager = AutoFileManager()
        files_info = manager.get_current_files_info()

        # 获取当前使用的股票数据信息
        from local_stock_data import LocalStockData
        local_data = LocalStockData()
        stock_list = local_data.get_stock_list()
        data_info = local_data.get_data_info()

        return jsonify({
            'status': 'ok',
            'current_data': {
                'total_stocks': len(stock_list) if stock_list is not None else 0,
                'data_source': data_info.get('data_source', '未知'),
                'last_updated': data_info.get('last_updated', '未知')
            },
            'files': {
                'data_files': len(files_info['data_files']),
                'backup_files': len(files_info['backup_files']),
                'watch_files': len(files_info['watch_files']),
                'processed_files': len(files_info['processed_files'])
            },
            'watch_directory': manager.watch_directory
        })

    except Exception as e:
        logger.error(f"获取股票数据状态失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/auto_update_stock_data', methods=['POST'])
def auto_update_stock_data():
    """手动触发股票数据自动更新"""
    try:
        manager = AutoFileManager()
        result = manager.auto_update()

        return jsonify({
            'success': result['updated'],
            'message': f'检查完成，{"发现并处理了新文件" if result["updated"] else "没有发现新文件"}',
            'new_files': result['new_files'],
            'errors': result['errors']
        })

    except Exception as e:
        logger.error(f"自动更新失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    try:
        config_summary = config_manager.get_config_summary()
        return jsonify({
            'status': 'ok',
            'config': config_summary
        })
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/config/api_keys', methods=['GET'])
def get_api_keys():
    """获取API密钥配置状态"""
    try:
        api_keys = config_manager.config_data.get("api_keys", {})
        # 只返回是否配置了密钥，不返回实际密钥值
        api_keys_status = {}
        for source, encrypted_key in api_keys.items():
            decrypted_key = config_manager._decrypt_value(encrypted_key)
            api_keys_status[source] = {
                'configured': bool(decrypted_key),
                'length': len(decrypted_key) if decrypted_key else 0
            }

        return jsonify({
            'status': 'ok',
            'api_keys': api_keys_status
        })
    except Exception as e:
        logger.error(f"获取API密钥状态失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/config/api_keys', methods=['POST'])
def set_api_keys():
    """设置API密钥"""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', {})

        success_count = 0
        errors = []

        for source, api_key in api_keys.items():
            if config_manager.set_api_key(source, api_key):
                success_count += 1
            else:
                errors.append(f"设置 {source} API密钥失败")

        return jsonify({
            'success': success_count > 0,
            'message': f'成功设置 {success_count} 个API密钥',
            'errors': errors
        })

    except Exception as e:
        logger.error(f"设置API密钥失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/test_connection/<source>')
def test_api_connection(source):
    """测试API连接"""
    try:
        result = config_manager.test_api_connection(source)
        return jsonify(result)
    except Exception as e:
        logger.error(f"测试API连接失败: {e}")
        return jsonify({
            'source': source,
            'status': 'error',
            'message': f'测试连接时发生错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/config/data_sources', methods=['GET'])
def get_data_sources_config():
    """获取数据源配置"""
    try:
        config = config_manager.get_data_source_config()
        return jsonify({
            'status': 'ok',
            'config': config
        })
    except Exception as e:
        logger.error(f"获取数据源配置失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/config/data_sources', methods=['POST'])
def set_data_sources_config():
    """设置数据源配置"""
    try:
        data = request.get_json()
        config = data.get('config', {})

        if config_manager.set_data_source_config(config):
            return jsonify({
                'success': True,
                'message': '数据源配置更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据源配置更新失败'
            }), 500

    except Exception as e:
        logger.error(f"设置数据源配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data_source_stats')
def get_data_source_stats():
    """获取数据源统计信息"""
    try:
        stats = config_manager.get_data_source_stats()
        return jsonify({
            'status': 'ok',
            'stats': stats
        })
    except Exception as e:
        logger.error(f"获取数据源统计失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/data_source_suggestion/<source>')
def get_data_source_suggestion(source):
    """获取数据源API配置建议"""
    try:
        suggestion = config_manager.should_suggest_api_config(source)
        return jsonify({
            'status': 'ok',
            'source': source,
            'suggestion': suggestion
        })
    except Exception as e:
        logger.error(f"获取数据源建议失败: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/record_failure/<source>', methods=['POST'])
def record_data_source_failure(source):
    """记录数据源失败"""
    try:
        data = request.get_json() or {}
        error_type = data.get('error_type', 'timeout')

        success = config_manager.record_data_source_failure(source, error_type)

        if success:
            # 检查是否应该建议配置API
            suggestion = config_manager.should_suggest_api_config(source)

            return jsonify({
                'success': True,
                'message': f'已记录 {source} 数据源失败',
                'suggestion': suggestion
            })
        else:
            return jsonify({
                'success': False,
                'error': '记录失败信息时出错'
            }), 500

    except Exception as e:
        logger.error(f"记录数据源失败时出错: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动股票代码名称补全Web应用...")
    print("📊 访问地址: http://localhost:5000")
    print("📁 上传文件夹: uploads/")
    print("📁 结果文件夹: result/")

    app.run(debug=True, host='0.0.0.0', port=5000)
