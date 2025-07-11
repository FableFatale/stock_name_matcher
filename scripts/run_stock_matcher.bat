@echo off
chcp 65001 >nul
echo ========================================
echo 股票名称匹配器 - Windows 启动脚本
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 安装依赖
echo 2. 快速开始演示
echo 3. 运行测试
echo 4. 匹配股票名称 (需要输入文件路径)
echo 5. 查看帮助
echo 6. 退出
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto quickstart
if "%choice%"=="3" goto test
if "%choice%"=="4" goto match
if "%choice%"=="5" goto help
if "%choice%"=="6" goto exit
echo 无效选择，请重新输入
goto menu

:install
echo.
echo 正在安装依赖...
python install_dependencies.py
pause
goto menu

:quickstart
echo.
echo 正在运行快速开始演示...
python quick_start.py
pause
goto menu

:test
echo.
echo 正在运行测试...
python test_stock_matcher.py
pause
goto menu

:match
echo.
set /p filepath=请输入Excel/CSV文件路径: 
if "%filepath%"=="" (
    echo 文件路径不能为空
    pause
    goto menu
)
echo 正在处理文件: %filepath%
python stock_name_matcher.py "%filepath%"
pause
goto menu

:help
echo.
echo 使用说明:
echo.
echo 1. 首次使用请先选择"安装依赖"
echo 2. 可以使用"快速开始演示"体验功能
echo 3. 准备好Excel或CSV文件后选择"匹配股票名称"
echo 4. 文件格式要求:
echo    - 包含股票名称列
echo    - 可选包含价格列用于验证
echo    - 支持.xlsx, .xls, .csv格式
echo.
echo 更多详细信息请查看: 股票名称匹配器使用说明.md
echo.
pause
goto menu

:exit
echo 感谢使用股票名称匹配器！
pause
exit
