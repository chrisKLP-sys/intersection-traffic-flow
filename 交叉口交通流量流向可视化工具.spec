# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['交叉口交通流量流向可视化工具1.3.py'],
    pathex=[],
    binaries=[],
    datas=[('帮助文档.html', '.'), ('fonts\\SourceHanSansCN-Regular.otf', 'fonts')],
    hiddenimports=['matplotlib.backends.backend_tkagg', 'matplotlib.backends.backend_svg', 'matplotlib.backends.backend_pdf', 'matplotlib.backends._backend_pdf_ps', 'matplotlib.backends.backend_agg', 'matplotlib.figure', 'matplotlib.font_manager', 'matplotlib.colors', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'webbrowser', 'urllib.parse', 'urllib.request', 'subprocess', 'PIL', 'PIL.Image', 'PIL.PdfImagePlugin', 'PIL.PdfParser'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['scipy', 'pandas', 'IPython', 'jupyter', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='交叉口交通流量流向可视化工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
)
