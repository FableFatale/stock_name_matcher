# 股票代码名称补全工具

[![Version](https://img.shields.io/badge/version-v2.0.0-blue.svg)](https://github.com/your-repo/releases)
[![智能API建议](https://img.shields.io/badge/🧠智能API建议-NEW-brightgreen.svg)](#智能api配置建议演示)
[![安全配置](https://img.shields.io/badge/🔐安全配置-加密存储-orange.svg)](#股票数据管理功能全新升级)
[![实时监控](https://img.shields.io/badge/📊实时监控-状态监控-purple.svg)](#数据源状态监控)

[English](README_EN.md) | 中文

一个智能的股票信息处理工具，提供**命令行**和**Web界面**两种使用方式，具备**🧠智能API配置建议**和**🔐全面的股票数据管理**功能：

> **🎉 v2.0.0 重大更新**：新增智能API配置建议功能，自动检测数据源问题并提供配置建议，大幅提升用户体验！

## 🌐 Web界面（推荐）
- **现代化Web界面**：拖拽上传、实时处理、在线预览
- **零配置使用**：自动检测列名，一键处理
- **实时反馈**：处理进度、统计结果、错误提示
- **移动端支持**：响应式设计，手机电脑都能用
- **🧠 智能API建议**：自动检测数据源问题并建议配置API密钥
- **🔐 安全配置管理**：加密存储API密钥，支持多数据源配置

## 💻 命令行工具
1. **股票名称匹配**：根据股票名称匹配股票代码和详细信息
2. **股票代码名称补全**：根据股票代码补全股票名称和详细信息

使用免费的AKShare API来获取最新的A股股票数据。

## 🌟 主要特点

### 🎯 核心功能
- **双模式支持**：股票名称匹配 + 股票代码名称补全
- **多种匹配策略**：精确匹配、模糊匹配、包含匹配
- **价格验证**：结合参考价格提高匹配准确性
- **自动模式检测**：自动识别输入数据类型并选择处理模式
- **自动列检测**：自动识别股票名称、代码和价格列
- **详细结果**：提供匹配度、备选方案、市场数据等详细信息

### 🧠 智能化特性（新）
- **智能API配置建议**：自动检测免费数据源连续失败，智能提示配置API密钥
- **失败监控机制**：实时监控数据源状态，记录失败次数和类型
- **建议冷却机制**：避免重复提示，提升用户体验
- **一键配置跳转**：快速跳转到API配置区域
- **多数据源状态监控**：实时显示各数据源的成功率和连接状态

### 🔐 数据管理与安全
- **加密API密钥存储**：使用cryptography库安全存储敏感信息
- **多数据源支持**：AKShare、Tushare、Alpha Vantage、Quandl等
- **配置文件管理**：统一的配置管理系统，支持备份和版本控制
- **股票列表管理**：支持上传自定义股票列表CSV文件
- **自动文件验证**：上传文件的格式验证和错误提示

### 📊 技术特性
- **代码格式验证**：验证股票代码格式的有效性
- **离线股票数据**：支持从API获取完整股票列表并离线使用
- **TXT格式支持**：支持TXT格式股票列表文件（如 all_stocks_20250616.txt）
- **多格式支持**：支持Excel (.xlsx, .xls)、CSV和TXT文件
- **性能优化**：并行处理，提升大文件处理速度

## 🧠 智能API配置建议演示

当免费数据源出现连续失败时，系统会智能提示用户配置API密钥：

```
用户选择AKShare数据源 → 连续3次超时失败 → 系统显示建议：

⚠️ 建议配置API密钥
AKShare连续失败3次，建议配置API密钥以获得更稳定的服务
[立即配置] [关闭]
```

**智能特性：**
- 🔍 **自动检测**：监控数据源连接状态和失败次数
- 💡 **智能建议**：达到失败阈值时自动提示配置API密钥
- ⏰ **冷却机制**：避免重复提示，默认冷却1小时
- 🔧 **快速配置**：一键跳转到API配置区域
- ✅ **自动停止**：配置API密钥后自动停止建议

## 🚀 快速开始

### 🌐 方式一：Web界面（推荐）
```bash
# 1. 安装依赖
python install_dependencies.py

# 2. 启动Web应用
python start_web_app.py

# 3. 浏览器自动打开 http://localhost:5000
```

**Web界面特点：**
- 🖱️ 拖拽上传CSV/Excel文件
- 🤖 自动检测股票代码和价格列
- 📊 实时显示处理进度和统计结果
- 💾 一键下载处理结果到result文件夹
- 🧠 **智能API建议**：自动检测数据源问题并提供配置建议
- 🔐 **安全配置管理**：加密存储API密钥，支持多数据源
- 📈 **状态监控**：实时显示各数据源的连接状态和成功率
- 📁 **数据管理**：支持上传自定义股票列表，自动验证格式
- 📱 支持手机和电脑访问

### 💻 方式二：一键安装（命令行）
```bash
python setup.py
```

### 🎮 方式三：交互式界面
```bash
python start.py
```

### 🔧 方式四：分步安装
```bash
# 1. 环境检查
python check_setup.py

# 2. 安装依赖
python install_dependencies.py
# 或者：pip install -r requirements.txt

# 3. 快速演示
python quick_start.py

# 4. 使用您的文件
python stock_name_matcher.py your_file.xlsx
```

### 🗂️ 方式五：获取完整股票列表（新功能）
```bash
# 获取所有A股股票代码和名称
python update_stock_list.py

# 只获取基本信息（代码和名称）
python update_stock_list.py --basic-only

# 按市场分别获取
python update_stock_list.py --by-market

# 显示统计信息
python update_stock_list.py --stats

# 演示完整功能
python demo_stock_fetcher.py
```

### 📄 方式六：使用TXT格式股票列表（新功能）
```bash
# 管理TXT格式股票文件
python txt_stock_manager.py

# 列出可用的TXT文件
python txt_stock_manager.py --list

# 分析TXT文件内容
python txt_stock_manager.py --analyze all_stocks_20250616.txt

# 将TXT文件转换为CSV格式
python txt_stock_manager.py --convert all_stocks_20250616.txt

# 测试TXT文件的搜索功能
python txt_stock_manager.py --test all_stocks_20250616.txt
```

### Windows用户
双击运行 `run_stock_matcher.bat` 获得图形化菜单界面。

## 📋 使用方法

### 基本用法

#### 自动模式（推荐）
```bash
# 自动检测输入数据类型并选择处理模式
python stock_name_matcher.py input_file.xlsx
```

#### 股票名称匹配模式
```bash
# 根据股票名称匹配代码
python stock_name_matcher.py stock_names.xlsx --mode name

# 指定列名
python stock_name_matcher.py stock_names.xlsx -n "股票名称" -p "价格"
```

#### 股票代码名称补全模式
```bash
# 根据股票代码补全名称
python stock_name_matcher.py stock_codes.csv --mode code

# 指定列名
python stock_name_matcher.py stock_codes.csv -c "代码" -p "价格"
```

#### 完整参数示例
```bash
python stock_name_matcher.py input_file.xlsx \
    --output results.csv \
    --name-column "股票名称" \
    --code-column "股票代码" \
    --price-column "参考价格" \
    --mode auto
```

### Windows用户
双击运行 `run_stock_matcher.bat` 获得图形化菜单界面。

## 📊 输入文件格式

### 股票名称匹配模式

#### Excel文件示例
| 股票名称 | 参考价格 |
|---------|---------|
| 平安银行 | 10.45   |
| 招商银行 | 35.20   |
| 中国平安 | 45.80   |

#### CSV文件示例
```csv
股票名称,参考价格
平安银行,10.45
招商银行,35.20
中国平安,45.80
```

#### TXT格式股票列表示例
```txt
# 所有A股股票列表 (更新时间: 2025-06-16)
# 格式: 股票代码,股票名称
000001,平安银行
000002,万科A
600036,招商银行
600519,贵州茅台
300059,东方财富
688001,华兴源创
```

### 股票代码名称补全模式

#### Excel文件示例
| 股票代码 | 参考价格 |
|---------|---------|
| 000001  | 10.45   |
| 600036  | 35.20   |
| 601318  | 45.80   |

#### CSV文件示例
```csv
股票代码,参考价格
000001,10.45
600036,35.20
601318,45.80
```

## 📈 输出结果

### 股票名称匹配模式输出
生成的CSV文件包含以下列：
- **原始名称**: 输入的股票名称
- **参考价格**: 输入的参考价格
- **匹配股票代码**: 匹配到的股票代码
- **匹配股票名称**: 匹配到的股票名称
- **当前价格**: 当前市场价格
- **匹配类型**: 匹配方式（精确匹配/模糊匹配/包含匹配）
- **匹配度**: 匹配相似度（0-100）
- **价格差异**: 与参考价格的差异
- **备选1_代码/名称**: 第二个最佳匹配
- **备选2_代码/名称**: 第三个最佳匹配

### 股票代码名称补全模式输出
生成的CSV文件包含以下列：
- **原始代码**: 输入的股票代码
- **参考价格**: 输入的参考价格
- **匹配状态**: 匹配状态（匹配成功/代码格式无效/未找到匹配）
- **股票代码**: 验证后的股票代码
- **股票名称**: 股票名称
- **当前价格**: 当前市场价格
- **价格差异**: 与参考价格的差异
- **匹配类型**: 匹配方式（代码精确匹配/格式验证失败/代码不存在）
- **涨跌幅**: 当日涨跌幅
- **涨跌额**: 当日涨跌额
- **成交量**: 成交量
- **成交额**: 成交额
- **市盈率**: 市盈率
- **市净率**: 市净率

## 🔧 处理策略

### 股票名称匹配策略

#### 1. 精确匹配
完全匹配股票名称，匹配度为100%

#### 2. 模糊匹配
使用模糊字符串匹配算法，处理拼写差异和简称

#### 3. 包含匹配
检查股票名称是否包含输入的关键词

#### 4. 价格验证
如果提供了参考价格，会优先选择价格接近的股票

### 股票代码名称补全策略

#### 1. 代码格式验证
验证股票代码是否符合A股代码格式：
- 沪市：600xxx, 601xxx, 603xxx, 605xxx, 688xxx
- 深市：000xxx, 001xxx, 002xxx, 003xxx
- 创业板：300xxx
- 科创板：688xxx

#### 2. 精确代码匹配
在股票数据库中查找完全匹配的股票代码

#### 3. 价格验证
结合参考价格验证匹配结果的准确性

## 🧪 测试

运行完整测试套件：
```bash
python test_stock_matcher.py
```

## 📁 文件说明

### 核心文件
- `stock_name_matcher.py` - 核心匹配器
- `local_stock_data.py` - 本地股票数据源
- `stock_data_fetcher.py` - 股票数据获取器（新）
- `requirements.txt` - 依赖列表
- `README.md` - 项目说明

### 安装和启动
- `setup.py` - 一键安装脚本
- `start.py` - 交互式启动界面
- `install_dependencies.py` - 依赖安装脚本
- `check_setup.py` - 环境检查脚本
- `run_stock_matcher.bat` - Windows启动脚本

### 股票数据管理（新功能）
- `update_stock_list.py` - 更新股票列表脚本
- `demo_stock_fetcher.py` - 股票数据获取演示
- `txt_stock_manager.py` - TXT格式股票数据管理工具
- `data/` - 离线股票数据目录
- `all_stocks_*.txt` - TXT格式股票列表文件

### 测试和演示
- `test_stock_matcher.py` - 测试套件
- `quick_start.py` - 快速开始演示
- `example_stocks.csv` - 示例数据文件

### 文档
- `股票名称匹配器使用说明.md` - 详细使用文档

## ⚠️ 注意事项

1. **网络连接**: 需要稳定的网络连接来访问AKShare API
2. **API限制**: 为避免API限制，程序在每次请求间添加了延迟
3. **数据准确性**: 股票价格为实时数据，可能与参考价格有差异
4. **匹配准确性**: 建议提供准确的股票名称和参考价格以提高匹配准确性

## 🔍 故障排查

### 常见错误及解决方案

1. **文件不存在**: 检查输入文件路径是否正确
2. **列名不匹配**: 使用`-n`和`-p`参数指定正确的列名
3. **网络错误**: 检查网络连接，稍后重试
4. **依赖包缺失**: 运行`pip install -r requirements.txt`

### 获取帮助
```bash
python stock_name_matcher.py --help
```

## 📖 详细文档

更多详细信息请查看：`股票名称匹配器使用说明.md`

## 🎯 使用场景

- 从Excel表格中快速识别股票
- 验证股票名称的准确性
- 获取最新的股票价格信息
- 处理各种格式的股票名称（包括简称、别名等）
- 批量处理大量股票数据

## 📊 股票数据管理功能（全新升级）

### 🧠 智能API配置建议（核心特性）
**自动问题检测：**
- 实时监控免费数据源的连接状态和失败次数
- 当连续失败达到阈值（默认3次）时，自动提示用户配置API密钥
- 支持不同类型的失败检测：超时、网络错误、API限制等

**智能提示机制：**
- 在数据源选择区域显示友好的配置建议
- 提供一键跳转到API配置区域的功能
- 建议冷却机制，避免重复提示（默认1小时）
- 配置API密钥后自动停止建议

**使用场景示例：**
```
用户选择AKShare数据源 → 连续3次超时失败 → 系统显示建议：
"AKShare连续失败3次，建议配置API密钥以获得更稳定的服务"
[立即配置] 按钮 → 跳转到API配置区域
```

### 🔑 API密钥配置
系统现在支持多种数据源的API密钥配置，提供更稳定和丰富的数据获取能力：

**支持的数据源：**
- **AKShare**: 免费的中文股票数据接口（通常无需API密钥）
- **Tushare**: 专业的金融数据平台（需要注册获取API密钥）
- **Alpha Vantage**: 国际股票和金融数据（需要API密钥）
- **Quandl**: 金融和经济数据平台（需要API密钥）
- **本地数据源**: 使用本地股票列表文件（推荐，无需网络）

**配置方式：**
1. 在Web界面的"股票数据管理"面板中配置API密钥
2. 系统会自动加密存储所有API密钥，确保安全性
3. 支持连接测试，验证API密钥的有效性

### 📁 股票列表文件管理
**上传股票列表：**
- 支持上传包含股票代码和名称的CSV文件
- 文件格式要求：
  ```csv
  代码,名称
  000001,平安银行
  000002,万科A
  ```
- 系统会自动验证文件格式和内容
- 支持自动备份和版本管理

**文件格式要求：**
- CSV格式，UTF-8编码
- 必须包含：`代码` 和 `名称` 列（或 `code` 和 `name` 列）
- 股票代码支持6位数字格式
- 文件大小限制：16MB

### 🔄 自动更新机制
- 系统会自动监控 `stock_name_list` 目录中的新文件
- 支持手动触发检查更新
- 自动处理文件验证、备份和安装
- 提供详细的处理日志和状态反馈

### 📈 数据源状态监控
- 实时显示各数据源的连接状态
- 显示当前股票数据的统计信息
- 支持一键测试所有数据源连接
- 提供数据源切换和优先级配置



### 🛠️ 配置管理
**系统配置：**
```json
{
  "api_keys": {
    "akshare": "加密存储的API密钥",
    "tushare": "加密存储的API密钥"
  },
  "data_sources": {
    "primary": "local",
    "fallback": ["akshare", "sina", "tencent"],
    "timeout": 30,
    "retry_count": 3
  },
  "system_settings": {
    "max_file_size_mb": 16,
    "auto_backup": true,
    "performance_optimization": true
  }
}
```

**使用配置管理器：**
```python
from config_manager import config_manager

# 设置API密钥
config_manager.set_api_key('tushare', 'your_api_key_here')

# 获取API密钥
api_key = config_manager.get_api_key('tushare')

# 测试连接
result = config_manager.test_api_connection('akshare')
print(f"连接状态: {result['status']}")

# 获取配置摘要
summary = config_manager.get_config_summary()
```

### 📊 离线股票数据功能

### 获取完整股票列表
```bash
# 获取所有A股股票数据并保存为离线文件
python update_stock_list.py

# 只获取基本信息（代码和名称）
python update_stock_list.py --basic-only

# 按市场分别获取数据
python update_stock_list.py --by-market

# 显示详细统计信息
python update_stock_list.py --stats
```

### 使用离线数据
```python
from local_stock_data import LocalStockData

# 使用离线数据（推荐）
stock_data = LocalStockData(use_offline_data=True)

# 搜索股票
result = stock_data.search_by_code('000001')
result = stock_data.search_by_name('平安银行')

# 获取市场股票
sh_stocks = stock_data.get_stocks_by_market('上海')
sz_stocks = stock_data.get_stocks_by_market('深圳')

# 获取数据统计
info = stock_data.get_data_info()
print(f"总股票数: {info['总股票数']}")
```

### 数据更新
- **首次使用**：运行 `python update_stock_list.py` 获取最新股票数据
- **定期更新**：建议每周运行一次更新脚本
- **离线使用**：获取数据后可完全离线使用
- **数据备份**：更新时自动备份现有数据

### 数据来源
- **AKShare API**：获取东方财富网实时股票数据
- **TXT格式文件**：支持自定义的TXT格式股票列表（如 all_stocks_20250616.txt）
- **覆盖范围**：沪深京A股（主板、中小板、创业板、科创板、北交所）
- **数据字段**：股票代码、名称、价格、市值等完整信息
- **更新频率**：支持实时获取最新数据

## 📄 TXT格式股票数据管理（新功能）

### TXT文件格式要求
- **文件命名**：建议使用 `all_stocks_YYYYMMDD.txt` 格式
- **文件编码**：UTF-8编码
- **数据格式**：每行一只股票，格式为 `股票代码,股票名称`
- **注释支持**：以 `#` 开头的行为注释行，会被自动跳过

### TXT文件管理工具
```bash
# 自动分析项目中的TXT文件
python txt_stock_manager.py

# 列出所有可用的TXT格式股票文件
python txt_stock_manager.py --list

# 分析指定TXT文件的内容和统计信息
python txt_stock_manager.py --analyze all_stocks_20250616.txt

# 将TXT文件转换为CSV格式（便于Excel打开）
python txt_stock_manager.py --convert all_stocks_20250616.txt

# 指定转换后的输出文件名
python txt_stock_manager.py --convert all_stocks_20250616.txt -o my_stocks.csv

# 测试TXT文件的股票搜索功能
python txt_stock_manager.py --test all_stocks_20250616.txt
```

### TXT文件自动识别
- **自动加载**：系统会自动识别项目中的TXT格式股票文件
- **优先级**：CSV文件 > TXT文件 > 示例数据
- **文件检测**：自动检测以 `all_stocks_` 开头、`.txt` 结尾的文件
- **数据验证**：自动验证股票代码格式的有效性

### 使用TXT数据进行股票匹配
```python
from local_stock_data import LocalStockData

# 创建股票数据实例（会自动使用TXT文件）
stock_data = LocalStockData(use_offline_data=True)

# 查看数据信息
info = stock_data.get_data_info()
print(f"数据源: {info['数据源']}")
print(f"股票数量: {info['总股票数']:,}")

# 根据代码搜索
result = stock_data.search_by_code('000001')

# 根据名称搜索
result = stock_data.search_by_name('平安银行')

# 获取市场股票
sh_stocks = stock_data.get_stocks_by_market('沪市')
sz_stocks = stock_data.get_stocks_by_market('深市')
```

## 🔄 更新日志

### v2.0.0 (2025-07-11) - 智能化升级 🧠
**🎯 核心新功能：**
- ✨ **智能API配置建议**：自动检测免费数据源连续失败，智能提示配置API密钥
- 🔐 **安全配置管理**：加密存储API密钥，支持多数据源配置
- 📊 **实时状态监控**：显示各数据源的成功率和连接状态
- 🔧 **一键配置跳转**：快速跳转到API配置区域
- ⏰ **智能冷却机制**：避免重复提示，提升用户体验

**🛠️ 技术改进：**
- 新增配置管理器模块 (`config_manager.py`)
- 失败监控和建议系统
- Web界面全面升级
- API端点扩展和安全增强

**📈 用户体验提升：**
- 主动问题检测和解决建议
- 更稳定的数据获取体验
- 智能化的用户引导
- 专业的配置管理界面

### v1.2.0 - TXT格式支持
- 新增TXT格式股票列表支持，包含完整的管理工具

### v1.1.0 - 离线数据功能
- 新增离线股票数据功能，支持获取完整A股列表

### v1.0.0 - 初始版本
- 支持基本的股票名称匹配功能
- 支持多种匹配策略和价格验证
- 完整的测试套件和文档

---

**免责声明**: 本工具仅用于股票名称匹配，不构成投资建议。股票价格数据仅供参考，请以实际交易价格为准。
