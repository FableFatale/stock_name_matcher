# Stock Name Matcher

English | [中文](README.md)

An intelligent stock information processing tool that provides both **Command Line** and **Web Interface** usage options:

## 🌐 Web Interface (Recommended)
- **Modern Web Interface**: Drag & drop upload, real-time processing, online preview
- **Zero Configuration**: Auto-detect column names, one-click processing
- **Real-time Feedback**: Processing progress, statistical results, error notifications
- **Mobile Support**: Responsive design, works on both mobile and desktop

## 💻 Command Line Tool
1. **Stock Name Matching**: Match stock codes and detailed information based on stock names
2. **Stock Code Completion**: Complete stock names and detailed information based on stock codes

Uses the free AKShare API to get the latest A-share stock data.

## 🌟 Key Features

- **Dual Mode Support**: Stock name matching + Stock code completion
- **Multiple Matching Strategies**: Exact match, fuzzy match, contains match
- **Price Validation**: Improve matching accuracy with reference prices
- **Auto Mode Detection**: Automatically identify input data type and select processing mode
- **Auto Column Detection**: Automatically identify stock name, code, and price columns
- **Detailed Results**: Provide matching score, alternative options, market data, and other detailed information
- **Code Format Validation**: Validate the validity of stock code formats
- **Offline Stock Data**: Support getting complete stock list from API for offline use
- **TXT Format Support**: Support TXT format stock list files (e.g., all_stocks_20250616.txt)
- **Free API**: Uses AKShare free stock data API
- **Multi-format Support**: Supports Excel (.xlsx, .xls), CSV, and TXT files

## 🚀 Quick Start

### 🌐 Method 1: Web Interface (Recommended)
```bash
# 1. Install dependencies
python install_dependencies.py

# 2. Start web application
python start_web_app.py

# 3. Browser will automatically open http://localhost:5000
```

**Web Interface Features:**
- 🖱️ Drag & drop CSV/Excel files
- 🤖 Auto-detect stock code and price columns
- 📊 Real-time display of processing progress and statistics
- 💾 One-click download results to result folder
- 📱 Support mobile and desktop access

### 💻 Method 2: One-click Installation (Command Line)
```bash
python setup.py
```

### 🎮 Method 3: Interactive Interface
```bash
python start.py
```

### 🔧 Method 4: Step-by-step Installation
```bash
# 1. Environment check
python check_setup.py

# 2. Install dependencies
python install_dependencies.py
# Or: pip install -r requirements.txt

# 3. Quick demo
python quick_start.py

# 4. Use your files
python stock_name_matcher.py your_file.xlsx
```

### 🗂️ Method 5: Get Complete Stock List (New Feature)
```bash
# Get all A-share stock codes and names
python update_stock_list.py

# Get basic information only (code and name)
python update_stock_list.py --basic-only

# Get by market separately
python update_stock_list.py --by-market

# Show statistics
python update_stock_list.py --stats

# Demo complete functionality
python demo_stock_fetcher.py
```

### 📄 Method 6: Use TXT Format Stock List (New Feature)
```bash
# Manage TXT format stock files
python txt_stock_manager.py

# List available TXT files
python txt_stock_manager.py --list

# Analyze TXT file content
python txt_stock_manager.py --analyze all_stocks_20250616.txt

# Convert TXT file to CSV format
python txt_stock_manager.py --convert all_stocks_20250616.txt

# Test TXT file search functionality
python txt_stock_manager.py --test all_stocks_20250616.txt
```

### Windows Users
Double-click `run_stock_matcher.bat` to get a graphical menu interface.

## 📋 Usage

### Basic Usage

#### Auto Mode (Recommended)
```bash
# Automatically detect input data type and select processing mode
python stock_name_matcher.py input_file.xlsx
```

#### Stock Name Matching Mode
```bash
# Match codes based on stock names
python stock_name_matcher.py stock_names.xlsx --mode name

# Specify column names
python stock_name_matcher.py stock_names.xlsx -n "Stock Name" -p "Price"
```

#### Stock Code Completion Mode
```bash
# Complete names based on stock codes
python stock_name_matcher.py stock_codes.csv --mode code

# Specify column names
python stock_name_matcher.py stock_codes.csv -c "Code" -p "Price"
```

#### Complete Parameter Example
```bash
python stock_name_matcher.py input_file.xlsx \
    --output results.csv \
    --name-column "Stock Name" \
    --code-column "Stock Code" \
    --price-column "Reference Price" \
    --mode auto
```

## 📊 Input File Formats

### Stock Name Matching Mode

#### Excel File Example
| Stock Name | Reference Price |
|------------|----------------|
| Ping An Bank | 10.45 |
| China Merchants Bank | 35.20 |
| Ping An Insurance | 45.80 |

#### CSV File Example
```csv
Stock Name,Reference Price
Ping An Bank,10.45
China Merchants Bank,35.20
Ping An Insurance,45.80
```

#### TXT Format Stock List Example
```txt
# All A-share Stock List (Updated: 2025-06-16)
# Format: Stock Code,Stock Name
000001,Ping An Bank
000002,Vanke A
600036,China Merchants Bank
600519,Kweichow Moutai
300059,East Money
688001,Hua Xing Yuan Chuang
```

### Stock Code Completion Mode

#### Excel File Example
| Stock Code | Reference Price |
|------------|----------------|
| 000001 | 10.45 |
| 600036 | 35.20 |
| 601318 | 45.80 |

#### CSV File Example
```csv
Stock Code,Reference Price
000001,10.45
600036,35.20
601318,45.80
```

## 📈 Output Results

### Stock Name Matching Mode Output
Generated CSV file contains the following columns:
- **Original Name**: Input stock name
- **Reference Price**: Input reference price
- **Matched Stock Code**: Matched stock code
- **Matched Stock Name**: Matched stock name
- **Current Price**: Current market price
- **Match Type**: Matching method (exact/fuzzy/contains match)
- **Match Score**: Matching similarity (0-100)
- **Price Difference**: Difference from reference price
- **Alternative 1_Code/Name**: Second best match
- **Alternative 2_Code/Name**: Third best match

### Stock Code Completion Mode Output
Generated CSV file contains the following columns:
- **Original Code**: Input stock code
- **Reference Price**: Input reference price
- **Match Status**: Match status (success/invalid format/not found)
- **Stock Code**: Validated stock code
- **Stock Name**: Stock name
- **Current Price**: Current market price
- **Price Difference**: Difference from reference price
- **Match Type**: Matching method (exact code match/format validation failed/code not exist)
- **Change Percent**: Daily change percentage
- **Change Amount**: Daily change amount
- **Volume**: Trading volume
- **Turnover**: Trading turnover
- **PE Ratio**: Price-to-earnings ratio
- **PB Ratio**: Price-to-book ratio

## 🔧 Processing Strategies

### Stock Name Matching Strategies

#### 1. Exact Match
Complete match of stock name, 100% matching score

#### 2. Fuzzy Match
Uses fuzzy string matching algorithm to handle spelling differences and abbreviations

#### 3. Contains Match
Check if stock name contains input keywords

#### 4. Price Validation
If reference price is provided, prioritize stocks with similar prices

### Stock Code Completion Strategies

#### 1. Code Format Validation
Validate if stock code conforms to A-share code format:
- Shanghai: 600xxx, 601xxx, 603xxx, 605xxx, 688xxx
- Shenzhen: 000xxx, 001xxx, 002xxx, 003xxx
- ChiNext: 300xxx
- STAR Market: 688xxx

#### 2. Exact Code Match
Find exact matching stock codes in the stock database

#### 3. Price Validation
Combine reference price to validate matching result accuracy

## 🧪 Testing

Run complete test suite:
```bash
python tests/run_tests.py
```

## 📁 File Description

### Core Files
- `stock_name_matcher.py` - Core matcher
- `local_stock_data.py` - Local stock data source
- `stock_data_fetcher.py` - Stock data fetcher (new)
- `requirements.txt` - Dependency list
- `README.md` - Project documentation (Chinese)
- `README_EN.md` - Project documentation (English)

### Installation and Startup
- `setup.py` - One-click installation script
- `start.py` - Interactive startup interface
- `install_dependencies.py` - Dependency installation script
- `check_setup.py` - Environment check script
- `run_stock_matcher.bat` - Windows startup script

### Stock Data Management (New Feature)
- `update_stock_list.py` - Update stock list script
- `txt_stock_manager.py` - TXT format stock data management tool
- `data/` - Offline stock data directory
- `stock_name_list/` - Stock name list directory

### Testing and Demo
- `tests/` - Test suite directory
- `quick_start.py` - Quick start demo

## ⚠️ Notes

1. **Network Connection**: Requires stable network connection to access AKShare API
2. **API Limitations**: Program adds delays between requests to avoid API limitations
3. **Data Accuracy**: Stock prices are real-time data, may differ from reference prices
4. **Matching Accuracy**: Recommend providing accurate stock names and reference prices for better matching

## 🔍 Troubleshooting

### Common Errors and Solutions

1. **File Not Found**: Check if input file path is correct
2. **Column Name Mismatch**: Use `-n` and `-p` parameters to specify correct column names
3. **Network Error**: Check network connection, retry later
4. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Get Help
```bash
python stock_name_matcher.py --help
```

## 📖 Detailed Documentation

For more detailed information, please see: `股票名称匹配器使用说明.md` (Chinese)

## 🎯 Use Cases

- Quickly identify stocks from Excel spreadsheets
- Verify accuracy of stock names
- Get latest stock price information
- Process various formats of stock names (including abbreviations, aliases, etc.)
- Batch process large amounts of stock data

## 📊 Offline Stock Data Feature (New)

### Get Complete Stock List
```bash
# Get all A-share stock data and save as offline file
python update_stock_list.py

# Get basic information only (code and name)
python update_stock_list.py --basic-only

# Get data by market separately
python update_stock_list.py --by-market

# Show detailed statistics
python update_stock_list.py --stats
```

### Use Offline Data
```python
from local_stock_data import LocalStockData

# Use offline data (recommended)
stock_data = LocalStockData(use_offline_data=True)

# Search stocks
result = stock_data.search_by_code('000001')
result = stock_data.search_by_name('Ping An Bank')

# Get market stocks
sh_stocks = stock_data.get_stocks_by_market('Shanghai')
sz_stocks = stock_data.get_stocks_by_market('Shenzhen')

# Get data statistics
info = stock_data.get_data_info()
print(f"Total stocks: {info['Total Stocks']}")
```

### Data Updates
- **First Use**: Run `python update_stock_list.py` to get latest stock data
- **Regular Updates**: Recommend running update script weekly
- **Offline Use**: Can be used completely offline after getting data
- **Data Backup**: Automatically backup existing data when updating

### Data Sources
- **AKShare API**: Get real-time stock data from East Money
- **TXT Format Files**: Support custom TXT format stock lists (e.g., all_stocks_20250616.txt)
- **Coverage**: Shanghai, Shenzhen, Beijing A-shares (Main Board, SME Board, ChiNext, STAR Market, NEEQ)
- **Data Fields**: Stock code, name, price, market cap, and other complete information
- **Update Frequency**: Support real-time latest data retrieval

## 🔄 Update Log

- v1.2.0 - Added TXT format stock list support with complete management tools
- v1.1.0 - Added offline stock data feature, support getting complete A-share list
- v1.0.0 - Initial version, support basic stock name matching functionality
- Support multiple matching strategies and price validation
- Complete test suite and documentation

---

**Disclaimer**: This tool is for stock name matching only and does not constitute investment advice. Stock price data is for reference only, please refer to actual trading prices.
