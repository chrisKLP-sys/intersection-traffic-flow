@echo off
chcp 65001 >nul
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat
echo.
echo 虚拟环境已激活！
echo 您现在可以使用以下命令运行程序:
echo   python 交叉口流量绘制1.0.py
echo.
cmd /k

