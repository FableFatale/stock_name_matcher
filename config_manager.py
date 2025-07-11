#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
管理API Keys、数据源配置和系统设置
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_data = {}
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 默认配置结构
        self.default_config = {
            "api_keys": {
                "akshare": "",
                "tushare": "",
                "sina": "",
                "tencent": "",
                "eastmoney": "",
                "netease": "",
                "xueqiu": "",
                "alpha_vantage": "",
                "quandl": ""
            },
            "data_sources": {
                "primary": "local",
                "fallback": ["akshare", "sina", "tencent"],
                "timeout": 30,
                "retry_count": 3,
                "cache_duration": 3600,
                "failure_threshold": 3,  # 失败阈值
                "suggestion_cooldown": 3600  # 建议冷却时间（秒）
            },
            "data_source_monitoring": {
                "failure_counts": {},
                "last_failures": {},
                "last_suggestions": {},
                "total_requests": {},
                "success_rates": {}
            },
            "system_settings": {
                "max_file_size_mb": 16,
                "allowed_file_types": [".csv", ".xlsx", ".xls"],
                "auto_backup": True,
                "log_level": "INFO",
                "performance_optimization": True
            },
            "user_preferences": {
                "default_api_source": "local",
                "enable_cross_validation": False,
                "auto_update_stock_list": True,
                "notification_enabled": True
            },
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }
        
        self.load_config()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        key_file = ".encryption_key"
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"无法读取加密密钥文件: {e}")
        
        # 创建新的加密密钥
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # 设置文件权限（仅所有者可读写）
            os.chmod(key_file, 0o600)
            logger.info("已创建新的加密密钥")
        except Exception as e:
            logger.error(f"无法保存加密密钥: {e}")
        
        return key
    
    def _encrypt_value(self, value: str) -> str:
        """加密敏感值"""
        if not value:
            return ""
        try:
            encrypted = self.cipher_suite.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"加密失败: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """解密敏感值"""
        if not encrypted_value:
            return ""
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return encrypted_value
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                
                # 合并默认配置（处理新增的配置项）
                self._merge_default_config()
                
                logger.info("配置文件加载成功")
                return True
            else:
                # 创建默认配置文件
                self.config_data = self.default_config.copy()
                self.save_config()
                logger.info("已创建默认配置文件")
                return True
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config_data = self.default_config.copy()
            return False
    
    def _merge_default_config(self):
        """合并默认配置，确保所有必要的配置项都存在"""
        def merge_dict(default: dict, current: dict) -> dict:
            for key, value in default.items():
                if key not in current:
                    current[key] = value
                elif isinstance(value, dict) and isinstance(current[key], dict):
                    merge_dict(value, current[key])
            return current
        
        self.config_data = merge_dict(self.default_config, self.config_data)
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            # 更新最后修改时间
            self.config_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("配置文件保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get_api_key(self, source: str) -> str:
        """获取API密钥（自动解密）"""
        encrypted_key = self.config_data.get("api_keys", {}).get(source, "")
        return self._decrypt_value(encrypted_key)
    
    def set_api_key(self, source: str, api_key: str) -> bool:
        """设置API密钥（自动加密）"""
        try:
            if "api_keys" not in self.config_data:
                self.config_data["api_keys"] = {}
            
            encrypted_key = self._encrypt_value(api_key)
            self.config_data["api_keys"][source] = encrypted_key
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"设置API密钥失败: {e}")
            return False
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """获取数据源配置"""
        return self.config_data.get("data_sources", {})
    
    def set_data_source_config(self, config: Dict[str, Any]) -> bool:
        """设置数据源配置"""
        try:
            self.config_data["data_sources"] = config
            return self.save_config()
        except Exception as e:
            logger.error(f"设置数据源配置失败: {e}")
            return False
    
    def get_system_settings(self) -> Dict[str, Any]:
        """获取系统设置"""
        return self.config_data.get("system_settings", {})
    
    def set_system_settings(self, settings: Dict[str, Any]) -> bool:
        """设置系统设置"""
        try:
            self.config_data["system_settings"] = settings
            return self.save_config()
        except Exception as e:
            logger.error(f"设置系统设置失败: {e}")
            return False
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.config_data.get("user_preferences", {})
    
    def set_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """设置用户偏好"""
        try:
            self.config_data["user_preferences"] = preferences
            return self.save_config()
        except Exception as e:
            logger.error(f"设置用户偏好失败: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置（API密钥已解密）"""
        config_copy = self.config_data.copy()
        
        # 解密API密钥
        if "api_keys" in config_copy:
            decrypted_keys = {}
            for source, encrypted_key in config_copy["api_keys"].items():
                decrypted_keys[source] = self._decrypt_value(encrypted_key)
            config_copy["api_keys"] = decrypted_keys
        
        return config_copy
    
    def test_api_connection(self, source: str) -> Dict[str, Any]:
        """测试API连接"""
        api_key = self.get_api_key(source)
        
        result = {
            "source": source,
            "status": "unknown",
            "message": "",
            "has_api_key": bool(api_key),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if source == "local":
                # 测试本地数据源
                from local_stock_data import LocalStockData
                local_data = LocalStockData()
                stock_list = local_data.get_stock_list()
                
                if stock_list is not None and len(stock_list) > 0:
                    result["status"] = "success"
                    result["message"] = f"本地数据源正常，共 {len(stock_list)} 只股票"
                else:
                    result["status"] = "error"
                    result["message"] = "本地数据源无数据"
            
            elif source == "akshare":
                # 测试AKShare连接
                try:
                    import akshare as ak
                    # 简单测试：获取股票基本信息
                    test_data = ak.stock_zh_a_spot_em()
                    if test_data is not None and not test_data.empty:
                        result["status"] = "success"
                        result["message"] = f"AKShare连接正常，获取到 {len(test_data)} 只股票数据"
                    else:
                        result["status"] = "error"
                        result["message"] = "AKShare返回空数据"
                except Exception as e:
                    result["status"] = "error"
                    result["message"] = f"AKShare连接失败: {str(e)}"
            
            else:
                # 其他数据源暂时标记为未实现
                result["status"] = "not_implemented"
                result["message"] = f"数据源 {source} 的连接测试尚未实现"
        
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"测试连接时发生错误: {str(e)}"
        
        return result
    
    def record_data_source_failure(self, source: str, error_type: str = "timeout") -> bool:
        """记录数据源失败"""
        try:
            monitoring = self.config_data.get("data_source_monitoring", {})

            # 初始化监控数据
            if "failure_counts" not in monitoring:
                monitoring["failure_counts"] = {}
            if "last_failures" not in monitoring:
                monitoring["last_failures"] = {}
            if "total_requests" not in monitoring:
                monitoring["total_requests"] = {}

            # 记录失败
            monitoring["failure_counts"][source] = monitoring["failure_counts"].get(source, 0) + 1
            monitoring["last_failures"][source] = {
                "timestamp": datetime.now().isoformat(),
                "error_type": error_type
            }
            monitoring["total_requests"][source] = monitoring["total_requests"].get(source, 0) + 1

            # 更新配置
            self.config_data["data_source_monitoring"] = monitoring
            self.save_config()

            logger.info(f"记录数据源失败: {source} - {error_type}")
            return True

        except Exception as e:
            logger.error(f"记录数据源失败时出错: {e}")
            return False

    def record_data_source_success(self, source: str) -> bool:
        """记录数据源成功"""
        try:
            monitoring = self.config_data.get("data_source_monitoring", {})

            # 初始化监控数据
            if "total_requests" not in monitoring:
                monitoring["total_requests"] = {}

            # 记录成功（重置失败计数）
            if "failure_counts" in monitoring:
                monitoring["failure_counts"][source] = 0

            monitoring["total_requests"][source] = monitoring["total_requests"].get(source, 0) + 1

            # 更新配置
            self.config_data["data_source_monitoring"] = monitoring
            self.save_config()

            return True

        except Exception as e:
            logger.error(f"记录数据源成功时出错: {e}")
            return False

    def should_suggest_api_config(self, source: str) -> Dict[str, Any]:
        """检查是否应该建议配置API"""
        try:
            monitoring = self.config_data.get("data_source_monitoring", {})
            data_sources_config = self.config_data.get("data_sources", {})

            failure_threshold = data_sources_config.get("failure_threshold", 3)
            suggestion_cooldown = data_sources_config.get("suggestion_cooldown", 3600)

            failure_count = monitoring.get("failure_counts", {}).get(source, 0)
            last_suggestion = monitoring.get("last_suggestions", {}).get(source)

            # 检查是否达到失败阈值
            should_suggest = failure_count >= failure_threshold

            # 检查冷却时间
            if should_suggest and last_suggestion:
                try:
                    last_suggestion_time = datetime.fromisoformat(last_suggestion)
                    time_since_last = (datetime.now() - last_suggestion_time).total_seconds()
                    if time_since_last < suggestion_cooldown:
                        should_suggest = False
                except:
                    pass

            # 检查是否已经配置了API密钥
            api_key = self.get_api_key(source)
            has_api_key = bool(api_key)

            result = {
                "should_suggest": should_suggest and not has_api_key,
                "failure_count": failure_count,
                "failure_threshold": failure_threshold,
                "has_api_key": has_api_key,
                "last_failure": monitoring.get("last_failures", {}).get(source),
                "suggestion_reason": self._get_suggestion_reason(source, failure_count, has_api_key)
            }

            # 如果应该建议，记录建议时间
            if result["should_suggest"]:
                self._record_suggestion_time(source)

            return result

        except Exception as e:
            logger.error(f"检查API配置建议时出错: {e}")
            return {
                "should_suggest": False,
                "failure_count": 0,
                "failure_threshold": 3,
                "has_api_key": False,
                "suggestion_reason": "检查失败"
            }

    def _get_suggestion_reason(self, source: str, failure_count: int, has_api_key: bool) -> str:
        """获取建议原因"""
        if has_api_key:
            return f"{source} API密钥已配置"
        elif failure_count >= 3:
            return f"{source} 连续失败 {failure_count} 次，建议配置API密钥以获得更稳定的服务"
        else:
            return f"{source} 运行正常"

    def _record_suggestion_time(self, source: str) -> bool:
        """记录建议时间"""
        try:
            monitoring = self.config_data.get("data_source_monitoring", {})
            if "last_suggestions" not in monitoring:
                monitoring["last_suggestions"] = {}

            monitoring["last_suggestions"][source] = datetime.now().isoformat()
            self.config_data["data_source_monitoring"] = monitoring
            self.save_config()

            return True
        except Exception as e:
            logger.error(f"记录建议时间失败: {e}")
            return False

    def get_data_source_stats(self) -> Dict[str, Any]:
        """获取数据源统计信息"""
        try:
            monitoring = self.config_data.get("data_source_monitoring", {})

            stats = {}
            for source in ["local", "akshare", "sina", "tencent", "eastmoney", "netease", "xueqiu"]:
                failure_count = monitoring.get("failure_counts", {}).get(source, 0)
                total_requests = monitoring.get("total_requests", {}).get(source, 0)
                success_rate = ((total_requests - failure_count) / total_requests * 100) if total_requests > 0 else 100

                suggestion_info = self.should_suggest_api_config(source)

                stats[source] = {
                    "failure_count": failure_count,
                    "total_requests": total_requests,
                    "success_rate": round(success_rate, 1),
                    "last_failure": monitoring.get("last_failures", {}).get(source),
                    "should_suggest_api": suggestion_info["should_suggest"],
                    "suggestion_reason": suggestion_info["suggestion_reason"],
                    "has_api_key": bool(self.get_api_key(source))
                }

            return stats

        except Exception as e:
            logger.error(f"获取数据源统计失败: {e}")
            return {}

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要信息"""
        api_keys_status = {}
        for source in self.config_data.get("api_keys", {}):
            api_key = self.get_api_key(source)
            api_keys_status[source] = {
                "configured": bool(api_key),
                "length": len(api_key) if api_key else 0
            }

        return {
            "version": self.config_data.get("version", "unknown"),
            "last_updated": self.config_data.get("last_updated", "unknown"),
            "api_keys_status": api_keys_status,
            "primary_data_source": self.config_data.get("data_sources", {}).get("primary", "unknown"),
            "system_settings": self.config_data.get("system_settings", {}),
            "user_preferences": self.config_data.get("user_preferences", {}),
            "data_source_stats": self.get_data_source_stats()
        }

# 全局配置管理器实例
config_manager = ConfigManager()
