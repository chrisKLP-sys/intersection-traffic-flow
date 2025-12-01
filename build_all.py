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
import io

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    """清理旧的构建文件（不删除可执行文件）"""
    print_step(2, 5, "清理旧的构建文件...")
    
    dirs_to_remove = ['build', '__pycache__']
    removed_count = 0
    
    # 不删除 dist 目录中的 exe 文件，保留旧版本
    # PyInstaller 会自动覆盖同名文件，如果需要保留旧版本，请手动重命名
    
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

def create_version_rc_file(version_txt_file, rc_file):
    """从version_info.txt创建.rc文件（Windows资源文件）"""
    try:
        # 读取version_info.txt内容
        with open(version_txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析版本信息
        import re
        # 提取版本号
        filevers_match = re.search(r'filevers=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
        prodvers_match = re.search(r'prodvers=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
        
        # 提取字符串信息（使用更宽松的正则表达式，支持中文字符）
        # 匹配 u'...' 或 '...' 格式的字符串，支持中文字符和特殊字符
        def extract_string(key, default):
            # 匹配 StringStruct(u'Key', u'Value') 或 StringStruct('Key', 'Value') 格式
            # 使用非贪婪匹配，匹配到下一个 StringStruct 或 ] 为止
            patterns = [
                rf"StringStruct\([u]?'{key}',\s*[u]?'([^']+)'\)",  # 简单字符串（无转义）
                rf"StringStruct\([u]?'{key}',\s*[u]?\"([^\"]+)\"\)",  # 使用双引号
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
            return default
        
        company = extract_string("CompanyName", "chrisKLP-sys")
        description = extract_string("FileDescription", "交叉口交通流量流向可视化工具")
        copyright = extract_string("LegalCopyright", "Copyright (c) 2025 交叉口交通流量流向可视化工具")
        product = extract_string("ProductName", "交叉口交通流量流向可视化工具")
        comments = extract_string("Comments", "https://github.com/chrisKLP-sys/intersection-traffic-flow")
        
        if filevers_match:
            filevers = f"{filevers_match.group(1)},{filevers_match.group(2)},{filevers_match.group(3)},{filevers_match.group(4)}"
        else:
            filevers = "1,2,0,0"
        
        if prodvers_match:
            prodvers = f"{prodvers_match.group(1)},{prodvers_match.group(2)},{prodvers_match.group(3)},{prodvers_match.group(4)}"
        else:
            prodvers = "1,2,0,0"
        
        # 转义.rc文件中的特殊字符
        def escape_rc_string(s):
            # 转义双引号和反斜杠
            return s.replace('\\', '\\\\').replace('"', '\\"')
        
        # 创建.rc文件内容
        rc_content = f"""#include <winver.h>

VS_VERSION_INFO VERSIONINFO
FILEVERSION {filevers}
PRODUCTVERSION {prodvers}
FILEFLAGSMASK 0x3fL
FILEFLAGS 0x0L
FILEOS 0x40004L
FILETYPE 0x1L
FILESUBTYPE 0x0L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904B0"
        BEGIN
            VALUE "CompanyName", "{escape_rc_string(company)}"
            VALUE "FileDescription", "{escape_rc_string(description)}"
            VALUE "FileVersion", "{filevers.replace(',', '.')}"
            VALUE "InternalName", "{escape_rc_string(product)}"
            VALUE "LegalCopyright", "{escape_rc_string(copyright)}"
            VALUE "OriginalFilename", "{escape_rc_string(product)}.exe"
            VALUE "ProductName", "{escape_rc_string(product)}"
            VALUE "ProductVersion", "{prodvers.replace(',', '.')}"
            VALUE "Comments", "{escape_rc_string(comments)}"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200
    END
END
"""
        
        # 写入.rc文件
        # Windows资源编译器通常需要UTF-16 LE编码，但PyInstaller可能支持UTF-8 with BOM
        # 先尝试UTF-8 with BOM
        try:
            with open(rc_file, 'wb') as f:
                # 写入UTF-8 BOM
                f.write(b'\xef\xbb\xbf')
                # 写入UTF-8编码的内容
                f.write(rc_content.encode('utf-8'))
        except Exception as e:
            # 如果失败，尝试UTF-16 LE（Windows资源编译器标准格式）
            print(f"  ⚠ UTF-8编码失败，尝试UTF-16 LE: {e}")
            with open(rc_file, 'wb') as f:
                # 写入UTF-16 LE BOM
                f.write(b'\xff\xfe')
                # 写入UTF-16 LE编码的内容
                f.write(rc_content.encode('utf-16-le'))
        
        return True
    except Exception as e:
        print(f"  ⚠ 创建.rc文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def build_application():
    """执行打包"""
    print_step(3, 5, "开始打包...")
    
    system_info = get_system_info()
    system = system_info['system']
    
    print(f"  检测到系统: {system} ({system_info['machine']})")
    
    # 主程序文件
    main_file = 'main.py'
    
    if not os.path.exists(main_file):
        print(f"  ❌ 未找到主程序文件: {main_file}")
        return False
    
    print(f"  使用主文件: {main_file}")
    
    # 检查帮助文档是否存在
    datas = []
    help_files = []
    
    help_file_zh = '帮助文档_中文.html'
    help_file_en = '帮助文档_English.html'
    if os.path.exists(help_file_zh):
        help_files.append(help_file_zh)
        print(f"  ✓ 找到帮助文档: {help_file_zh}")
    else:
        print(f"  ⚠ 未找到帮助文档: {help_file_zh}")
    if os.path.exists(help_file_en):
        help_files.append(help_file_en)
        print(f"  ✓ 找到帮助文档: {help_file_en}")
    else:
        print(f"  ⚠ 未找到帮助文档: {help_file_en}")
    
    # 添加帮助文档到数据文件列表
    for help_file in help_files:
        datas.append((help_file, '.'))
    
    # 检查并添加二维码文件
    qrcode_file = 'qrcode.jpg'
    if os.path.exists(qrcode_file):
        datas.append((qrcode_file, '.'))
        print(f"  ✓ 找到二维码文件: {qrcode_file}")
    else:
        print(f"  ⚠ 未找到二维码文件: {qrcode_file}")
    
    # 检查图标文件是否存在
    icon_file = None
    # 优先使用Sparrow.png作为图标
    sparrow_png = 'Sparrow.png'
    icon_ico = 'app_icon.ico'
    icon_png = 'app_icon.png'
    
    # 优先使用Sparrow.png（用于窗口图标）
    if os.path.exists(sparrow_png):
        datas.append((sparrow_png, '.'))
        print(f"  ✓ 找到并添加窗口图标: {sparrow_png}")
        # 如果存在Sparrow.ico，也用于可执行文件图标
        sparrow_ico = 'Sparrow.ico'
        if os.path.exists(sparrow_ico):
            icon_file = sparrow_ico
            print(f"  ✓ 找到可执行文件图标: {sparrow_ico}")
        else:
            # 如果没有ICO文件，尝试从PNG转换（需要PIL）
            try:
                from PIL import Image
                # 尝试创建ICO文件
                img = Image.open(sparrow_png)
                # 创建多个尺寸的图标（Windows需要）
                sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
                img.save(sparrow_ico, format='ICO', sizes=sizes)
                icon_file = sparrow_ico
                print(f"  ✓ 已从PNG生成ICO文件: {sparrow_ico}")
            except Exception as e:
                print(f"  ⚠ 无法从PNG生成ICO文件: {e}")
                print(f"  ⚠ 可执行文件将使用默认图标，窗口图标仍会使用Sparrow.png")
                # 尝试使用旧的ICO文件作为后备
                if os.path.exists(icon_ico):
                    icon_file = icon_ico
                    print(f"  ✓ 使用后备图标文件: {icon_ico}")
    # 向后兼容：如果没有Sparrow.png，使用app_icon
    elif os.path.exists(icon_ico):
        icon_file = icon_ico
        print(f"  ✓ 找到图标文件: {icon_ico}")
    elif os.path.exists(icon_png):
        datas.append((icon_png, '.'))
        print(f"  ✓ 找到PNG图标: {icon_png}，建议运行 convert_icon.py 生成ICO文件")
        print(f"  ✓ 添加窗口图标: {icon_png}")
    
    # 检查并添加字体文件
    fonts_dir = 'fonts'
    if os.path.exists(fonts_dir):
        font_count = 0
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith(('.ttf', '.otf', '.ttc')):
                font_path = os.path.join(fonts_dir, font_file)
                datas.append((font_path, 'fonts'))
                font_count += 1
        if font_count > 0:
            print(f"  ✓ 找到 {font_count} 个字体文件")
        else:
            print(f"  ⚠ 未找到字体文件（.ttf, .otf, .ttc）")
    else:
        print(f"  ⚠ 未找到字体目录: {fonts_dir}")
    
    # 构建 PyInstaller 命令
    # 2.3版本需要包含update_checker.py模块
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--name', '交叉口交通流量流向可视化工具',
        main_file
    ]
    
    # 添加图标（可执行文件图标）
    if icon_file and system == 'Windows':
        cmd.extend(['--icon', icon_file])
        print(f"  ✓ 使用图标: {icon_file}")
    
    # 添加版本信息（仅Windows）
    # PyInstaller的--version-file参数期望version_info.txt格式（Python代码格式），而不是.rc文件
    if system == 'Windows':
        version_file = 'version_info.txt'
        if os.path.exists(version_file):
            cmd.extend(['--version-file', version_file])
            print(f"  ✓ 使用版本信息: {version_file}")
        else:
            print(f"  ⚠ 未找到版本信息文件: {version_file}")
    
    # macOS 特殊处理
    if system == 'Darwin':
        # macOS 使用 windowed 模式，但添加一些额外选项
        cmd.append('--windowed')
        # 添加 macOS 特定的选项
        cmd.extend(['--osx-bundle-identifier', 'com.trafficflow.app'])
    else:
        # Windows 使用 windowed 模式
        cmd.append('--windowed')
    
    # 添加version_info.txt到数据文件（作为后备，用于读取版本号）
    version_info_file = 'version_info.txt'
    if os.path.exists(version_info_file):
        datas.append((version_info_file, '.'))
        print(f"  ✓ 添加版本信息文件: {version_info_file}")
    
    # 添加数据文件（帮助文档、图标和版本信息文件）
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
        'urllib.error',  # 用于错误处理
        'subprocess',  # 用于备用打开方式
        'json',  # 用于解析API响应
        'threading',  # 用于后台更新检查
        'tempfile',  # 用于临时文件
        'shutil',  # 用于文件操作
        'platform',  # 用于系统检测
        # pywin32模块（可选，代码中有fallback，但包含它们可以提升功能）
        'win32api',  # 用于Windows版本信息（可选）
        'win32file',  # 用于Windows文件操作（可选）
        'pywintypes',  # pywin32的基础类型模块
        'win32con',  # Windows常量定义
        'PIL',  # Pillow，matplotlib需要
        'PIL.Image',  # PIL的Image模块
        'PIL.PdfImagePlugin',  # PDF图像支持
        'PIL.PdfParser',  # PDF解析器
        'update_checker',  # 更新检查模块（2.3版本新增）
    ]
    
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    # 排除不需要的模块（注意：不能排除PIL，matplotlib需要它）
    excludes = ['scipy', 'pandas', 'IPython', 'jupyter', 'notebook']
    for exc in excludes:
        cmd.extend(['--exclude-module', exc])
    
    print(f"  执行命令: {' '.join(cmd[:5])}... (共 {len(cmd)} 个参数)")
    print("  这可能需要几分钟时间，请耐心等待...\n")
    print("  [开始打包，实时输出如下：]")
    print("  " + "=" * 60)
    print("  💡 提示：")
    print("     - 'Hidden import not found' 警告是正常的（pywin32模块是可选的）")
    print("     - 'Permission denied' 警告会自动重试，通常不是问题")
    print("     - 打包过程可能需要几分钟，请耐心等待...")
    print("  " + "=" * 60)
    
    try:
        # 执行打包，实时显示输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将stderr合并到stdout
            text=True,
            bufsize=0,  # 无缓冲，立即输出
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'  # 处理编码错误
        )
        
        # 实时输出每一行，只显示关键信息
        output_lines = []
        last_status = ""
        last_message = ""  # 避免重复显示相同消息
        
        # 使用迭代器逐行读取，并立即刷新输出
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            line = line.rstrip()
            if line:
                output_lines.append(line)
                line_lower = line.lower()
                
                # 只显示关键阶段信息
                current_message = ""
                if any(keyword in line_lower for keyword in [
                    'analyzing modules for base_library',  # 分析基础库
                    'analyzing ',  # 分析主程序（简化显示）
                    'building',  # 构建
                    'creating',  # 创建
                    'copying',  # 复制
                    'writing',  # 写入
                    'checking',  # 检查
                    'collecting',  # 收集
                    'running analysis',  # 运行分析
                    'looking for python',  # 查找Python
                    'using python',  # 使用Python
                    'platform:',  # 平台信息
                    'pyinstaller:',  # PyInstaller版本
                ]):
                    # 简化显示，只显示关键部分
                    if 'analyzing ' in line_lower and '.py' in line:
                        # 只显示"Analyzing 主程序文件"
                        if '交叉口' in line or 'intersection' in line_lower:
                            current_message = "📦 正在分析主程序..."
                    elif 'building' in line_lower and 'analysis' not in line_lower:
                        current_message = "🔨 正在构建..."
                    elif 'creating' in line_lower and 'pyz' in line_lower:
                        current_message = "📝 正在创建压缩包..."
                    elif 'copying' in line_lower:
                        current_message = "📋 正在复制文件..."
                    elif 'writing' in line_lower and ('exe' in line_lower or 'executable' in line_lower):
                        current_message = "💾 正在写入可执行文件..."
                    elif 'checking' in line_lower and 'analysis' in line_lower:
                        current_message = "✓ 检查完成"
                    elif 'collecting' in line_lower:
                        current_message = "📚 正在收集依赖..."
                    elif 'running analysis' in line_lower:
                        current_message = "🔍 运行依赖分析..."
                    elif 'platform:' in line_lower or 'pyinstaller:' in line_lower:
                        # 只显示一次环境信息
                        if not last_status.startswith("环境"):
                            current_message = line.split('INFO:')[-1].strip()
                            last_status = "环境"
                
                # 显示警告和错误（重要），但过滤掉乱码行
                if 'warning' in line_lower or 'error' in line_lower or 'failed' in line_lower:
                    # 过滤掉包含乱码的警告行（通常是路径问题）
                    if 'warnings written to' in line_lower or 'warn-' in line_lower:
                        # 跳过这些乱码警告行
                        continue
                    # 处理隐藏导入错误（这些是可选的，不影响打包）
                    if 'hidden import' in line_lower and 'not found' in line_lower:
                        # 这些是可选的pywin32模块，没有安装也不影响
                        module_name = line.split("'")[1] if "'" in line else ""
                        if module_name in ['win32file', 'pywintypes', 'win32con']:
                            # 这些是可选的，不显示错误，只记录
                            continue
                    # 处理权限错误（PyInstaller会自动重试，通常不是问题）
                    if 'permission denied' in line_lower and 'retrying' in line_lower:
                        # 这是正常的重试，不显示
                        continue
                    # 显示其他重要的警告和错误
                    error_msg = line.split('INFO:')[-1].strip() if 'INFO:' in line else line
                    error_msg = line.split('ERROR:')[-1].strip() if 'ERROR:' in line else error_msg
                    error_msg = line.split('WARNING:')[-1].strip() if 'WARNING:' in line else error_msg
                    current_message = f"⚠ {error_msg}"
                # 显示完成信息
                elif any(keyword in line_lower for keyword in ['complete', 'success', 'done', 'finished', 'successfully']):
                    current_message = f"✓ {line.split('INFO:')[-1].strip() if 'INFO:' in line else line}"
                # 显示最终结果
                elif 'executable' in line_lower or ('exe' in line_lower and ('created' in line_lower or 'written' in line_lower)):
                    current_message = f"✅ {line.split('INFO:')[-1].strip() if 'INFO:' in line else line}"
                
                # 只显示新消息，避免重复
                if current_message and current_message != last_message:
                    print(f"  {current_message}", flush=True)  # 立即刷新输出
                    last_message = current_message
        
        # 等待进程完成
        return_code = process.wait()
        
        print("  " + "=" * 60)
        
        if return_code == 0:
            print("  ✓ 打包命令执行成功")
            return True
        else:
            print(f"  ❌ 打包失败，退出码: {return_code}")
            # 显示最后几行错误信息
            if output_lines:
                print("  最后几行输出：")
                for line in output_lines[-10:]:
                    print(f"    {line}")
            return False
    except FileNotFoundError:
        print("  " + "=" * 60)
        print("  ❌ 未找到 PyInstaller，请先安装: pip install pyinstaller")
        return False
    except Exception as e:
        print("  " + "=" * 60)
        print(f"  ❌ 打包过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_build():
    """验证打包结果（只检查文件名，不检查详细信息）"""
    print_step(4, 5, "验证打包结果...")
    
    system = platform.system()
    
    if system == 'Windows':
        exe_path = os.path.join('dist', '交叉口交通流量流向可视化工具.exe')
    else:
        exe_path = os.path.join('dist', '交叉口交通流量流向可视化工具')
    
    # 只检查文件是否存在（比对文件名），不检查文件大小等详细信息
    if os.path.exists(exe_path):
        print(f"  ✓ 可执行文件已生成: {os.path.basename(exe_path)}")
        return True, exe_path
    else:
        print(f"  ❌ 未找到可执行文件: {os.path.basename(exe_path)}")
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
            print("  2. 在终端中运行: ./dist/交叉口交通流量流向可视化工具")
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
    print_header("交叉口交通流量流向可视化工具 - 统一打包脚本")
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 主程序文件
    main_file = 'main.py'
    
    if not os.path.exists(main_file):
        print(f"❌ 错误: 未找到主程序文件: {main_file}")
        print("   请确保文件存在，或在项目根目录下运行此脚本")
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

