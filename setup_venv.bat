@echo off
chcp 65001 >nul
echo ================================================
echo 交叉口流量绘制 - 虚拟环境设置
echo ================================================
echo.

set VENV_DIR=venv

REM 检查是否已存在虚拟环境
if exist %VENV_DIR% (
    echo 检测到已存在的虚拟环境目录: %VENV_DIR%
    set /p response="是否删除并重建? (y/n): "
    if /i "%response%"=="y" (
        echo 正在删除旧的虚拟环境...
        rmdir /s /q %VENV_DIR%
        echo 已删除旧的虚拟环境
    ) else (
        echo 保留现有虚拟环境
        goto :install
    )
)

REM 创建虚拟环境
echo.
echo 正在创建虚拟环境: %VENV_DIR%
python -m venv %VENV_DIR%
if errorlevel 1 (
    echo 虚拟环境创建失败！
    pause
    exit /b 1
)

echo 虚拟环境创建成功！

:install
REM 升级pip
echo.
echo 正在升级pip...
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip

REM 安装依赖
echo.
if exist requirements.txt (
    echo 正在从 requirements.txt 安装依赖...
    %VENV_DIR%\Scripts\pip.exe install -r requirements.txt
) else (
    echo 未找到 requirements.txt 文件
    echo 正在安装基础依赖...
    %VENV_DIR%\Scripts\pip.exe install matplotlib>=3.5.0 numpy>=1.21.0 pyinstaller>=5.0.0 Pillow>=8.0.0
)

if errorlevel 1 (
    echo.
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ================================================
echo 虚拟环境设置完成！
echo ================================================
echo.
echo 要激活虚拟环境，请运行:
echo   %VENV_DIR%\Scripts\activate
echo.
echo 或者直接使用虚拟环境中的Python:
echo   %VENV_DIR%\Scripts\python.exe 交叉口交通流量流向可视化工具1.2.py
echo.
pause

