#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动文件管理器
自动检测和管理股票数据文件，确保系统始终使用最新的数据
"""

import os
import sys
import time
import logging
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoFileManager:
    """自动文件管理器"""
    
    def __init__(self, watch_directory: str = "stock_name_list"):
        self.watch_directory = watch_directory
        self.data_directory = "data"
        self.backup_directory = "backup"

        # 确保目录存在
        os.makedirs(self.watch_directory, exist_ok=True)
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.backup_directory, exist_ok=True)

        # 创建说明文件
        self._create_readme_file()
        
        # 支持的文件模式 - 简化为支持所有CSV文件
        self.supported_patterns = [
            # 任何CSV文件都可以，让验证函数来判断内容是否正确
        ]
    
    def is_stock_data_file(self, filename: str) -> bool:
        """
        判断文件是否为股票数据文件
        在 stock_name_list 目录中，所有CSV文件都被认为是潜在的股票数据文件
        具体验证通过 validate_stock_file 函数进行
        """
        return filename.lower().endswith('.csv')

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

    def _create_readme_file(self):
        """在监控目录创建说明文件"""
        readme_path = os.path.join(self.watch_directory, "README.md")

        if not os.path.exists(readme_path):
            readme_content = """# 股票名称列表目录

## 📁 目录说明
这个目录专门用于存放股票代码和名称的CSV文件。系统会自动扫描此目录，找到最新的股票数据文件并使用。

## 📋 文件格式要求
- **CSV文件** (必须是UTF-8编码)
- **必须包含的列**：
  - 股票代码列：`code` 或 `代码` 或 `股票代码`
  - 股票名称列：`name` 或 `名称` 或 `股票名称`

## 📝 文件命名
- 支持任何 `.csv` 文件名
- 系统会自动选择最新的文件（按修改时间或文件名中的日期）
- 建议使用包含日期的文件名，如：`stocks_20250620.csv`

## 🚀 使用方法
1. 将新的股票数据CSV文件放入此目录
2. 系统会自动检测并使用最新的文件
3. 可以通过Web界面手动触发更新
4. 旧文件会自动备份到 `backup` 目录

## 📊 文件示例格式
```csv
code,name
000001,平安银行
000002,万科A
600000,浦发银行
600036,招商银行
```

## ⚠️ 注意事项
- 确保CSV文件编码为UTF-8
- 股票代码应为6位数字
- 文件大小建议不超过50MB
- 系统会自动备份被替换的旧文件

## 📞 技术支持
如有问题，请检查日志文件或联系技术支持。
"""

            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
                logger.info(f"已创建说明文件: {readme_path}")
            except Exception as e:
                logger.error(f"创建说明文件失败: {e}")

    def scan_for_new_files(self) -> list:
        """扫描股票数据文件，返回最新的文件"""
        try:
            all_files = []

            # 获取所有CSV文件
            for filename in os.listdir(self.watch_directory):
                if self.is_stock_data_file(filename):
                    filepath = os.path.join(self.watch_directory, filename)
                    all_files.append(filepath)

            if not all_files:
                return []

            # 选择最新的文件
            latest_file = self._select_best_data_file(all_files)

            if latest_file:
                # 检查是否需要更新（文件是否比当前使用的更新）
                current_latest = os.path.join(self.data_directory, 'stock_list_latest.csv')
                if not os.path.exists(current_latest):
                    logger.info(f"未找到当前latest文件，将处理: {latest_file}")
                    return [latest_file]
                else:
                    # 比较修改时间
                    latest_mtime = os.path.getmtime(latest_file)
                    current_mtime = os.path.getmtime(current_latest)

                    logger.info(f"文件时间比较: {latest_file} ({latest_mtime}) vs current ({current_mtime})")

                    if latest_mtime > current_mtime:
                        logger.info(f"发现更新的文件: {latest_file}")
                        return [latest_file]
                    else:
                        logger.info(f"当前文件已是最新: {current_latest}")

                        # 额外检查：如果有多个文件，可能有新文件
                        if len(all_files) > 1:
                            # 按修改时间排序，检查是否有比当前latest更新的文件
                            sorted_files = sorted(all_files, key=os.path.getmtime, reverse=True)
                            newest_file = sorted_files[0]
                            if os.path.getmtime(newest_file) > current_mtime:
                                logger.info(f"发现最新文件: {newest_file}")
                                return [newest_file]

            return []

        except Exception as e:
            logger.error(f"扫描文件时发生错误: {e}")
            return []
    
    def validate_stock_file(self, filepath: str) -> dict:
        """验证股票数据文件的有效性"""
        result = {
            'valid': False,
            'error': None,
            'info': {}
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                result['error'] = "文件为空"
                return result
            
            # 尝试读取文件
            df = pd.read_csv(filepath, nrows=10)  # 只读取前10行进行验证
            
            # 检查列名
            columns = df.columns.tolist()
            has_code = any(col.lower() in ['code', '代码', '股票代码'] for col in columns)
            has_name = any(col.lower() in ['name', '名称', '股票名称'] for col in columns)
            
            if not (has_code and has_name):
                result['error'] = f"文件缺少必要的列（代码/名称），当前列: {columns}"
                return result
            
            # 检查数据行数
            total_rows = len(pd.read_csv(filepath))
            if total_rows < 10:
                result['error'] = f"数据行数太少: {total_rows} 行"
                return result
            
            result['valid'] = True
            result['info'] = {
                'columns': columns,
                'total_rows': total_rows,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
            
            return result
            
        except Exception as e:
            result['error'] = f"读取文件失败: {str(e)}"
            return result
    
    def backup_old_file(self, filename: str) -> bool:
        """备份旧文件"""
        try:
            data_filepath = os.path.join(self.data_directory, filename)
            if os.path.exists(data_filepath):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{os.path.splitext(filename)[0]}_backup_{timestamp}.csv"
                backup_filepath = os.path.join(self.backup_directory, backup_filename)
                
                shutil.copy2(data_filepath, backup_filepath)
                logger.info(f"已备份旧文件: {backup_filepath}")
                return True
            
            return True  # 如果文件不存在，也算成功
            
        except Exception as e:
            logger.error(f"备份文件失败: {e}")
            return False
    
    def install_new_file(self, source_filepath: str) -> bool:
        """安装新的股票数据文件"""
        try:
            filename = os.path.basename(source_filepath)
            
            # 验证文件
            validation = self.validate_stock_file(source_filepath)
            if not validation['valid']:
                logger.error(f"文件验证失败: {validation['error']}")
                return False
            
            logger.info(f"文件验证通过: {validation['info']}")
            
            # 备份旧文件
            if not self.backup_old_file(filename):
                logger.warning("备份旧文件失败，但继续安装新文件")
            
            # 复制新文件到data目录
            dest_filepath = os.path.join(self.data_directory, filename)
            shutil.copy2(source_filepath, dest_filepath)

            logger.info(f"新文件已安装: {dest_filepath}")

            # 如果文件名不包含latest，创建一个latest链接
            if 'latest' not in filename.lower():
                self.create_latest_link(filename)

            # 不移动原文件，保留在stock_name_list目录中
            logger.info(f"文件保留在原目录: {source_filepath}")

            return True
            
        except Exception as e:
            logger.error(f"安装文件失败: {e}")
            return False
    
    def create_latest_link(self, filename: str):
        """创建latest文件链接"""
        try:
            # 确定latest文件名
            base_name = os.path.splitext(filename)[0]
            if base_name.startswith('all_stocks_'):
                latest_filename = 'stock_list_latest.csv'
            else:
                latest_filename = 'stock_list_latest.csv'
            
            source_filepath = os.path.join(self.data_directory, filename)
            latest_filepath = os.path.join(self.data_directory, latest_filename)
            
            # 如果latest文件已存在，先备份
            if os.path.exists(latest_filepath):
                self.backup_old_file(latest_filename)
            
            # 复制文件（而不是创建链接，因为Windows链接可能有权限问题）
            shutil.copy2(source_filepath, latest_filepath)
            logger.info(f"已创建latest文件: {latest_filepath}")
            
        except Exception as e:
            logger.error(f"创建latest文件失败: {e}")

    def auto_update(self) -> dict:
        """自动更新股票数据文件"""
        result = {
            'updated': False,
            'new_files': [],
            'errors': []
        }
        
        logger.info("🔍 开始自动检查新的股票数据文件...")
        
        # 扫描新文件
        new_files = self.scan_for_new_files()
        
        if not new_files:
            logger.info("✅ 没有发现新的股票数据文件")
            return result
        
        logger.info(f"📁 发现 {len(new_files)} 个新文件: {[os.path.basename(f) for f in new_files]}")
        
        # 处理每个新文件
        for filepath in new_files:
            filename = os.path.basename(filepath)
            logger.info(f"📥 处理文件: {filename}")
            
            if self.install_new_file(filepath):
                result['new_files'].append(filename)
                result['updated'] = True
                logger.info(f"✅ 文件安装成功: {filename}")
            else:
                error_msg = f"文件安装失败: {filename}"
                result['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        if result['updated']:
            logger.info(f"🎉 自动更新完成，成功安装 {len(result['new_files'])} 个文件")
        
        return result
    
    def get_current_files_info(self) -> dict:
        """获取当前文件信息"""
        info = {
            'data_files': [],
            'backup_files': [],
            'watch_files': [],
            'processed_files': []
        }
        
        try:
            # 检查data目录
            if os.path.exists(self.data_directory):
                for filename in os.listdir(self.data_directory):
                    if self.is_stock_data_file(filename):
                        filepath = os.path.join(self.data_directory, filename)
                        file_info = {
                            'name': filename,
                            'path': filepath,
                            'size': os.path.getsize(filepath),
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        info['data_files'].append(file_info)
            
            # 检查备份目录
            if os.path.exists(self.backup_directory):
                for filename in os.listdir(self.backup_directory):
                    if filename.endswith('.csv'):
                        filepath = os.path.join(self.backup_directory, filename)
                        file_info = {
                            'name': filename,
                            'path': filepath,
                            'size': os.path.getsize(filepath),
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        info['backup_files'].append(file_info)
            
            # 检查监控目录
            for filename in os.listdir(self.watch_directory):
                if self.is_stock_data_file(filename):
                    filepath = os.path.join(self.watch_directory, filename)
                    file_info = {
                        'name': filename,
                        'path': filepath,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    info['watch_files'].append(file_info)

            # 已处理文件信息（简化版本，不再使用processed目录）
            # 可以显示备份文件作为已处理的文件

        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")

        return info


def main():
    """主函数"""
    print("🚀 自动文件管理器")
    print("=" * 50)
    
    manager = AutoFileManager()
    
    # 显示当前文件状态
    files_info = manager.get_current_files_info()
    
    print(f"📁 数据文件 ({len(files_info['data_files'])} 个):")
    for file_info in files_info['data_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB, {file_info['modified']})")
    
    print(f"\n📁 监控目录文件 ({len(files_info['watch_files'])} 个):")
    for file_info in files_info['watch_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB, {file_info['modified']})")

    print(f"\n📁 已处理文件 ({len(files_info['processed_files'])} 个):")
    for file_info in files_info['processed_files']:
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  - {file_info['name']} ({size_mb:.2f} MB, {file_info['modified']})")

    # 执行自动更新
    print(f"\n🔄 执行自动更新...")
    result = manager.auto_update()
    
    if result['updated']:
        print(f"✅ 更新成功！新安装文件: {result['new_files']}")
    else:
        print("ℹ️  没有需要更新的文件")
    
    if result['errors']:
        print(f"❌ 错误: {result['errors']}")


if __name__ == '__main__':
    main()
