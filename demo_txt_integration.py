#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示TXT格式股票列表与股票匹配器的集成使用
"""

import sys
import os
import pandas as pd
import logging
from datetime import datetime
from local_stock_data import LocalStockData

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_input_file():
    """创建示例输入文件用于演示"""
    sample_data = [
        {'股票名称': '平安银行', '参考价格': 10.45},
        {'股票名称': '万科A', '参考价格': 18.20},
        {'股票名称': '招商银行', '参考价格': 35.80},
        {'股票名称': '贵州茅台', '参考价格': 1680.0},
        {'股票名称': '中兴通讯', '参考价格': 28.50},
        {'股票名称': '东方财富', '参考价格': 15.60},
        {'股票名称': '华兴源创', '参考价格': 45.67},
        {'股票名称': '比亚迪', '参考价格': 250.0},
    ]
    
    df = pd.DataFrame(sample_data)
    filename = f"demo_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    return filename

def demonstrate_txt_integration():
    """演示TXT文件与股票匹配器的集成"""
    print("=" * 70)
    print("🔗 TXT格式股票列表与股票匹配器集成演示")
    print("=" * 70)
    
    try:
        # 1. 检查TXT文件
        print("\n📁 1. 检查TXT格式股票文件")
        print("-" * 50)
        
        txt_files = [f for f in os.listdir(".") if f.startswith("all_stocks_") and f.endswith(".txt")]
        if txt_files:
            txt_file = txt_files[0]
            size = os.path.getsize(txt_file)
            print(f"✅ 找到TXT文件: {txt_file} ({size:,} 字节)")
        else:
            print("❌ 未找到TXT格式股票文件")
            return False
        
        # 2. 初始化股票数据
        print("\n🔧 2. 初始化股票数据源")
        print("-" * 50)
        
        stock_data = LocalStockData(use_offline_data=True)
        info = stock_data.get_data_info()
        
        print(f"✅ 数据源: {info['数据源']}")
        print(f"✅ 股票数量: {info['总股票数']:,}")
        
        if '市场分布' in info:
            print("✅ 市场分布:")
            for market, count in info['市场分布'].items():
                print(f"   - {market}: {count:,} 只")
        
        # 3. 创建示例输入文件
        print("\n📝 3. 创建示例输入文件")
        print("-" * 50)
        
        input_file = create_sample_input_file()
        print(f"✅ 创建示例文件: {input_file}")
        
        # 读取示例文件
        input_data = pd.read_csv(input_file, encoding='utf-8-sig')
        print(f"✅ 示例数据包含 {len(input_data)} 只股票:")
        for _, row in input_data.iterrows():
            print(f"   - {row['股票名称']}: {row['参考价格']}")
        
        # 4. 执行股票匹配
        print("\n🔍 4. 执行股票名称匹配")
        print("-" * 50)
        
        results = []
        for _, row in input_data.iterrows():
            stock_name = row['股票名称']
            ref_price = row['参考价格']
            
            # 搜索股票
            search_result = stock_data.search_by_name(stock_name)
            
            if search_result is not None and not search_result.empty:
                matched_stock = search_result.iloc[0]
                result = {
                    '原始名称': stock_name,
                    '参考价格': ref_price,
                    '匹配代码': matched_stock['代码'],
                    '匹配名称': matched_stock['名称'],
                    '匹配状态': '成功',
                    '匹配类型': '精确匹配' if stock_name == matched_stock['名称'] else '模糊匹配'
                }
                print(f"   ✅ {stock_name} -> {matched_stock['代码']} ({matched_stock['名称']})")
            else:
                result = {
                    '原始名称': stock_name,
                    '参考价格': ref_price,
                    '匹配代码': '',
                    '匹配名称': '',
                    '匹配状态': '失败',
                    '匹配类型': '未找到'
                }
                print(f"   ❌ {stock_name} -> 未找到匹配")
            
            results.append(result)
        
        # 5. 保存匹配结果
        print("\n💾 5. 保存匹配结果")
        print("-" * 50)
        
        results_df = pd.DataFrame(results)
        output_file = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ 结果已保存: {output_file}")
        print(f"✅ 匹配统计:")
        
        success_count = len([r for r in results if r['匹配状态'] == '成功'])
        total_count = len(results)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"   - 成功匹配: {success_count}/{total_count} ({success_rate:.1f}%)")
        print(f"   - 精确匹配: {len([r for r in results if r['匹配类型'] == '精确匹配'])}")
        print(f"   - 模糊匹配: {len([r for r in results if r['匹配类型'] == '模糊匹配'])}")
        
        # 6. 显示结果预览
        print("\n📊 6. 结果预览")
        print("-" * 50)
        
        print("匹配结果:")
        for result in results:
            status_icon = "✅" if result['匹配状态'] == '成功' else "❌"
            print(f"   {status_icon} {result['原始名称']} -> {result['匹配代码']} ({result['匹配名称']})")
        
        # 7. 清理临时文件
        print("\n🧹 7. 清理临时文件")
        print("-" * 50)
        
        if os.path.exists(input_file):
            os.remove(input_file)
            print(f"✅ 删除输入文件: {input_file}")
        
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"✅ 删除输出文件: {output_file}")
        
        print("\n" + "=" * 70)
        print("🎉 TXT格式股票列表集成演示完成！")
        print("=" * 70)
        
        # 总结
        print(f"\n📋 演示总结:")
        print(f"   - 使用了包含 {info['总股票数']:,} 只股票的TXT数据源")
        print(f"   - 成功匹配了 {success_count}/{total_count} 只股票")
        print(f"   - 匹配成功率: {success_rate:.1f}%")
        print(f"   - 数据源: {info['数据源']}")
        
        print(f"\n💡 使用建议:")
        print(f"   - TXT文件提供了完整的股票列表，匹配准确性高")
        print(f"   - 可以直接在股票匹配器中使用TXT数据源")
        print(f"   - 建议定期更新TXT文件以获取最新股票信息")
        
        return True
        
    except Exception as e:
        logger.error(f"演示过程中发生错误: {str(e)}")
        print(f"\n❌ 演示失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = demonstrate_txt_integration()
    
    if success:
        print("\n✅ 演示成功完成！")
        return 0
    else:
        print("\n❌ 演示失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
