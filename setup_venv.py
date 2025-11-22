#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
虚拟环境设置脚本
用于创建虚拟环境并安装项目依赖
"""
import os
import sys
import subprocess
import shutil

def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def main():
    print("="*50)
    print("交叉口流量绘制 - 虚拟环境设置")
    print("="*50)
    
    venv_dir = "venv"
    
    # 检查是否已存在虚拟环境
    if os.path.exists(venv_dir):
        print(f"\n检测到已存在的虚拟环境目录: {venv_dir}")
        response = input("是否删除并重建? (y/n): ").strip().lower()
        if response == 'y':
            print(f"正在删除旧的虚拟环境...")
            try:
                shutil.rmtree(venv_dir)
                print("已删除旧的虚拟环境")
            except Exception as e:
                print(f"删除失败: {e}")
                return False
        else:
            print("保留现有虚拟环境")
            return True
    
    # 创建虚拟环境
    print(f"\n正在创建虚拟环境: {venv_dir}")
    if not run_command(f"{sys.executable} -m venv {venv_dir}", "创建虚拟环境"):
        print("\n虚拟环境创建失败！")
        return False
    
    print("\n虚拟环境创建成功！")
    
    # 确定激活脚本路径
    if sys.platform == "win32":
        pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")
    
    # 升级pip
    print("\n正在升级pip...")
    if not run_command(f'"{python_path}" -m pip install --upgrade pip', "升级pip"):
        print("警告: pip升级失败，但可以继续")
    
    # 安装依赖
    if os.path.exists("requirements.txt"):
        print("\n正在从 requirements.txt 安装依赖...")
        if run_command(f'"{pip_path}" install -r requirements.txt', "安装项目依赖"):
            print("\n" + "="*50)
            print("虚拟环境设置完成！")
            print("="*50)
            print("\n要激活虚拟环境，请运行:")
            if sys.platform == "win32":
                print(f"  {venv_dir}\\Scripts\\activate")
            else:
                print(f"  source {venv_dir}/bin/activate")
            print("\n或者直接使用虚拟环境中的Python:")
            print(f'  "{python_path}" 交叉口交通流量流向可视化工具1.2.py')
            return True
        else:
            print("\n依赖安装失败！")
            return False
    else:
        print("\n未找到 requirements.txt 文件")
        print("正在安装基础依赖...")
        packages = "matplotlib>=3.5.0 numpy>=1.21.0 pyinstaller>=5.0.0 Pillow>=8.0.0"
        if run_command(f'"{pip_path}" install {packages}', "安装基础依赖"):
            print("\n" + "="*50)
            print("虚拟环境设置完成！")
            print("="*50)
            return True
        else:
            print("\n依赖安装失败！")
            return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

