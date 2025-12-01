# -*- coding: utf-8 -*-
"""UI工具函数模块"""
import os
import sys
import platform
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import matplotlib.font_manager as fm

# Windows API 用于临时加载字体
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        gdi32 = ctypes.windll.gdi32
        WINDOWS_FONT_LOADED = False
        WINDOWS_FONT_HANDLE = None
    except:
        gdi32 = None
        WINDOWS_FONT_LOADED = False
        WINDOWS_FONT_HANDLE = None
else:
    gdi32 = None
    WINDOWS_FONT_LOADED = False
    WINDOWS_FONT_HANDLE = None

# 导入ttkbootstrap（如果可用）
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    ttkb = None

# 全局变量：存储图标对象引用
_app_icon = None
_cached_pil_image = None  # 缓存缩放后的PIL Image对象（避免重复加载和缩放大文件）

# 全局变量：GUI字体
GUI_FONT_FAMILY = None
_custom_font_file = None  # 存储自定义字体文件路径，供 matplotlib 使用
_harmonyos_font_file = None  # HarmonyOS Sans Regular 字体文件路径（主字体）
_harmonyos_medium_font_file = None  # HarmonyOS Sans Medium 字体文件路径（用于标题、按钮等）
_inter_font_file = None  # Inter 字体文件路径（用于英文和数字）
_harmonyos_font_file = None  # HarmonyOS Sans 字体文件路径（主字体）

def load_font_to_system(font_path):
    """
    使用 Windows API 临时加载字体到系统（仅 Windows）
    返回是否成功加载
    """
    global WINDOWS_FONT_LOADED
    
    if platform.system() != 'Windows' or not gdi32:
        return False
    
    if WINDOWS_FONT_LOADED:
        return True
    
    try:
        # 使用 AddFontResourceEx 加载字体（FR_PRIVATE 表示仅当前进程可见）
        FR_PRIVATE = 0x10
        result = gdi32.AddFontResourceExW(ctypes.c_wchar_p(font_path), FR_PRIVATE, None)
        if result > 0:
            WINDOWS_FONT_LOADED = True
            # 通知所有窗口字体已更改
            try:
                user32 = ctypes.windll.user32
                HWND_BROADCAST = 0xFFFF
                WM_FONTCHANGE = 0x001D
                user32.SendMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
            except:
                pass
            return True
    except:
        pass
    
    return False

def get_font_family():
    """
    获取主字体族名称（优先使用 HarmonyOS Sans）
    返回字体族名称，用于 Tkinter
    """
    global _harmonyos_font_file, _custom_font_file
    
    # 优先使用 HarmonyOS Sans
    if _harmonyos_font_file and os.path.exists(_harmonyos_font_file):
        try:
            from fontTools.ttLib import TTFont
            font = TTFont(_harmonyos_font_file)
            name_table = font.get('name')
            font_family = None
            # 优先使用 Font Family name (nameID=1)
            for record in name_table.names:
                if record.nameID == 1:  # Font Family name
                    font_family = record.toUnicode()
                    break
            # 如果没有找到，尝试 PostScript name
            if not font_family:
                for record in name_table.names:
                    if record.nameID == 6:  # PostScript name
                        font_family = record.toUnicode()
                        break
            font.close()
            if font_family:
                # 验证字体是否可用
                try:
                    test_font = tkfont.Font(family=font_family, size=10)
                    actual = test_font.actual()
                    if font_family in actual.get('family', '') or actual.get('family', '') in font_family:
                        return font_family
                except:
                    pass
        except:
            pass
    
    # 如果没有 HarmonyOS Sans，使用其他自定义字体
    if _custom_font_file and os.path.exists(_custom_font_file):
        try:
            from fontTools.ttLib import TTFont
            font = TTFont(_custom_font_file)
            name_table = font.get('name')
            font_family = None
            for record in name_table.names:
                if record.nameID == 1:  # Font Family name
                    font_family = record.toUnicode()
                    break
                elif record.nameID == 6 and font_family is None:  # PostScript name
                    font_family = record.toUnicode()
            font.close()
            if font_family:
                return font_family
        except:
            pass
    
    # 如果无法从字体文件获取，使用 GUI_FONT_FAMILY 或安全字体
    if GUI_FONT_FAMILY:
        return GUI_FONT_FAMILY
    return get_safe_font_family()

def get_font_family_medium():
    """
    获取 HarmonyOS Sans Medium 字体族名称（用于标题、按钮等需要加粗的地方）
    返回字体族名称，用于 Tkinter
    """
    global _harmonyos_medium_font_file, _harmonyos_font_file
    
    # 优先使用 HarmonyOS Sans Medium
    if _harmonyos_medium_font_file and os.path.exists(_harmonyos_medium_font_file):
        try:
            from fontTools.ttLib import TTFont
            font = TTFont(_harmonyos_medium_font_file)
            name_table = font.get('name')
            font_family = None
            # 优先使用 Font Family name (nameID=1)
            for record in name_table.names:
                if record.nameID == 1:  # Font Family name
                    font_family = record.toUnicode()
                    break
            # 如果没有找到，尝试 PostScript name
            if not font_family:
                for record in name_table.names:
                    if record.nameID == 6:  # PostScript name
                        font_family = record.toUnicode()
                        break
            font.close()
            if font_family:
                # 验证字体是否可用
                try:
                    test_font = tkfont.Font(family=font_family, size=10)
                    actual = test_font.actual()
                    if font_family in actual.get('family', '') or actual.get('family', '') in font_family:
                        return font_family
                except:
                    pass
        except:
            pass
    
    # 如果 Medium 不可用，返回 Regular（主字体）
    return get_font_family()

def get_font_file():
    """
    获取主字体文件路径（如果存在）
    返回字体文件路径，用于 matplotlib
    """
    global _harmonyos_font_file, _custom_font_file
    # 优先返回 HarmonyOS Sans
    if _harmonyos_font_file and os.path.exists(_harmonyos_font_file):
        return _harmonyos_font_file
    if _custom_font_file and os.path.exists(_custom_font_file):
        return _custom_font_file
    return None

def get_font_file_medium():
    """
    获取 HarmonyOS Sans Medium 字体文件路径（如果存在）
    返回字体文件路径，用于 matplotlib
    """
    global _harmonyos_medium_font_file
    if _harmonyos_medium_font_file and os.path.exists(_harmonyos_medium_font_file):
        return _harmonyos_medium_font_file
    # 如果 Medium 不可用，返回 Regular
    return get_font_file()

def get_safe_font_family(default=None):
    """
    安全地获取可用的字体族名称
    如果指定的字体不存在，会尝试多个备选字体
    """
    system = platform.system()
    
    # 如果提供了默认字体，先尝试使用它
    if default:
        try:
            test_font = tkfont.Font(family=default, size=10)
            actual = test_font.actual()
            # 检查字体是否真的加载成功
            if actual.get('family') == default or default in str(actual.get('family', '')):
                return default
        except:
            pass
    
    # 根据系统尝试不同的字体
    if system == 'Windows':
        # Windows字体列表（按优先级排序）
        font_candidates = [
            'Microsoft YaHei UI',
            'Microsoft YaHei',
            'SimHei',
            'SimSun',
            'Arial Unicode MS',
            'Arial'
        ]
        for font_name in font_candidates:
            try:
                test_font = tkfont.Font(family=font_name, size=10)
                actual = test_font.actual()
                # 检查字体是否真的加载成功
                if actual.get('family') == font_name or font_name.split()[0] in str(actual.get('family', '')):
                    return font_name
            except:
                continue
        # 如果都失败，返回系统默认字体
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
            return default_font.cget("family")
        except:
            return "Arial"
    elif system == 'Darwin':
        # macOS字体列表
        font_candidates = [
            'PingFang SC',
            'STHeiti',
            'Arial Unicode MS',
            'Arial'
        ]
        for font_name in font_candidates:
            try:
                test_font = tkfont.Font(family=font_name, size=10)
                actual = test_font.actual()
                if actual.get('family') == font_name:
                    return font_name
            except:
                continue
        return "Arial"
    else:
        # Linux字体列表
        font_candidates = [
            'WenQuanYi Micro Hei',
            'Noto Sans CJK SC',
            'DejaVu Sans',
            'Arial'
        ]
        for font_name in font_candidates:
            try:
                test_font = tkfont.Font(family=font_name, size=10)
                actual = test_font.actual()
                if actual.get('family') == font_name:
                    return font_name
            except:
                continue
        return "Arial"

def set_window_icon(window):
    """设置窗口图标为Sparrow.png（使用缓存优化性能）"""
    global _app_icon, _cached_pil_image
    try:
        # 获取图标文件路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'Sparrow.png')
        
        if os.path.exists(icon_path):
            # 尝试使用PIL加载PNG图片
            try:
                from PIL import Image, ImageTk
                
                # 如果已有缓存的缩放图像，直接使用（避免重复加载和缩放大文件）
                if _cached_pil_image is None:
                    # 第一次加载：读取并缩放图标
                    pil_image = Image.open(icon_path)
                    # 优化：如果图标太大，先缩放到合适的大小（32x32或64x64）
                    # 窗口图标通常只需要小尺寸，大图标会导致加载缓慢和抖动
                    max_icon_size = 64  # 最大图标尺寸
                    if pil_image.width > max_icon_size or pil_image.height > max_icon_size:
                        # 保持宽高比缩放（使用兼容的重采样方法）
                        try:
                            # PIL 10.0.0+ 使用 Image.Resampling.LANCZOS
                            pil_image.thumbnail((max_icon_size, max_icon_size), Image.Resampling.LANCZOS)
                        except AttributeError:
                            # 旧版本使用 Image.LANCZOS
                            try:
                                pil_image.thumbnail((max_icon_size, max_icon_size), Image.LANCZOS)
                            except AttributeError:
                                # 更旧的版本使用 ANTIALIAS
                                pil_image.thumbnail((max_icon_size, max_icon_size), Image.ANTIALIAS)
                    # 缓存缩放后的PIL图像
                    _cached_pil_image = pil_image
                else:
                    # 使用缓存的图像（避免重复加载和缩放）
                    pil_image = _cached_pil_image
                
                # 为当前窗口创建PhotoImage对象（每个窗口需要自己的PhotoImage）
                icon_image = ImageTk.PhotoImage(pil_image, master=window)
                window.iconphoto(True, icon_image)
                
                # 保持引用，避免被垃圾回收
                if _app_icon is None:
                    _app_icon = []
                # 避免重复添加相同的图标引用
                if icon_image not in _app_icon:
                    _app_icon.append(icon_image)
                return True
            except ImportError:
                # 如果没有PIL，尝试使用PhotoImage（仅支持GIF/PNG，但可能不支持PNG）
                try:
                    from tkinter import PhotoImage
                    icon_image = PhotoImage(file=icon_path, master=window)
                    window.iconphoto(True, icon_image)
                    if _app_icon is None:
                        _app_icon = []
                    if icon_image not in _app_icon:
                        _app_icon.append(icon_image)
                    return True
                except Exception as e:
                    print(f"使用PhotoImage加载图标失败: {e}")
            except Exception as e:
                print(f"使用PIL加载图标失败: {e}")
        
        # 如果PNG加载失败，尝试使用ICO文件
        try:
            # 尝试使用Sparrow.ico（如果存在）
            ico_path = os.path.join(base_path, 'Sparrow.ico')
            if os.path.exists(ico_path):
                window.iconbitmap(ico_path)
                return True
            # 尝试使用app_icon.ico（如果存在）
            ico_path = os.path.join(base_path, 'app_icon.ico')
            if os.path.exists(ico_path):
                window.iconbitmap(ico_path)
                return True
        except Exception as e:
            print(f"使用ICO文件设置图标失败: {e}")
        
        return False
    except Exception as e:
        # 设置图标失败不影响程序运行
        print(f"设置窗口图标失败: {e}")
        return False

def load_ui_font():
    """
    加载用于GUI界面的字体（优先使用项目fonts文件夹中的字体）
    优先查找 HarmonyOS Sans 和 Inter 字体
    返回主字体文件路径
    """
    global _harmonyos_font_file, _inter_font_file
    
    # 获取字体文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 优先使用项目fonts文件夹中的字体文件
    fonts_dir = os.path.join(base_path, 'fonts')
    if os.path.exists(fonts_dir):
        # 优先查找 HarmonyOS Sans Regular 和 Medium
        harmonyos_regular = None
        harmonyos_medium = None
        
        for ext in ['.ttf', '.otf', '.ttc']:
            for file in os.listdir(fonts_dir):
                if file.lower().endswith(ext):
                    font_path = os.path.join(fonts_dir, file)
                    if os.path.isfile(font_path):
                        file_lower = file.lower()
                        # 查找 HarmonyOS Sans Regular
                        if 'harmonyos' in file_lower and 'sans' in file_lower:
                            if 'regular' in file_lower and not harmonyos_regular:
                                harmonyos_regular = font_path
                            elif 'medium' in file_lower and not harmonyos_medium:
                                harmonyos_medium = font_path
                            # 如果没有明确标注 Regular，但也没有标注其他字重，可能是 Regular
                            elif not harmonyos_regular and 'medium' not in file_lower and 'bold' not in file_lower:
                                harmonyos_regular = font_path
        
        # 如果找到 HarmonyOS Sans Regular，使用它作为主字体
        if harmonyos_regular:
            _harmonyos_font_file = harmonyos_regular
            # 尝试使用 Windows API 加载字体（仅 Windows）
            if platform.system() == 'Windows':
                load_font_to_system(harmonyos_regular)
        
        # 如果找到 HarmonyOS Sans Medium，保存路径
        if harmonyos_medium:
            _harmonyos_medium_font_file = harmonyos_medium
            # 尝试使用 Windows API 加载字体（仅 Windows）
            if platform.system() == 'Windows':
                load_font_to_system(harmonyos_medium)
        
        # 返回主字体文件路径（Regular）
        if harmonyos_regular:
            return harmonyos_regular
        
        # 如果没有找到 HarmonyOS Sans，查找其他字体文件
        font_files = []
        for ext in ['.ttf', '.otf', '.ttc']:
            for file in os.listdir(fonts_dir):
                if file.lower().endswith(ext):
                    font_path = os.path.join(fonts_dir, file)
                    if os.path.isfile(font_path):
                        font_files.append(font_path)
        
        # 如果找到字体文件，尝试加载到系统并返回路径
        if font_files:
            font_files.sort()
            font_path = font_files[0]
            # 尝试使用 Windows API 加载字体（仅 Windows）
            if platform.system() == 'Windows':
                load_font_to_system(font_path)
            return font_path
    
    # 如果没有找到项目字体，回退到系统字体
    return get_safe_font_family()


def setup_modern_style(root):
    """设置现代化的界面样式（使用ttkbootstrap如果可用）"""
    global _custom_font_file, _harmonyos_font_file
    
    # 获取字体（会加载 HarmonyOS Sans 和 Inter）
    ui_font_path = load_ui_font()
    
    # 更新 _custom_font_file 为主字体（用于向后兼容）
    if _harmonyos_font_file:
        _custom_font_file = _harmonyos_font_file
    elif ui_font_path and os.path.exists(ui_font_path):
        _custom_font_file = ui_font_path
    
    # 如果返回的是字体文件路径，尝试从字体文件获取字体名称
    font_family = None
    if os.path.exists(ui_font_path):
        # 如果是字体文件路径，尝试读取字体信息获取字体名称
        try:
            # 方法1: 使用 fontTools 读取字体信息（如果可用）
            try:
                from fontTools.ttLib import TTFont
                font = TTFont(ui_font_path)
                name_table = font.get('name')
                for record in name_table.names:
                    if record.nameID == 6:  # PostScript name
                        font_family = record.toUnicode()
                        break
                    elif record.nameID == 1 and font_family is None:  # Font Family name
                        font_family = record.toUnicode()
                font.close()
            except (ImportError, Exception):
                # 如果没有 fontTools，无法从字体文件获取字体名称
                pass
            
            # 如果无法从字体文件获取字体名称，回退到系统字体
            if not font_family:
                font_family = get_safe_font_family()
            # 确保保存字体文件路径（无论是否成功获取字体名称）
            _custom_font_file = ui_font_path
        except:
            # 如果加载字体失败，回退到系统字体，但仍保存字体文件路径供 matplotlib 使用
            _custom_font_file = ui_font_path
            font_family = get_safe_font_family()
    else:
        # 使用系统字体名称，但需要验证字体是否存在
        font_family = get_safe_font_family(default=ui_font_path)
    
    # 如果ttkbootstrap可用，使用它
    if TTKBOOTSTRAP_AVAILABLE and ttkb:
        try:
            # 推荐主题：'cosmo', 'flatly', 'litera', 'minty', 'pulse', 'sandstone', 'united'
            theme_name = 'flatly'  # 扁平风格主题
            
            # 如果root是ttkbootstrap Window，确保主题已设置
            if hasattr(root, 'style'):
                # ttkbootstrap Window已经有style属性，确保主题正确
                try:
                    root.style.theme_use(theme_name)
                except:
                    pass
            else:
                # 如果不是ttkbootstrap Window，创建Style对象
                style = ttkb.Style(theme=theme_name)
        except Exception as e:
            print(f"使用ttkbootstrap主题失败: {e}，回退到传统样式")
            # 回退到传统样式
            style = ttk.Style()
            if system == 'Windows':
                try:
                    style.theme_use('vista')
                except:
                    style.theme_use('clam')
            else:
                style.theme_use('clam')
    else:
        # 使用传统ttk样式
        style = ttk.Style()
        if system == 'Windows':
            try:
                style.theme_use('vista')
            except:
                style.theme_use('clam')
        else:
            style.theme_use('clam')
    
    # 配置默认字体（无论是否使用ttkbootstrap都需要）
    # 这会影响所有 tk.Label, tk.Entry, tk.Text 等组件的默认字体
    try:
        # 使用字体名称配置所有默认字体（Tkinter 不支持直接从文件加载）
        # font_family 已经是从字体文件获取的字体名称，或回退的系统字体
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=font_family, size=10)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=font_family, size=10)
        
        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family=font_family, size=10)
        
        # 配置菜单字体
        try:
            tkfont.nametofont("TkMenuFont").configure(family=font_family, size=10)
        except:
            pass
    except Exception as e:
        print(f"配置默认字体失败: {e}")
    
    # 获取 Medium 字体（用于按钮、标题等）
    font_family_medium = get_font_family_medium()
    
    # 配置 ttk 样式（无论是否使用ttkbootstrap都需要配置字体）
    # 如果使用ttkbootstrap，也需要配置字体
    if TTKBOOTSTRAP_AVAILABLE and ttkb:
        # ttkbootstrap 使用 style 对象
        try:
            if hasattr(root, 'style'):
                root_style = root.style
            else:
                root_style = ttkb.Style()
            
            # 配置所有 ttk 组件的字体（按钮使用 Medium）
            try:
                root_style.configure('TButton', font=(font_family_medium, 10))
            except:
                pass
            try:
                root_style.configure('TEntry', font=(font_family, 10))
            except:
                pass
            try:
                root_style.configure('TLabel', font=(font_family, 10))
            except:
                pass
            try:
                root_style.configure('TRadiobutton', font=(font_family, 10))
            except:
                pass
            try:
                root_style.configure('TCheckbutton', font=(font_family, 10))
            except:
                pass
        except Exception as e:
            # ttkbootstrap 字体配置失败不影响程序运行
            pass
    
    # 如果未使用ttkbootstrap，配置传统样式
    if not TTKBOOTSTRAP_AVAILABLE or not ttkb:
        # 配置按钮样式（现代化扁平风格）
        try:
            style.configure('TButton',
                           font=(font_family, 10),
                           padding=(12, 6),
                           relief='flat',
                           borderwidth=1)
            
            style.map('TButton',
                     background=[('active', '#e8e8e8'), ('!disabled', '#f0f0f0'), ('pressed', '#d0d0d0')],
                     foreground=[('active', '#000000'), ('!disabled', '#000000')],
                     bordercolor=[('focus', '#0078d4'), ('!focus', '#d0d0d0')])
        except Exception as e:
            print(f"配置按钮样式失败: {e}")
        
        # 配置输入框样式
        try:
            style.configure('TEntry',
                           font=(font_family, 10),
                           fieldbackground='white',
                           borderwidth=1,
                           relief='solid',
                           padding=4,
                           bordercolor='#d0d0d0')
            
            style.map('TEntry',
                     fieldbackground=[('focus', '#ffffff'), ('!focus', '#ffffff')],
                     bordercolor=[('focus', '#0078d4'), ('!focus', '#d0d0d0')])
        except Exception as e:
            print(f"配置输入框样式失败: {e}")
        
        # 配置标签样式
        try:
            style.configure('TLabel',
                           font=(font_family, 10),
                           background='white',
                           foreground='#333333')
        except Exception as e:
            print(f"配置标签样式失败: {e}")
        
        # 配置单选按钮样式
        try:
            style.configure('TRadiobutton',
                           font=(font_family, 10),
                           background='white',
                           foreground='#333333')
        except Exception as e:
            print(f"配置单选按钮样式失败: {e}")
        
        # 配置菜单样式
        try:
            style.configure('TMenu',
                           font=(font_family, 10))
        except Exception as e:
            print(f"配置菜单样式失败: {e}")
    
    # 配置主窗口背景
    try:
        if not TTKBOOTSTRAP_AVAILABLE or not hasattr(root, 'style'):
            root.configure(bg='#f5f5f5')
    except:
        pass
    
    # 更新全局字体变量（确保使用安全的字体）
    global GUI_FONT_FAMILY
    # 确保 font_family 是安全的（如果之前获取的字体可能不存在，重新获取一次）
    GUI_FONT_FAMILY = get_safe_font_family(default=font_family)
    
    # 强制更新所有已创建的字体对象（确保所有组件使用新字体）
    try:
        # 更新所有命名字体
        for font_name in ["TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"]:
            try:
                named_font = tkfont.nametofont(font_name)
                if _custom_font_file and os.path.exists(_custom_font_file):
                    try:
                        # 使用已加载的字体名称（字体已通过 Windows API 加载）
                        named_font.configure(family=GUI_FONT_FAMILY)
                    except:
                        named_font.configure(family=GUI_FONT_FAMILY)
                else:
                    named_font.configure(family=GUI_FONT_FAMILY)
            except:
                pass
    except:
        pass
    
    return GUI_FONT_FAMILY

def find_chinese_font():
    """查找系统中可用的中文字体"""
    system = platform.system()
    
    # Windows 系统
    if system == 'Windows':
        font_paths = [
            r'C:\Windows\Fonts\simhei.ttf',  # 黑体
            r'C:\Windows\Fonts\simsun.ttc',   # 宋体
            r'C:\Windows\Fonts\msyh.ttc',    # 微软雅黑
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    
    # macOS 系统
    elif system == 'Darwin':
        font_paths = [
            '/System/Library/Fonts/STHeiti Light.ttc',  # 黑体-简
            '/System/Library/Fonts/STHeiti Medium.ttc',  # 黑体-繁
            '/System/Library/Fonts/STSong.ttc',          # 宋体
            '/System/Library/Fonts/Supplemental/Songti.ttc',  # 宋体
            '/Library/Fonts/Arial Unicode.ttf',         # Arial Unicode
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    
    # Linux 系统
    elif system == 'Linux':
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # 文泉驿微米黑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',    # 文泉驿正黑
            '/usr/share/fonts/truetype/arphic/uming.ttc',      # AR PL UMing
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
    
    # 如果找不到，尝试使用 matplotlib 的字体管理器查找
    try:
        fonts = [f.name for f in fm.fontManager.ttflist if 'hei' in f.name.lower() or 'song' in f.name.lower() or 'sim' in f.name.lower()]
        if fonts:
            # 返回第一个找到的字体名称，让 matplotlib 自动查找
            return fonts[0]
    except:
        pass
    
    # 如果都找不到，返回 None，使用默认字体
    return None

# 获取字体路径或名称（用于matplotlib绘图）
font_path = find_chinese_font()
if font_path and os.path.exists(font_path):
    font = fm.FontProperties(fname=font_path, size=12)
elif font_path:
    # 如果是字体名称而不是路径
    font = fm.FontProperties(family=font_path, size=12)
else:
    # 使用默认字体
    font = fm.FontProperties(size=12)

def adjust_window_size(window, keep_position=False):
    """调整窗口大小以适应内容，并居中显示（如果 keep_position=True，则保持当前位置）"""
    # 更新窗口以确保正确计算大小
    window.update_idletasks()
    window.update()
    
    # 如果保持位置，先获取当前位置
    if keep_position:
        try:
            current_geometry = window.geometry()
            # 解析当前位置：widthxheight+x+y
            if '+' in current_geometry:
                parts = current_geometry.split('+')
                current_x = int(parts[1])
                current_y = int(parts[2])
            else:
                current_x = None
                current_y = None
        except:
            current_x = None
            current_y = None
    else:
        current_x = None
        current_y = None
    
    # 计算窗口所需的最小尺寸（基于内容大小）
    req_width = window.winfo_reqwidth()
    req_height = window.winfo_reqheight()
    
    # 如果请求的尺寸无效，使用实际尺寸
    if req_width <= 1:
        req_width = window.winfo_width()
    if req_height <= 1:
        req_height = window.winfo_height()
    
    # 如果还是无效，再等待一次并重新获取
    if req_width <= 1 or req_height <= 1:
        window.update_idletasks()
        window.update()
        req_width = max(window.winfo_reqwidth(), window.winfo_width())
        req_height = max(window.winfo_reqheight(), window.winfo_height())
    
    # 添加边距（左右各20像素，上下各20像素）
    padding = 40
    req_width += padding
    req_height += padding
    
    # 获取屏幕尺寸，确保窗口不超出屏幕
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # 限制窗口大小不超过屏幕（留出一些边距）
    max_width = screen_width - 40
    max_height = screen_height - 40
    req_width = min(req_width, max_width)
    req_height = min(req_height, max_height)
    
    # 确保最小尺寸
    req_width = max(req_width, 400)
    req_height = max(req_height, 300)
    
    # 计算位置
    if keep_position and current_x is not None and current_y is not None:
        # 保持当前位置，只调整大小
        x = current_x
        y = current_y
    else:
        # 居中显示
        x = (screen_width - req_width) // 2
        y = (screen_height - req_height) // 2
    
    # 确保窗口不会超出屏幕边界
    x = max(0, min(x, screen_width - req_width))
    y = max(0, min(y, screen_height - req_height))
    
    # 设置窗口geometry
    window.geometry(f"{req_width}x{req_height}+{x}+{y}")
    window.update_idletasks()


def center_window(window):
    """将窗口居中显示在当前显示器上"""
    try:
        # 更新窗口以确保正确计算大小
        window.update_idletasks()
        window.update()
        
        # 获取窗口大小（优先使用请求大小，因为窗口可能还在隐藏状态）
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        
        # 如果请求大小为0或太小，尝试获取实际大小
        if width <= 1 or height <= 1:
            width = window.winfo_width()
            height = window.winfo_height()
        
        # 如果仍然太小，使用默认大小
        if width < 200:
            width = 400
        if height < 200:
            height = 300
        
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        
        # 设置窗口位置和大小（如果大小有效）
        if width > 1 and height > 1:
            window.geometry(f'{width}x{height}+{x}+{y}')
        else:
            # 如果大小仍然无效，只设置位置，让窗口自动调整大小
            window.geometry(f'+{x}+{y}')
    except Exception as e:
        # 如果居中失败，至少确保窗口在可见位置
        try:
            window.geometry('400x300+100+100')
        except:
            pass

def create_window(themename='flatly'):
    """
    创建窗口（使用ttkbootstrap如果可用，否则使用tk.Tk）
    themename: ttkbootstrap主题名称（仅在ttkbootstrap可用时有效）
    """
    if TTKBOOTSTRAP_AVAILABLE and ttkb:
        try:
            window = ttkb.Window(themename=themename)
            # 确保主题已应用
            if hasattr(window, 'style'):
                window.style.theme_use(themename)
            return window
        except Exception as e:
            print(f"使用ttkbootstrap.Window失败: {e}，回退到tk.Tk")
            return tk.Tk()
    else:
        return tk.Tk()

def create_toplevel(parent=None, themename='flatly'):
    """
    创建Toplevel窗口（使用ttkbootstrap如果可用，否则使用tk.Toplevel）
    parent: 父窗口（可以为None）
    themename: ttkbootstrap主题名称（仅在ttkbootstrap可用时有效）
    """
    if TTKBOOTSTRAP_AVAILABLE and ttkb:
        try:
            if parent:
                toplevel = ttkb.Toplevel(parent)
                # 确保主题正确应用（ttkbootstrap Toplevel会自动继承父窗口主题，但为了保险起见）
                if hasattr(toplevel, 'style') and hasattr(parent, 'style'):
                    try:
                        # 从父窗口获取主题
                        parent_theme = parent.style.theme.name if hasattr(parent.style.theme, 'name') else themename
                        toplevel.style.theme_use(parent_theme)
                    except:
                        pass
                return toplevel
            else:
                # 如果没有父窗口，尝试创建一个独立的窗口
                # ttkbootstrap的Toplevel需要父窗口，如果没有则回退到tk.Toplevel
                return tk.Toplevel()
        except Exception as e:
            print(f"使用ttkbootstrap.Toplevel失败: {e}，回退到tk.Toplevel")
            if parent:
                return tk.Toplevel(parent)
            else:
                return tk.Toplevel()
    else:
        if parent:
            return tk.Toplevel(parent)
        else:
            return tk.Toplevel()

