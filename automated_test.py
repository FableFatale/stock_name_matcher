#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票匹配系统自动化测试脚本
"""

import os
import sys
import time
import requests
import subprocess
import pandas as pd
import logging
from datetime import datetime
import json

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockMatcherTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_file = "20250617171501.csv"
        self.web_process = None
        self.results = {
            'command_line': {},
            'web_interface': {},
            'comparison': {}
        }
    
    def start_web_server(self):
        """启动Web服务器"""
        logger.info("🚀 启动Web服务器...")
        try:
            # 启动Web应用
            self.web_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # 等待服务器启动
            time.sleep(5)
            
            # 检查服务器是否启动成功
            for i in range(10):
                try:
                    response = requests.get(f"{self.base_url}/api/status", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ Web服务器启动成功")
                        return True
                except:
                    time.sleep(2)
            
            logger.error("❌ Web服务器启动失败")
            return False
            
        except Exception as e:
            logger.error(f"❌ 启动Web服务器异常: {e}")
            return False
    
    def stop_web_server(self):
        """停止Web服务器"""
        if self.web_process:
            logger.info("🛑 停止Web服务器...")
            self.web_process.terminate()
            self.web_process.wait()
    
    def test_command_line(self):
        """测试命令行工具"""
        logger.info("📋 测试命令行工具...")
        
        try:
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"result/test_cli_{timestamp}.csv"
            
            # 执行命令行工具
            cmd = [
                sys.executable, "stock_name_matcher.py",
                self.test_file,
                "-o", output_file,
                "--mode", "code"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            end_time = time.time()
            
            if result.returncode == 0:
                # 读取结果文件
                if os.path.exists(output_file):
                    df = pd.read_csv(output_file)
                    success_count = len(df[df['匹配状态'] == '匹配成功'])
                    total_count = len(df)
                    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
                    
                    self.results['command_line'] = {
                        'status': 'success',
                        'total': total_count,
                        'success': success_count,
                        'success_rate': success_rate,
                        'execution_time': end_time - start_time,
                        'output_file': output_file
                    }
                    
                    logger.info(f"✅ 命令行测试成功: {success_count}/{total_count} ({success_rate:.1f}%)")
                else:
                    self.results['command_line'] = {'status': 'error', 'message': '输出文件不存在'}
                    logger.error("❌ 命令行测试失败: 输出文件不存在")
            else:
                self.results['command_line'] = {
                    'status': 'error', 
                    'message': result.stderr,
                    'stdout': result.stdout
                }
                logger.error(f"❌ 命令行测试失败: {result.stderr}")
                
        except Exception as e:
            self.results['command_line'] = {'status': 'error', 'message': str(e)}
            logger.error(f"❌ 命令行测试异常: {e}")
    
    def test_web_interface(self):
        """测试Web界面"""
        logger.info("🌐 测试Web界面...")
        
        try:
            # 1. 测试API状态
            response = requests.get(f"{self.base_url}/api/status")
            if response.status_code != 200:
                self.results['web_interface'] = {'status': 'error', 'message': 'API状态异常'}
                logger.error("❌ Web API状态异常")
                return
            
            api_data = response.json()
            logger.info(f"📊 API状态: {api_data.get('status')}, 股票数量: {api_data.get('stock_count')}")
            
            # 2. 上传文件
            if not os.path.exists(self.test_file):
                self.results['web_interface'] = {'status': 'error', 'message': '测试文件不存在'}
                logger.error(f"❌ 测试文件不存在: {self.test_file}")
                return
            
            with open(self.test_file, 'rb') as f:
                files = {'file': (self.test_file, f, 'text/csv')}
                response = requests.post(f"{self.base_url}/upload", files=files)
            
            if response.status_code != 200:
                self.results['web_interface'] = {'status': 'error', 'message': '文件上传失败'}
                logger.error("❌ 文件上传失败")
                return
            
            upload_data = response.json()
            filename = upload_data.get('filename')
            logger.info(f"📁 文件上传成功: {filename}")
            
            # 3. 处理文件
            process_data = {
                'filename': filename,
                'code_column': '股票代码',
                'price_column': '买入价格',
                'api_source': 'akshare',
                'enable_cross_validation': False
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/process",
                json=process_data,
                headers={'Content-Type': 'application/json'}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result_data = response.json()
                stats = result_data.get('statistics', {})
                
                self.results['web_interface'] = {
                    'status': 'success',
                    'total': stats.get('total', 0),
                    'success': stats.get('success', 0),
                    'success_rate': stats.get('success_rate', 0),
                    'execution_time': end_time - start_time,
                    'result_file': result_data.get('result_file', ''),
                    'preview': result_data.get('preview', [])
                }
                
                logger.info(f"✅ Web界面测试成功: {stats.get('success', 0)}/{stats.get('total', 0)} ({stats.get('success_rate', 0):.1f}%)")
            else:
                self.results['web_interface'] = {'status': 'error', 'message': response.text}
                logger.error(f"❌ Web界面处理失败: {response.text}")
                
        except Exception as e:
            self.results['web_interface'] = {'status': 'error', 'message': str(e)}
            logger.error(f"❌ Web界面测试异常: {e}")
    
    def compare_results(self):
        """比较命令行和Web界面的结果"""
        logger.info("🔍 比较测试结果...")
        
        cli_result = self.results.get('command_line', {})
        web_result = self.results.get('web_interface', {})
        
        if cli_result.get('status') == 'success' and web_result.get('status') == 'success':
            cli_success_rate = cli_result.get('success_rate', 0)
            web_success_rate = web_result.get('success_rate', 0)
            
            rate_diff = abs(cli_success_rate - web_success_rate)
            
            self.results['comparison'] = {
                'cli_success_rate': cli_success_rate,
                'web_success_rate': web_success_rate,
                'rate_difference': rate_diff,
                'consistent': rate_diff < 1.0,  # 允许1%的误差
                'cli_time': cli_result.get('execution_time', 0),
                'web_time': web_result.get('execution_time', 0)
            }
            
            if rate_diff < 1.0:
                logger.info(f"✅ 结果一致: CLI({cli_success_rate:.1f}%) vs Web({web_success_rate:.1f}%)")
            else:
                logger.warning(f"⚠️ 结果不一致: CLI({cli_success_rate:.1f}%) vs Web({web_success_rate:.1f}%)")
        else:
            self.results['comparison'] = {
                'consistent': False,
                'message': '无法比较，存在测试失败'
            }
            logger.error("❌ 无法比较结果，存在测试失败")
    
    def generate_report(self):
        """生成测试报告"""
        logger.info("📊 生成测试报告...")
        
        report = {
            'test_time': datetime.now().isoformat(),
            'test_file': self.test_file,
            'results': self.results
        }
        
        # 保存JSON报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要报告
        print("\n" + "="*60)
        print("📋 股票匹配系统自动化测试报告")
        print("="*60)
        print(f"测试时间: {report['test_time']}")
        print(f"测试文件: {report['test_file']}")
        print()
        
        # 命令行结果
        cli_result = self.results.get('command_line', {})
        print("🖥️ 命令行工具测试:")
        if cli_result.get('status') == 'success':
            print(f"   状态: ✅ 成功")
            print(f"   成功率: {cli_result.get('success_rate', 0):.1f}% ({cli_result.get('success', 0)}/{cli_result.get('total', 0)})")
            print(f"   执行时间: {cli_result.get('execution_time', 0):.2f}秒")
        else:
            print(f"   状态: ❌ 失败")
            print(f"   错误: {cli_result.get('message', '未知错误')}")
        
        # Web界面结果
        web_result = self.results.get('web_interface', {})
        print("\n🌐 Web界面测试:")
        if web_result.get('status') == 'success':
            print(f"   状态: ✅ 成功")
            print(f"   成功率: {web_result.get('success_rate', 0):.1f}% ({web_result.get('success', 0)}/{web_result.get('total', 0)})")
            print(f"   执行时间: {web_result.get('execution_time', 0):.2f}秒")
        else:
            print(f"   状态: ❌ 失败")
            print(f"   错误: {web_result.get('message', '未知错误')}")
        
        # 比较结果
        comparison = self.results.get('comparison', {})
        print("\n🔍 结果比较:")
        if comparison.get('consistent'):
            print("   一致性: ✅ 结果一致")
        else:
            print("   一致性: ❌ 结果不一致")
            if 'rate_difference' in comparison:
                print(f"   差异: {comparison['rate_difference']:.1f}%")
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        print("="*60)
        
        return report_file
    
    def run_full_test(self):
        """运行完整测试"""
        logger.info("🧪 开始股票匹配系统自动化测试...")
        
        try:
            # 1. 测试命令行工具
            self.test_command_line()
            
            # 2. 启动Web服务器
            if self.start_web_server():
                # 3. 测试Web界面
                self.test_web_interface()
                
                # 4. 停止Web服务器
                self.stop_web_server()
            
            # 5. 比较结果
            self.compare_results()
            
            # 6. 生成报告
            report_file = self.generate_report()
            
            return report_file
            
        except Exception as e:
            logger.error(f"❌ 测试过程异常: {e}")
            self.stop_web_server()
            return None

def main():
    """主函数"""
    tester = StockMatcherTester()
    report_file = tester.run_full_test()
    
    if report_file:
        logger.info(f"🎉 测试完成，报告文件: {report_file}")
    else:
        logger.error("❌ 测试失败")

if __name__ == "__main__":
    main()
