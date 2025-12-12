@echo off
chcp 65001 >nul
echo ====================================
echo   扫雷辅助工具 - GUI版本
echo ====================================
echo.
echo 正在启动图形界面...
echo.
python minesweeper_gui.py
if errorlevel 1 (
    echo.
    echo 错误：程序运行失败！
    echo.
    echo 可能的原因：
    echo 1. 未安装Python
    echo 2. 未安装依赖包
    echo.
    echo 解决方案：
    echo 1. 确保已安装Python 3.7+
    echo 2. 运行: pip install -r requirements.txt
    echo.
    pause
)

