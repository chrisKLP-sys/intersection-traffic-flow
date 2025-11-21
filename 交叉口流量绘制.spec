# -*- mode: python ; coding: utf-8 -*-


# 数据文件列表（包含帮助文档和图标）
datas = [('帮助文档.html', '.')]
# 添加图标文件（如果存在）
import os
if os.path.exists('app_icon.png'):
    datas.append(('app_icon.png', '.'))

a = Analysis(
    ['交叉口流量绘制1.0.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['matplotlib.backends.backend_tkagg', 'matplotlib.backends.backend_svg', 'matplotlib.backends.backend_pdf', 'matplotlib.backends._backend_pdf_ps', 'matplotlib.backends.backend_agg', 'matplotlib.figure', 'matplotlib.font_manager', 'matplotlib.colors', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'webbrowser', 'urllib.parse', 'urllib.request', 'subprocess', 'PIL', 'PIL.Image', 'PIL.PdfImagePlugin', 'PIL.PdfParser'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['scipy', 'pandas', 'IPython', 'jupyter', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# 检查ICO图标文件是否存在
icon_file = None
if os.path.exists('app_icon.ico'):
    icon_file = 'app_icon.ico'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='交叉口流量绘制',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=icon_file,  # 可执行文件图标
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
