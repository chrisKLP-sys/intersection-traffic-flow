# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
用于打包交叉口流量绘制应用程序
"""

block_cipher = None

# 检查帮助文档和图标文件是否存在
import os
help_file = '帮助文档.html'
datas_list = []
if os.path.exists(help_file):
    datas_list.append((help_file, '.'))

# 添加字体文件
fonts_dir = 'fonts'
if os.path.exists(fonts_dir):
    for font_file in os.listdir(fonts_dir):
        if font_file.endswith(('.ttf', '.otf', '.ttc')):
            font_path = os.path.join(fonts_dir, font_file)
            datas_list.append((font_path, 'fonts'))

# 添加图标文件（用于窗口图标）
if os.path.exists('app_icon.png'):
    datas_list.append(('app_icon.png', '.'))

# 自动检测主文件
<<<<<<< Updated upstream
main_files = ['交叉口交通流量流向可视化工具1.2.py', '交叉口流量绘制1.1.py', '交叉口流量绘制1.0.py', 'Alpha1.0.py']
main_file = '交叉口交通流量流向可视化工具1.2.py'  # 默认值
=======
main_files = ['交叉口交通流量流向可视化工具1.3.py', '交叉口交通流量流向可视化工具1.2.py', '交叉口流量绘制1.1.py', '交叉口流量绘制1.0.py', 'Alpha1.0.py']
main_file = '交叉口交通流量流向可视化工具1.3.py'  # 默认值
>>>>>>> Stashed changes
for file in main_files:
    if os.path.exists(file):
        main_file = file
        break

a = Analysis(
    [main_file],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',  # 用于在tkinter中显示图形
        'matplotlib.backends.backend_svg',    # 用于导出SVG
        'matplotlib.backends.backend_pdf',    # 用于导出PDF
        'matplotlib.backends._backend_pdf_ps',  # PDF后端的内部模块
        'matplotlib.backends.backend_agg',    # 用于导出PNG/JPG/TIF
        'matplotlib.figure',
        'matplotlib.font_manager',
        'matplotlib.colors',  # 需要PIL
        'pkg_resources.py2_warn',
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'scipy',
        'pandas',
        # 注意：不能排除PIL，matplotlib需要它
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 检查ICO图标文件是否存在（用于可执行文件图标）
icon_file = None
if os.path.exists('app_icon.ico'):
    icon_file = 'app_icon.ico'

# 检查版本信息文件（仅Windows）
# PyInstaller的version参数期望version_info.txt格式（Python代码格式），而不是.rc文件
version_file = None
if os.path.exists('version_info.txt'):
    version_file = 'version_info.txt'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='交叉口交通流量流向可视化工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口（GUI应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # 可执行文件图标
    version=version_file,  # 版本信息文件（仅Windows）
)

