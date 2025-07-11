// 股票代码名称补全工具 - 前端JavaScript

let currentFile = null;
let resultFileName = null;

// DOM元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileDetails = document.getElementById('fileDetails');
const columnConfig = document.getElementById('columnConfig');
const codeColumn = document.getElementById('codeColumn');
const priceColumn = document.getElementById('priceColumn');
const apiSource = document.getElementById('apiSource');
const enableCrossValidation = document.getElementById('enableCrossValidation');
const enableOptimization = document.getElementById('enableOptimization');
const processBtn = document.getElementById('processBtn');

// 数据源建议相关元素
const dataSourceSuggestion = document.getElementById('dataSourceSuggestion');
const suggestionMessage = document.getElementById('suggestionMessage');
const goToApiConfigBtn = document.getElementById('goToApiConfigBtn');

// 股票数据管理相关元素
const stockDataFile = document.getElementById('stockDataFile');
const uploadStockDataBtn = document.getElementById('uploadStockDataBtn');
const autoUpdateBtn = document.getElementById('autoUpdateBtn');

// API Key配置相关元素
const akshareApiKey = document.getElementById('akshareApiKey');
const tushareApiKey = document.getElementById('tushareApiKey');
const alphaVantageApiKey = document.getElementById('alphaVantageApiKey');
const quandlApiKey = document.getElementById('quandlApiKey');
const saveApiKeysBtn = document.getElementById('saveApiKeysBtn');
const testAllConnectionsBtn = document.getElementById('testAllConnectionsBtn');
const progressContainer = document.getElementById('progressContainer');
const resultSection = document.getElementById('resultSection');
const downloadBtn = document.getElementById('downloadBtn');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkApiStatus();
});

function setupEventListeners() {
    // 文件拖拽
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', (e) => {
        // 如果点击的是按钮，按钮会处理，这里不需要处理
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            return;
        }
        fileInput.click();
    });

    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);
    
    // 处理按钮
    processBtn.addEventListener('click', processFile);
    
    // 下载按钮
    downloadBtn.addEventListener('click', downloadResult);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // 检查文件类型
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const allowedExtensions = ['.csv', '.xlsx', '.xls'];
    
    const isValidType = allowedTypes.includes(file.type) || 
                       allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!isValidType) {
        showAlert('请上传CSV或Excel文件', 'danger');
        return;
    }
    
    // 检查文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('文件大小不能超过16MB', 'danger');
        return;
    }
    
    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showProgress('正在上传文件...');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        
        if (data.success) {
            currentFile = data.filename;
            displayFileInfo(data.file_info);
            setupColumnOptions(data.file_info.columns);
            showAlert('文件上传成功！', 'success');
        } else {
            showAlert(data.error || '文件上传失败', 'danger');
        }
    })
    .catch(error => {
        hideProgress();
        console.error('上传错误:', error);
        showAlert('文件上传失败，请重试', 'danger');
    });
}

function displayFileInfo(info) {
    fileDetails.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <strong>列数:</strong> ${info.columns.length}<br>
                <strong>行数:</strong> ${info.rows}
            </div>
            <div class="col-md-6">
                <strong>列名:</strong> ${info.columns.join(', ')}
            </div>
        </div>
        <div class="mt-2">
            <strong>数据预览:</strong>
            <div class="table-responsive mt-2">
                <table class="table table-sm table-bordered">
                    <thead>
                        <tr>
                            ${info.columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${info.preview.map(row => 
                            `<tr>${info.columns.map(col => `<td>${row[col] || ''}</td>`).join('')}</tr>`
                        ).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    fileInfo.classList.remove('d-none');
    columnConfig.classList.remove('d-none');
}

function setupColumnOptions(columns) {
    // 清空现有选项
    codeColumn.innerHTML = '<option value="">自动检测</option>';
    priceColumn.innerHTML = '<option value="">自动检测</option>';
    
    // 添加列选项
    columns.forEach(col => {
        codeColumn.innerHTML += `<option value="${col}">${col}</option>`;
        priceColumn.innerHTML += `<option value="${col}">${col}</option>`;
    });
    
    // 自动选择可能的列
    autoSelectColumns(columns);
}

function autoSelectColumns(columns) {
    // 自动检测股票代码列
    const codeKeywords = ['代码', '股票代码', '证券代码', 'code', 'symbol'];
    for (let col of columns) {
        if (codeKeywords.some(keyword => col.toLowerCase().includes(keyword.toLowerCase()))) {
            codeColumn.value = col;
            break;
        }
    }
    
    // 自动检测价格列
    const priceKeywords = ['价格', '股价', '现价', '最新价', '收盘价', 'price', 'close'];
    for (let col of columns) {
        if (priceKeywords.some(keyword => col.toLowerCase().includes(keyword.toLowerCase()))) {
            priceColumn.value = col;
            break;
        }
    }
}

function processFile() {
    if (!currentFile) {
        showAlert('请先上传文件', 'warning');
        return;
    }
    
    const requestData = {
        filename: currentFile,
        code_column: codeColumn.value || null,
        price_column: priceColumn.value || null,
        api_source: apiSource.value,
        enable_cross_validation: enableCrossValidation.checked,
        use_optimization: enableOptimization.checked
    };
    
    // 根据选项显示不同的进度信息
    let progressMessage = '正在处理股票代码名称补全';
    if (enableOptimization.checked) {
        progressMessage += '（🚀 性能优化模式）';
    }
    if (enableCrossValidation.checked) {
        progressMessage += '并进行多数据源验证';
    }
    progressMessage += '...';
    showProgress(progressMessage);
    processBtn.disabled = true;

    // 显示或隐藏验证列
    const validationColumns = document.querySelectorAll('.validation-column');
    validationColumns.forEach(col => {
        col.style.display = enableCrossValidation.checked ? 'table-cell' : 'none';
    });
    
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        processBtn.disabled = false;
        
        if (data.success) {
            resultFileName = data.result_file;
            displayResults(data.statistics, data.preview);
            showAlert('处理完成！', 'success');
        } else {
            showAlert(data.error || '处理失败', 'danger');

            // 如果是数据源相关的错误，记录失败并检查建议
            const errorMessage = data.error || '';
            const selectedSource = apiSource.value;

            if (selectedSource && selectedSource !== 'local') {
                if (errorMessage.includes('超时') || errorMessage.includes('timeout') ||
                    errorMessage.includes('连接') || errorMessage.includes('网络')) {
                    recordDataSourceFailure(selectedSource, 'timeout');
                } else if (errorMessage.includes('API') || errorMessage.includes('密钥')) {
                    recordDataSourceFailure(selectedSource, 'api_error');
                } else {
                    recordDataSourceFailure(selectedSource, 'unknown');
                }
            }
        }
    })
    .catch(error => {
        hideProgress();
        processBtn.disabled = false;
        console.error('处理错误:', error);
        showAlert('处理失败，请重试', 'danger');
    });
}

function displayResults(stats, preview) {
    // 更新统计信息
    document.getElementById('totalCount').textContent = stats.total;
    document.getElementById('successCount').textContent = stats.success;
    document.getElementById('successRate').textContent = stats.success_rate + '%';
    
    // 更新结果表格
    const tbody = document.querySelector('#resultTable tbody');
    tbody.innerHTML = '';
    
    preview.forEach(row => {
        const tr = document.createElement('tr');

        // 基础列
        let rowHtml = `
            <td>${row['原始代码'] || ''}</td>
            <td>${row['标准化代码'] || ''}</td>
            <td>${row['股票名称'] || ''}</td>
            <td>${row['当前价格'] || ''}</td>
            <td>${row['参考价格'] || ''}</td>
            <td>${row['价格差异'] || ''}</td>
            <td>
                <span class="badge ${getStatusBadgeClass(row['匹配状态'])}">
                    ${row['匹配状态'] || ''}
                </span>
            </td>
        `;

        // 验证列（如果启用了交叉验证）
        if (enableCrossValidation.checked) {
            rowHtml += `
                <td class="validation-column">${row['验证置信度'] || ''}</td>
                <td class="validation-column">${row['名称一致性'] || ''}</td>
            `;
        }

        tr.innerHTML = rowHtml;
        tbody.appendChild(tr);
    });
    
    resultSection.classList.remove('d-none');
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case '匹配成功':
            return 'bg-success';
        case '代码格式无效':
            return 'bg-warning';
        case '未找到匹配':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

function downloadResult() {
    if (!resultFileName) {
        showAlert('没有可下载的结果文件', 'warning');
        return;
    }

    // 显示下载状态
    showDownloadStatus(`正在准备下载: ${resultFileName}`, 'downloading');

    // 尝试多种下载方法
    downloadWithMultipleMethods();
}

function downloadWithMultipleMethods() {
    console.log('开始下载文件:', resultFileName);

    // 方法1: 使用fetch + blob (最兼容的方法)
    downloadWithFetch()
        .then(success => {
            if (!success) {
                console.log('Fetch方法失败，尝试直接链接方法');
                return downloadWithDirectLink();
            }
            return true;
        })
        .then(success => {
            if (!success) {
                console.log('直接链接方法失败，尝试新窗口方法');
                downloadWithNewWindow();
            }
        })
        .catch(error => {
            console.error('所有下载方法都失败了:', error);
            showDownloadStatus('下载失败，请稍后重试', 'error');
            showAlert('下载失败，请稍后重试', 'danger');
        });
}

function downloadWithFetch() {
    return new Promise((resolve) => {
        fetch(`/download/${resultFileName}`)
            .then(response => {
                console.log('Fetch响应状态:', response.status);
                console.log('Fetch响应头:', Object.fromEntries(response.headers.entries()));

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.blob();
            })
            .then(blob => {
                console.log('Blob创建成功，大小:', blob.size);

                // 创建下载链接
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = resultFileName;
                link.style.display = 'none';

                // 添加到DOM并触发点击
                document.body.appendChild(link);

                // 使用setTimeout确保链接被正确添加到DOM
                setTimeout(() => {
                    link.click();
                    console.log('Fetch下载链接已点击');

                    // 清理
                    setTimeout(() => {
                        if (link.parentNode) {
                            document.body.removeChild(link);
                        }
                        window.URL.revokeObjectURL(url);
                    }, 1000);
                }, 10);

                showDownloadStatus(`文件下载完成: ${resultFileName}`, 'success');
                showAlert(`文件下载完成: ${resultFileName}`, 'success');
                resolve(true);
            })
            .catch(error => {
                console.error('Fetch下载失败:', error);
                resolve(false);
            });
    });
}

function downloadWithDirectLink() {
    return new Promise((resolve) => {
        try {
            console.log('尝试直接链接下载方法');

            const link = document.createElement('a');
            link.href = `/download/${resultFileName}`;
            link.download = resultFileName;
            link.target = '_blank'; // 在新标签页打开
            link.style.display = 'none';

            // 添加到DOM
            document.body.appendChild(link);

            // 触发点击
            setTimeout(() => {
                link.click();
                console.log('直接链接已点击');

                // 清理
                setTimeout(() => {
                    if (link.parentNode) {
                        document.body.removeChild(link);
                    }
                }, 1000);
            }, 10);

            showDownloadStatus(`开始下载: ${resultFileName}`, 'downloading');
            showAlert(`开始下载: ${resultFileName}`, 'success');

            // 假设成功（无法确定直接链接是否真的成功）
            setTimeout(() => resolve(true), 2000);

        } catch (error) {
            console.error('直接链接下载失败:', error);
            resolve(false);
        }
    });
}

function downloadWithNewWindow() {
    try {
        console.log('尝试新窗口下载方法');

        // 在新窗口中打开下载链接
        const newWindow = window.open(`/download/${resultFileName}`, '_blank');

        if (newWindow) {
            showDownloadStatus(`在新窗口中下载: ${resultFileName}`, 'success');
            showAlert(`在新窗口中下载: ${resultFileName}`, 'success');
        } else {
            throw new Error('无法打开新窗口，可能被浏览器阻止');
        }

    } catch (error) {
        console.error('新窗口下载失败:', error);
        showDownloadStatus('下载失败，请检查浏览器弹窗设置', 'error');
        showAlert('下载失败，请检查浏览器弹窗设置', 'danger');
    }
}



function showDownloadStatus(message, type = 'info') {
    const statusDiv = document.getElementById('downloadStatus');
    const statusText = document.getElementById('downloadStatusText');

    if (statusDiv && statusText) {
        statusText.textContent = message;
        statusDiv.style.display = 'block';

        // 根据类型设置不同的样式
        statusDiv.className = 'mt-2 small';
        switch (type) {
            case 'downloading':
                statusDiv.className += ' text-primary';
                break;
            case 'success':
                statusDiv.className += ' text-success';
                break;
            case 'error':
                statusDiv.className += ' text-danger';
                break;
            default:
                statusDiv.className += ' text-muted';
        }

        // 如果是成功或错误状态，3秒后自动隐藏
        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    }
}

function showProgress(message) {
    progressContainer.querySelector('span').textContent = message;
    progressContainer.classList.remove('d-none');
}

function hideProgress() {
    progressContainer.classList.add('d-none');
}

function showAlert(message, type) {
    // 移除现有的alert
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 创建新的alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 插入到页面顶部
    document.querySelector('.container').insertBefore(alert, document.querySelector('.container').firstChild);
    
    // 自动消失
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function checkApiStatus() {
    fetch('/api/status')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            console.log(`API状态正常，股票数据: ${data.stock_count} 只`);
        } else {
            console.warn('API状态异常:', data.error);
        }
    })
    .catch(error => {
        console.error('API状态检查失败:', error);
    });
}

// 股票数据管理功能
function loadStockDataStatus() {
    fetch('/api/stock_data_status')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                updateStockDataStatus(data);
            } else {
                showStockDataMessage('获取股票数据状态失败: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('加载股票数据状态失败:', error);
            showStockDataMessage('加载股票数据状态失败', 'error');
        });
}

function updateStockDataStatus(data) {
    const statusDiv = document.getElementById('stockDataStatus');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>当前股票数据:</strong><br>
                    <span class="text-primary">${data.current_data.total_stocks}</span> 只股票<br>
                    <small class="text-muted">数据源: ${data.current_data.data_source}</small>
                </div>
                <div class="col-md-6">
                    <strong>文件统计:</strong><br>
                    数据文件: ${data.files.data_files} 个<br>
                    备份文件: ${data.files.backup_files} 个<br>
                    待处理: ${data.files.watch_files} 个
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-folder"></i> 监控目录: <code>${data.watch_directory}</code>
                </small>
            </div>
        `;
    }
}

function uploadStockData() {
    const fileInput = document.getElementById('stockDataFile');
    const file = fileInput.files[0];

    if (!file) {
        showStockDataMessage('请选择要上传的CSV文件', 'warning');
        return;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
        showStockDataMessage('只支持CSV格式的文件', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // 显示上传进度
    const uploadBtn = document.getElementById('uploadStockDataBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
    uploadBtn.disabled = true;

    showStockDataMessage('正在上传和处理股票数据文件...', 'info');

    fetch('/api/upload_stock_data', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStockDataMessage(
                `股票数据上传成功！<br>
                文件: ${data.filename}<br>
                股票数量: ${data.file_info.total_rows} 只<br>
                文件大小: ${data.file_info.file_size_mb} MB`,
                'success'
            );

            // 重新加载状态
            setTimeout(() => {
                loadStockDataStatus();
            }, 1000);

            // 清空文件选择
            fileInput.value = '';
            fileInput.nextElementSibling.textContent = '选择CSV文件...';

        } else {
            showStockDataMessage('上传失败: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('上传失败:', error);
        showStockDataMessage('上传失败: ' + error.message, 'error');
    })
    .finally(() => {
        // 恢复按钮状态
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    });
}

function autoUpdateStockData() {
    const updateBtn = document.getElementById('autoUpdateBtn');
    const originalText = updateBtn.innerHTML;
    updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 检查中...';
    updateBtn.disabled = true;

    showStockDataMessage('正在检查新的股票数据文件...', 'info');

    fetch('/api/auto_update_stock_data', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.new_files.length > 0) {
                showStockDataMessage(
                    `发现并处理了新文件:<br>${data.new_files.join('<br>')}`,
                    'success'
                );
                // 重新加载状态
                setTimeout(() => {
                    loadStockDataStatus();
                }, 1000);
            } else {
                showStockDataMessage('没有发现新的股票数据文件', 'info');
            }
        } else {
            showStockDataMessage('自动更新失败: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('自动更新失败:', error);
        showStockDataMessage('自动更新失败: ' + error.message, 'error');
    })
    .finally(() => {
        // 恢复按钮状态
        updateBtn.innerHTML = originalText;
        updateBtn.disabled = false;
    });
}

function showStockDataMessage(message, type) {
    const messageDiv = document.getElementById('stockDataMessage');
    if (messageDiv) {
        messageDiv.style.display = 'block';
        messageDiv.className = `alert alert-${type === 'error' ? 'danger' : type}`;
        messageDiv.innerHTML = message;

        // 自动隐藏成功和信息消息
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }
    }
}

// API Key配置管理功能
function loadApiKeysStatus() {
    fetch('/api/config/api_keys')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                updateApiKeysStatus(data.api_keys);
            } else {
                showStockDataMessage('获取API密钥状态失败: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('加载API密钥状态失败:', error);
            showStockDataMessage('加载API密钥状态失败', 'error');
        });
}

function updateApiKeysStatus(apiKeysStatus) {
    // 更新输入框的占位符，显示是否已配置
    Object.keys(apiKeysStatus).forEach(source => {
        const input = document.getElementById(source + 'ApiKey');
        if (input) {
            const status = apiKeysStatus[source];
            if (status.configured) {
                input.placeholder = `已配置 (${status.length} 字符)`;
                input.classList.add('is-valid');
            } else {
                input.placeholder = `输入${source}API密钥`;
                input.classList.remove('is-valid');
            }
        }
    });
}

function saveApiKeys() {
    const apiKeys = {
        akshare: akshareApiKey ? akshareApiKey.value : '',
        tushare: tushareApiKey ? tushareApiKey.value : '',
        alpha_vantage: alphaVantageApiKey ? alphaVantageApiKey.value : '',
        quandl: quandlApiKey ? quandlApiKey.value : ''
    };

    // 只保存非空的API密钥
    const nonEmptyKeys = {};
    Object.keys(apiKeys).forEach(key => {
        if (apiKeys[key].trim()) {
            nonEmptyKeys[key] = apiKeys[key].trim();
        }
    });

    if (Object.keys(nonEmptyKeys).length === 0) {
        showStockDataMessage('请至少输入一个API密钥', 'warning');
        return;
    }

    // 显示保存进度
    const saveBtn = document.getElementById('saveApiKeysBtn');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';
    saveBtn.disabled = true;

    showStockDataMessage('正在保存API密钥...', 'info');

    fetch('/api/config/api_keys', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            api_keys: nonEmptyKeys
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStockDataMessage(
                `API密钥保存成功！${data.message}`,
                'success'
            );

            // 重新加载状态
            setTimeout(() => {
                loadApiKeysStatus();
            }, 1000);

            // 清空输入框
            Object.keys(apiKeys).forEach(key => {
                const input = document.getElementById(key + 'ApiKey');
                if (input) {
                    input.value = '';
                }
            });

        } else {
            showStockDataMessage('保存失败: ' + (data.error || '未知错误'), 'error');
        }
    })
    .catch(error => {
        console.error('保存API密钥失败:', error);
        showStockDataMessage('保存失败: ' + error.message, 'error');
    })
    .finally(() => {
        // 恢复按钮状态
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    });
}

function testApiConnection(source) {
    return fetch(`/api/config/test_connection/${source}`)
        .then(response => response.json())
        .then(data => {
            return {
                source: source,
                status: data.status,
                message: data.message,
                has_api_key: data.has_api_key
            };
        })
        .catch(error => {
            return {
                source: source,
                status: 'error',
                message: `连接测试失败: ${error.message}`,
                has_api_key: false
            };
        });
}

function testAllConnections() {
    const testBtn = document.getElementById('testAllConnectionsBtn');
    const originalText = testBtn.innerHTML;
    testBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 测试中...';
    testBtn.disabled = true;

    showStockDataMessage('正在测试所有数据源连接...', 'info');

    const sources = ['local', 'akshare', 'sina', 'tencent', 'eastmoney'];
    const testPromises = sources.map(source => testApiConnection(source));

    Promise.all(testPromises)
        .then(results => {
            updateConnectionStatus(results);
            showStockDataMessage('连接测试完成', 'success');
        })
        .catch(error => {
            console.error('测试连接失败:', error);
            showStockDataMessage('测试连接失败: ' + error.message, 'error');
        })
        .finally(() => {
            // 恢复按钮状态
            testBtn.innerHTML = originalText;
            testBtn.disabled = false;
        });
}

function updateConnectionStatus(results) {
    const statusList = document.getElementById('connectionStatusList');
    if (!statusList) return;

    let html = '';
    results.forEach(result => {
        const statusClass = result.status === 'success' ? 'text-success' :
                           result.status === 'error' ? 'text-danger' : 'text-warning';
        const icon = result.status === 'success' ? 'bi-check-circle' :
                    result.status === 'error' ? 'bi-x-circle' : 'bi-question-circle';

        html += `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span>
                    <i class="bi ${icon} ${statusClass}"></i>
                    ${result.source}
                </span>
                <span class="${statusClass} small">${result.message}</span>
            </div>
        `;
    });

    statusList.innerHTML = html;
}

// 数据源监控和建议功能
function checkDataSourceSuggestion(source) {
    if (!source || source === 'local') {
        hideDataSourceSuggestion();
        return;
    }

    fetch(`/api/data_source_suggestion/${source}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok' && data.suggestion) {
                const suggestion = data.suggestion;
                if (suggestion.should_suggest) {
                    showDataSourceSuggestion(source, suggestion);
                } else {
                    hideDataSourceSuggestion();
                }
            }
        })
        .catch(error => {
            console.error('检查数据源建议失败:', error);
        });
}

function showDataSourceSuggestion(source, suggestion) {
    if (!dataSourceSuggestion || !suggestionMessage) return;

    const message = `${source} ${suggestion.suggestion_reason}`;
    suggestionMessage.textContent = message;
    dataSourceSuggestion.style.display = 'block';

    // 滚动到建议区域
    setTimeout(() => {
        dataSourceSuggestion.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function hideDataSourceSuggestion() {
    if (dataSourceSuggestion) {
        dataSourceSuggestion.style.display = 'none';
    }
}

function recordDataSourceFailure(source, errorType = 'timeout') {
    fetch(`/api/record_failure/${source}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            error_type: errorType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.suggestion && data.suggestion.should_suggest) {
            showDataSourceSuggestion(source, data.suggestion);
        }
    })
    .catch(error => {
        console.error('记录数据源失败时出错:', error);
    });
}

function loadDataSourceStats() {
    fetch('/api/data_source_stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                updateDataSourceStatsDisplay(data.stats);
            }
        })
        .catch(error => {
            console.error('加载数据源统计失败:', error);
        });
}

function updateDataSourceStatsDisplay(stats) {
    // 更新连接状态显示，包含统计信息
    const statusList = document.getElementById('connectionStatusList');
    if (!statusList) return;

    let html = '';
    Object.keys(stats).forEach(source => {
        const stat = stats[source];
        const statusClass = stat.success_rate >= 80 ? 'text-success' :
                           stat.success_rate >= 50 ? 'text-warning' : 'text-danger';
        const icon = stat.success_rate >= 80 ? 'bi-check-circle' :
                    stat.success_rate >= 50 ? 'bi-exclamation-triangle' : 'bi-x-circle';

        const suggestionBadge = stat.should_suggest_api ?
            '<span class="badge bg-warning ms-1">建议配置API</span>' : '';

        html += `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span>
                    <i class="bi ${icon} ${statusClass}"></i>
                    ${source}
                    ${suggestionBadge}
                </span>
                <span class="${statusClass} small">
                    成功率: ${stat.success_rate}%
                    ${stat.failure_count > 0 ? `(失败${stat.failure_count}次)` : ''}
                </span>
            </div>
        `;
    });

    statusList.innerHTML = html;
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载股票数据状态
    loadStockDataStatus();

    // 加载API密钥状态
    loadApiKeysStatus();

    // 加载数据源统计
    loadDataSourceStats();

    // 股票数据文件选择事件
    if (stockDataFile) {
        stockDataFile.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : '';
            // 更新文件选择提示（Bootstrap 5不需要label更新）
        });
    }

    // 上传股票数据按钮事件
    if (uploadStockDataBtn) {
        uploadStockDataBtn.addEventListener('click', uploadStockData);
    }

    // 自动更新按钮事件
    if (autoUpdateBtn) {
        autoUpdateBtn.addEventListener('click', autoUpdateStockData);
    }

    // API Key配置相关事件
    if (saveApiKeysBtn) {
        saveApiKeysBtn.addEventListener('click', saveApiKeys);
    }

    if (testAllConnectionsBtn) {
        testAllConnectionsBtn.addEventListener('click', testAllConnections);
    }

    // 数据源选择变化事件
    if (apiSource) {
        apiSource.addEventListener('change', function() {
            const selectedSource = this.value;
            checkDataSourceSuggestion(selectedSource);
        });

        // 初始检查
        checkDataSourceSuggestion(apiSource.value);
    }

    // 跳转到API配置按钮
    if (goToApiConfigBtn) {
        goToApiConfigBtn.addEventListener('click', function() {
            // 滚动到API配置区域
            const apiConfigSection = document.querySelector('#stockDataPanel');
            if (apiConfigSection) {
                apiConfigSection.scrollIntoView({ behavior: 'smooth' });

                // 展开面板（如果是折叠的）
                const collapseElement = document.getElementById('stockDataPanel');
                if (collapseElement && !collapseElement.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(collapseElement, {
                        show: true
                    });
                }

                // 高亮API配置区域
                const apiKeySection = document.querySelector('h6:contains("API密钥配置")');
                if (apiKeySection) {
                    apiKeySection.style.backgroundColor = '#fff3cd';
                    setTimeout(() => {
                        apiKeySection.style.backgroundColor = '';
                    }, 3000);
                }
            }

            // 隐藏建议提示
            hideDataSourceSuggestion();
        });
    }

    // 单个API测试按钮事件
    const testButtons = [
        { id: 'testAkshareBtn', source: 'akshare' },
        { id: 'testTushareBtn', source: 'tushare' },
        { id: 'testAlphaVantageBtn', source: 'alpha_vantage' },
        { id: 'testQuandlBtn', source: 'quandl' }
    ];

    testButtons.forEach(({ id, source }) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                btn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
                btn.disabled = true;

                testApiConnection(source)
                    .then(result => {
                        const statusClass = result.status === 'success' ? 'text-success' : 'text-danger';
                        showStockDataMessage(`${source}: ${result.message}`, result.status === 'success' ? 'success' : 'error');
                    })
                    .finally(() => {
                        btn.innerHTML = '<i class="bi bi-wifi"></i> 测试';
                        btn.disabled = false;
                    });
            });
        }
    });
});
