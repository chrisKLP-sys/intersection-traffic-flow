# 虚拟环境使用说明

## 问题说明

在 PowerShell 中激活虚拟环境时，可能会遇到执行策略限制的错误。这是因为 Windows 默认禁止运行未签名的脚本。

## 解决方案

### 方案一：使用批处理文件激活（推荐，最简单）

直接双击运行 `激活虚拟环境.bat` 文件，或在命令提示符（CMD）中运行：

```cmd
激活虚拟环境.bat
```

或直接运行：

```cmd
venv\Scripts\activate.bat
```

### 方案二：修复 PowerShell 执行策略

运行 `修复PowerShell执行策略.ps1` 脚本：

```powershell
.\修复PowerShell执行策略.ps1
```

或者手动设置（在 PowerShell 中运行，需要管理员权限）：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 方案三：直接使用虚拟环境中的 Python（无需激活）

这是最简单的方法，不需要激活虚拟环境：

```powershell
venv\Scripts\python.exe 交叉口流量绘制1.1.py
```

或者：

```cmd
venv\Scripts\python.exe 交叉口流量绘制1.1.py
```

### 方案四：临时绕过执行策略（仅当前会话）

在 PowerShell 中运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\Activate.ps1
```

## 推荐工作流程

1. **开发时**：使用 `激活虚拟环境.bat` 或直接使用 `venv\Scripts\python.exe`
2. **运行程序**：直接使用 `venv\Scripts\python.exe 交叉口流量绘制1.1.py`

## 验证虚拟环境

安装依赖后，可以验证：

```cmd
venv\Scripts\python.exe -m pip list
```

应该能看到已安装的包：
- matplotlib
- numpy
- pyinstaller
- Pillow

