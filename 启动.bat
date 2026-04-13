@echo off
chcp 65001 >nul
title 鼠大师 - 鼠标键盘操控程序

echo ========================================
echo     鼠大师 - 鼠标键盘操控程序
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6+
    echo.
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 正在检查依赖包...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 首次运行，正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖包安装完成
    echo.
)

echo [信息] 正在启动程序...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行出错
    pause
)
