# 测试文档

本目录包含股票代码补全系统的所有测试文件。

## 📁 测试文件结构

```
tests/
├── __init__.py                    # 测试模块初始化
├── README.md                      # 测试说明文档（本文件）
├── run_tests.py                   # 测试运行器
├── test_file_format.py            # 文件格式检测测试
├── test_upload_simulation.py      # 文件上传模拟测试
├── test_enhanced_features.py      # 增强功能测试
├── test_upload_request.py         # Web上传请求测试
└── test_web_app.py               # 完整Web应用测试
```

## 🧪 测试说明

### 1. test_file_format.py
**功能**: 测试文件格式检测功能
- 检测Excel和CSV文件格式
- 验证文件头部识别
- 测试文件读取功能

**运行条件**: 需要 `000852.csv` 测试文件

### 2. test_upload_simulation.py
**功能**: 模拟文件上传处理流程
- 测试文件信息获取
- 验证JSON序列化
- 模拟Web应用的文件处理逻辑

**运行条件**: 需要 `000852.csv` 测试文件

### 3. test_enhanced_features.py
**功能**: 测试增强功能
- 被引号包裹的股票代码处理
- 多数据源交叉验证
- 完整工作流程测试

**运行条件**: 无特殊要求，会自动创建测试数据

### 4. test_upload_request.py
**功能**: 测试Web应用文件上传
- HTTP文件上传请求
- JSON响应解析
- 错误处理测试

**运行条件**: 
- Web应用必须运行 (`python app.py`)
- 需要 `000852.csv` 测试文件

### 5. test_web_app.py
**功能**: 完整Web应用测试
- 文件上传测试
- 基础处理测试
- 交叉验证测试
- 文件下载测试
- API端点测试

**运行条件**: Web应用必须运行 (`python app.py`)

## 🚀 运行测试

### 运行所有测试
```bash
cd tests
python run_tests.py
```

### 运行单个测试
```bash
cd tests
python test_enhanced_features.py
```

### 运行Web应用测试
```bash
# 1. 启动Web应用
python app.py

# 2. 在另一个终端运行测试
cd tests
python test_web_app.py
```

## 📋 测试前准备

### 1. 确保依赖已安装
```bash
pip install -r requirements.txt
```

### 2. 准备测试数据
- 确保根目录有 `000852.csv` 文件（用于某些测试）
- 或者测试会自动创建所需的测试数据

### 3. 启动Web应用（如需要）
```bash
python app.py
```

## 🔍 测试结果说明

### 成功标志
- ✅ 表示测试通过
- 📊 显示处理统计信息
- 🎉 表示所有测试完成

### 失败标志
- ❌ 表示测试失败
- ⚠️ 表示警告或跳过
- 💥 表示严重错误

### 常见问题

1. **Web应用连接失败**
   - 确保 `python app.py` 正在运行
   - 检查端口5000是否被占用

2. **测试文件不存在**
   - 某些测试需要 `000852.csv` 文件
   - 检查文件路径是否正确

3. **依赖包缺失**
   - 运行 `pip install -r requirements.txt`
   - 确保所有必要的包都已安装

4. **权限问题**
   - 确保有读写测试目录的权限
   - 检查临时文件创建权限

## 📈 测试覆盖范围

- ✅ 文件格式检测
- ✅ 股票代码标准化
- ✅ 引号包裹代码处理
- ✅ 多数据源验证
- ✅ Web文件上传
- ✅ JSON序列化/反序列化
- ✅ 错误处理
- ✅ API端点测试
- ✅ 完整工作流程

## 🛠️ 添加新测试

1. 在 `tests/` 目录创建新的测试文件
2. 文件名以 `test_` 开头
3. 添加适当的导入路径设置
4. 在 `run_tests.py` 中添加新测试
5. 更新本文档

## 📞 支持

如果测试过程中遇到问题，请检查：
1. 日志文件 (`logs/` 目录)
2. 错误输出信息
3. 系统环境配置
