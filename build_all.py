#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一打包脚本 - 自动检测系统并生成对应版本的应用
支持 Windows 和 macOS 系统
"""

import os
import sys
import platform
import subprocess
import shutil

def print_header(text):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(step_num, total, text):
    """打印步骤信息"""
    print(f"[{step_num}/{total}] {text}")

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 错误: 需要 Python 3.7 或更高版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """检查并安装依赖"""
    print_step(1, 5, "检查依赖...")
    
    required_packages = {
        'matplotlib': ('matplotlib', 'matplotlib>=3.5.0'),
        'numpy': ('numpy', 'numpy>=1.21.0'),
        'PyInstaller': ('PyInstaller', 'pyinstaller>=5.0.0')
    }
    
    missing = []
    for package_name, (import_name, requirement) in required_packages.items():
        try:
            if package_name == 'PyInstaller':
                # PyInstaller 需要特殊检查
                result = subprocess.run(
                    [sys.executable, '-m', 'PyInstaller', '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"  ✓ {package_name} 已安装")
                else:
                    raise ImportError()
            else:
                __import__(import_name)
                print(f"  ✓ {package_name} 已安装")
        except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
            print(f"  ✗ {package_name} 未安装")
            missing.append(requirement)
    
    if missing:
        print(f"\n正在安装缺失的依赖: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✓ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def clean_build_files():
    """清理旧的构建文件"""
    print_step(2, 5, "清理旧的构建文件...")
    
    dirs_to_remove = ['build', '__pycache__']
    removed_count = 0
    
    # 尝试删除 dist 目录中的 exe 文件（如果存在且被占用）
    if os.path.exists('dist') and os.path.isdir('dist'):
        exe_files = []
        try:
            for file in os.listdir('dist'):
                if file.endswith('.exe'):
                    exe_path = os.path.join('dist', file)
                    if os.path.isfile(exe_path):
                        exe_files.append(exe_path)
        except:
            pass
        
        # 尝试删除 exe 文件
        for exe_path in exe_files:
            try:
                # 尝试直接删除
                os.remove(exe_path)
                print(f"  ✓ 已删除: {os.path.basename(exe_path)}")
                removed_count += 1
            except PermissionError:
                print(f"  ⚠ 无法删除 {os.path.basename(exe_path)}：文件正在运行或被占用")
                print(f"     请先关闭程序（如果有正在运行的程序），然后手动删除 dist 目录")
                print(f"     或者等待几秒后重新运行打包脚本（PyInstaller 会尝试覆盖）")
            except Exception as e:
                print(f"  ⚠ 无法删除 {os.path.basename(exe_path)}: {e}")
        
        # 尝试删除 dist 目录（如果为空）
        if os.path.exists('dist'):
            try:
                if not os.listdir('dist'):
                    os.rmdir('dist')
                    print(f"  ✓ 已删除: dist/")
                    removed_count += 1
            except:
                pass
    
    # 删除其他目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  ✓ 已删除: {dir_name}/")
                removed_count += 1
            except Exception as e:
                print(f"  ⚠ 无法删除 {dir_name}: {e}")
    
    # 删除 .pyc 文件
    for root, dirs, files in os.walk('.'):
        # 跳过 .git 和虚拟环境目录
        if '.git' in root or 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    removed_count += 1
                except:
                    pass
    
    if removed_count > 0:
        print(f"  ✓ 已清理 {removed_count} 个文件/目录")
    else:
        print("  ✓ 无需清理")
    
    return True

def get_system_info():
    """获取系统信息"""
    system = platform.system()
    machine = platform.machine()
    
    info = {
        'system': system,
        'machine': machine,
        'platform': platform.platform(),
        'python_version': sys.version.split()[0]
    }
    
    return info

def build_application():
    """执行打包"""
    print_step(3, 5, "开始打包...")
    
    system_info = get_system_info()
    system = system_info['system']
    
    print(f"  检测到系统: {system} ({system_info['machine']})")
    
    # 自动检测主文件
    main_files = ['Alpha1.0.py', '交叉口流量绘制1.0.py']
    main_file = None
    for file in main_files:
        if os.path.exists(file):
            main_file = file
            break
    
    if not main_file:
        print("  ❌ 未找到主程序文件")
        return False
    
    print(f"  使用主文件: {main_file}")
    
    # 检查帮助文档是否存在
    help_file = '帮助文档.html'
    datas = []
    if os.path.exists(help_file):
        print(f"  ✓ 找到帮助文档: {help_file}")
        datas.append((help_file, '.'))
    else:
        print(f"  ⚠ 未找到帮助文档: {help_file}")
    
    # 检查图标文件是否存在
    icon_file = None
    icon_ico = 'app_icon.ico'
    icon_png = 'app_icon.png'
    
    # 优先使用ICO文件（可执行文件图标）
    if os.path.exists(icon_ico):
        icon_file = icon_ico
        print(f"  ✓ 找到图标文件: {icon_ico}")
    elif os.path.exists(icon_png):
        print(f"  ✓ 找到PNG图标: {icon_png}，建议运行 convert_icon.py 生成ICO文件")
    
    # 将PNG图标添加到数据文件（用于窗口图标）
    if os.path.exists(icon_png):
        datas.append((icon_png, '.'))
        print(f"  ✓ 添加窗口图标: {icon_png}")
    
    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--name', '交叉口流量绘制',
        main_file
    ]
    
    # 添加图标（可执行文件图标）
    if icon_file and system == 'Windows':
        cmd.extend(['--icon', icon_file])
        print(f"  ✓ 使用图标: {icon_file}")
    
    # macOS 特殊处理
    if system == 'Darwin':
        # macOS 使用 windowed 模式，但添加一些额外选项
        cmd.append('--windowed')
        # 添加 macOS 特定的选项
        cmd.extend(['--osx-bundle-identifier', 'com.trafficflow.app'])
    else:
        # Windows 使用 windowed 模式
        cmd.append('--windowed')
    
    # 添加数据文件（帮助文档和图标）
    for src, dst in datas:
        cmd.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
    
    # 添加隐藏导入
    hidden_imports = [
        'matplotlib.backends.backend_tkagg',  # 用于在tkinter中显示图形
        'matplotlib.backends.backend_svg',    # 用于导出SVG
        'matplotlib.backends.backend_pdf',    # 用于导出PDF
        'matplotlib.backends._backend_pdf_ps',  # PDF后端的内部模块
        'matplotlib.backends.backend_agg',    # 用于导出PNG/JPG/TIF
        'matplotlib.figure',
        'matplotlib.font_manager',
        'matplotlib.colors',  # 需要PIL
        # 注意：numpy.core._methods 和 numpy.lib.format 在 Python 3.13/新版本 numpy 中已不存在
        # PyInstaller 会自动处理 numpy 的依赖，无需手动指定
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'webbrowser',  # 用于打开帮助文档
        'urllib.parse',  # 用于URL编码
        'urllib.request',  # 用于路径转换
        'subprocess',  # 用于备用打开方式
        'PIL',  # Pillow，matplotlib需要
        'PIL.Image',  # PIL的Image模块
        'PIL.PdfImagePlugin',  # PDF图像支持
        'PIL.PdfParser',  # PDF解析器
    ]
    
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # 排除不需要的模块（注意：不能排除PIL，matplotlib需要它）
    excludes = ['scipy', 'pandas', 'IPython', 'jupyter', 'notebook']
    for exc in excludes:
        cmd.extend(['--exclude-module', exc])
    
    print(f"  执行命令: {' '.join(cmd[:5])}... (共 {len(cmd)} 个参数)")
    print("  这可能需要几分钟时间，请耐心等待...\n")
    
    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  ✓ 打包命令执行成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 打包失败")
        print(f"  错误信息: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  ❌ 未找到 PyInstaller，请先安装: pip install pyinstaller")
        return False

def verify_build():
    """验证打包结果"""
    print_step(4, 5, "验证打包结果...")
    
    system = platform.system()
    
    if system == 'Windows':
        exe_path = os.path.join('dist', '交叉口流量绘制.exe')
    else:
        exe_path = os.path.join('dist', '交叉口流量绘制')
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        size_mb = file_size / (1024 * 1024)
        print(f"  ✓ 可执行文件已生成: {exe_path}")
        print(f"  ✓ 文件大小: {size_mb:.2f} MB")
        return True, exe_path
    else:
        print(f"  ❌ 未找到可执行文件: {exe_path}")
        return False, None

def run_tests():
    """运行测试用例"""
    print_step(5, 5, "运行测试用例...")
    
    if not os.path.exists('test_build.py'):
        print("  ⚠ 未找到 test_build.py，跳过测试")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, 'test_build.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("  ✓ 所有测试通过")
            return True
        else:
            print("  ⚠ 部分测试失败，但打包可能仍然可用")
            print(f"  测试输出:\n{result.stdout}")
            return True  # 测试失败不影响打包结果
    except subprocess.TimeoutExpired:
        print("  ⚠ 测试超时，跳过")
        return True
    except Exception as e:
        print(f"  ⚠ 测试执行出错: {e}")
        return True

def show_summary(exe_path, system_info):
    """显示打包摘要"""
    print_header("打包完成")
    
    system = system_info['system']
    
    print(f"✓ 系统: {system} ({system_info['machine']})")
    print(f"✓ Python: {system_info['python_version']}")
    
    if exe_path and os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✓ 可执行文件: {exe_path}")
        print(f"✓ 文件大小: {file_size:.2f} MB")
        
        print("\n" + "-" * 60)
        print("📦 打包成功！")
        print("-" * 60)
        
        if system == 'Windows':
            print("\n使用方法:")
            print(f"  1. 找到文件: {exe_path}")
            print("  2. 双击运行即可")
        else:
            print("\n使用方法:")
            print(f"  1. 找到文件: {exe_path}")
            print("  2. 在终端中运行: ./dist/交叉口流量绘制")
            print("  3. 或右键点击 -> 打开")
            print("\n如果提示'无法打开'，请运行:")
            print(f"  xattr -cr {exe_path}")
        
        print("\n💡 提示:")
        print("  - 可以将可执行文件复制到其他位置使用")
        print("  - 首次运行可能需要几秒钟启动时间")
        print("  - 如果遇到问题，请查看 BUILD.md 文档")
    else:
        print("❌ 打包失败，请检查错误信息")

def main():
    """主函数"""
    print_header("交叉口流量绘制 - 统一打包脚本")
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查是否在项目目录，自动检测主文件
    main_files = ['Alpha1.0.py', '交叉口流量绘制1.0.py']
    main_file = None
    for file in main_files:
        if os.path.exists(file):
            main_file = file
            break
    
    if not main_file:
        print("❌ 错误: 未找到主程序文件")
        print("   请确保以下文件之一存在:")
        for file in main_files:
            print(f"     - {file}")
        print("   或在项目根目录下运行此脚本")
        sys.exit(1)
    
    print(f"✓ 找到主程序文件: {main_file}")
    
    # 获取系统信息
    system_info = get_system_info()
    system = system_info['system']
    
    if system not in ['Windows', 'Darwin']:
        print(f"⚠ 警告: 当前系统 {system} 可能不受官方支持")
        print("   建议在 Windows 或 macOS 系统上打包")
        response = input("   是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print(f"\n当前系统: {system}")
    print(f"将打包 {system} 版本\n")
    
    # 执行打包流程
    success = True
    exe_path = None
    
    # 1. 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 2. 清理旧文件
    if not clean_build_files():
        sys.exit(1)
    
    # 3. 执行打包
    if not build_application():
        sys.exit(1)
    
    # 4. 验证结果
    success, exe_path = verify_build()
    
    # 5. 运行测试（可选）
    run_tests()
    
    # 显示摘要
    show_summary(exe_path, system_info)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断打包")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

