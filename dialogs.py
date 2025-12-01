# -*- coding: utf-8 -*-
"""对话框模块"""
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
_about_dialog_instance = None


def _canvas_create_rounded_rectangle(self, x1, y1, x2, y2, radius=16, **kwargs):
    """在 Canvas 上绘制圆角矩形"""
    # 确保坐标顺序正确
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    # 限制圆角半径不超过宽高的一半
    radius = max(0, min(radius, (x2 - x1) // 2, (y2 - y1) // 2))
    # 使用多边形 + smooth 实现圆角效果
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return self.create_polygon(points, **kwargs, smooth=True)


if not hasattr(tk.Canvas, "create_rounded_rectangle"):
    tk.Canvas.create_rounded_rectangle = _canvas_create_rounded_rectangle

# 延迟导入模块，避免循环依赖
def t(key, **kwargs):
    """翻译函数（延迟导入i18n）"""
    try:
        import i18n
        return i18n.t(key, **kwargs)
    except:
        return key

def get_ui_utils():
    """获取ui_utils模块的函数"""
    try:
        import ui_utils
        return {
            'create_window': ui_utils.create_window,
            'create_toplevel': ui_utils.create_toplevel,
            'set_window_icon': ui_utils.set_window_icon,
            'setup_modern_style': ui_utils.setup_modern_style,
            'center_window': ui_utils.center_window,
            'adjust_window_size': ui_utils.adjust_window_size,
            'GUI_FONT_FAMILY': getattr(ui_utils, 'GUI_FONT_FAMILY', None)
        }
    except:
        def create_window(): return tk.Tk()
        def create_toplevel(p): return tk.Toplevel(p) if p else tk.Toplevel()
        def set_window_icon(w): pass
        def setup_modern_style(w): return None
        def center_window(w): pass
        def adjust_window_size(w): pass
        return {
            'create_window': create_window,
            'create_toplevel': create_toplevel,
            'set_window_icon': set_window_icon,
            'setup_modern_style': setup_modern_style,
            'center_window': center_window,
            'adjust_window_size': adjust_window_size,
            'GUI_FONT_FAMILY': None
        }

def get_i18n():
    """获取i18n模块的变量和函数"""
    try:
        import i18n
        return {
            'CURRENT_LANGUAGE': i18n.CURRENT_LANGUAGE,
            '_ui_components': i18n._ui_components,
            'set_language': i18n.set_language,
            'update_ui_language': i18n.update_ui_language
        }
    except:
        def set_language(c): return False
        def update_ui_language(): pass
        return {
            'CURRENT_LANGUAGE': 'zh_CN',
            '_ui_components': {'table': None, 'root': None},
            'set_language': set_language,
            'update_ui_language': update_ui_language
        }

def select_intersection_type():
    """选择交叉口类型或读取文件"""
    # 获取ui工具函数
    ui_utils_funcs = get_ui_utils()
    create_window = ui_utils_funcs['create_window']
    set_window_icon = ui_utils_funcs['set_window_icon']
    setup_modern_style = ui_utils_funcs['setup_modern_style']
    center_window = ui_utils_funcs['center_window']
    adjust_window_size = ui_utils_funcs['adjust_window_size']
    GUI_FONT_FAMILY = ui_utils_funcs['GUI_FONT_FAMILY']
    
    # 获取i18n变量和函数
    i18n_vars = get_i18n()
    CURRENT_LANGUAGE = i18n_vars['CURRENT_LANGUAGE']
    _ui_components = i18n_vars['_ui_components']
    set_language = i18n_vars['set_language']
    update_ui_language = i18n_vars['update_ui_language']
    
    # 直接创建一个独立的对话框窗口
    dialog = create_window()
    dialog.title(t('select_intersection_type'))
    # 设置窗口图标
    set_window_icon(dialog)
    dialog.resizable(False, False)
    # 启动界面使用无标题窗口样式（无系统标题栏）
    try:
        dialog.overrideredirect(True)
    except:
        pass
    
    # 立即隐藏窗口，避免闪现
    dialog.withdraw()
    
    # 先设置一个临时位置（屏幕外），避免在左上角闪现
    dialog.geometry("1x1+-10000+-10000")
    
    # 为对话框也应用字体设置（确保 ttk 组件也使用项目字体）
    setup_modern_style(dialog)
    
    # 确保对话框中的 ttk 组件也使用项目字体
    try:
        import ui_utils
        dialog_font_family = ui_utils.get_font_family()
        # 获取 Medium 字体（用于按钮）
        try:
            dialog_font_family_medium = ui_utils.get_font_family_medium()
        except:
            dialog_font_family_medium = dialog_font_family
        # 配置对话框的 ttk 样式
        dialog_style = ttk.Style(dialog)
        dialog_style.configure('TButton', font=(dialog_font_family, 10))
        dialog_style.configure('TEntry', font=(dialog_font_family, 10))
        dialog_style.configure('TLabel', font=(dialog_font_family, 10))
        dialog_style.configure('TRadiobutton', font=(dialog_font_family, 10))
        dialog_style.configure('TCheckbutton', font=(dialog_font_family, 10))
        # 启动界面主按钮样式：大号圆角矩形按钮
        dialog_style.configure(
            'StartMain.TButton',
            font=(dialog_font_family_medium, 12),
            padding=(24, 14)
        )
        
        # 强制更新对话框的默认字体
        try:
            from tkinter import font as tkfont
            if ui_utils._custom_font_file and os.path.exists(ui_utils._custom_font_file):
                try:
                    default_font = tkfont.Font(file=ui_utils._custom_font_file, size=10)
                    tkfont.nametofont("TkDefaultFont").configure(family=default_font.actual()['family'], size=10)
                except:
                    tkfont.nametofont("TkDefaultFont").configure(family=dialog_font_family, size=10)
            else:
                tkfont.nametofont("TkDefaultFont").configure(family=dialog_font_family, size=10)
        except:
            pass
    except:
        pass
    
    result = {'choice': None}
    
    def on_choice(choice):
        result['choice'] = choice
        dialog.quit()
        dialog.destroy()
    
    def on_close():
        try:
            result['choice'] = None
            dialog.quit()
            dialog.destroy()
        except:
            pass
        finally:
            # 确保进程完全退出
            os._exit(0)
    
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    # 设置对话框背景
    dialog.configure(bg='#f5f5f5')
    
    # 存储界面组件引用，用于更新
    dialog_components = {
        'title_label': None,
        'btn1': None,
        'btn2': None,
        'btn3': None,
        'btn4': None,
        'btn5': None,
        'toolbar': None,
        'help_btn': None,
        'about_btn': None,
    }
    
    def change_dialog_language(lang_code):
        """切换对话框语言（全局生效）"""
        if set_language(lang_code):
            update_dialog_language()
            # 重新调整对话框大小以适应新的文本长度
            dialog.update_idletasks()
            center_window(dialog)
            # 同时更新主界面（如果已创建）
            if _ui_components.get('root'):
                update_ui_language()
                root = _ui_components.get('root')
                if root:
                    adjust_window_size(root)
            return True
        return False
    
    # 创建顶层容器（包含自定义标题栏和内容区域）
    root_frame = tk.Frame(dialog, bg='#f5f5f5', bd=0, highlightthickness=0)
    root_frame.pack(fill='both', expand=True)
    
    # 自定义标题栏（支持拖动和关闭）
    title_bar_height = 40
    # 颜色与主窗口保持一致（浅灰背景）
    TITLE_BG = '#f5f5f5'
    TITLE_HOVER_CLOSE = '#e0e0e0'
    TITLE_CLOSE_FG = '#333333'
    
    title_bar = tk.Frame(root_frame, bg=TITLE_BG, height=title_bar_height, bd=0, highlightthickness=0)
    title_bar.pack(fill='x', side='top')
    title_bar.pack_propagate(False)
    
    # 标题栏文字去掉，仅保留可拖动区域
    title_text_widget = tk.Label(
        title_bar,
        text='',
        bg=TITLE_BG,
        fg=TITLE_CLOSE_FG,
        padx=8
    )
    title_text_widget.pack(side='left', fill='y')
    
    # 关闭按钮
    close_btn_frame = tk.Frame(title_bar, bg=TITLE_BG, width=40, height=title_bar_height, bd=0, highlightthickness=0)
    close_btn_frame.pack(side='right')
    close_btn_frame.pack_propagate(False)
    
    close_btn = tk.Label(
        close_btn_frame,
        text='✕',
        bg=TITLE_BG,
        fg=TITLE_CLOSE_FG,
        font=('Arial', 13),
        cursor='hand2'
    )
    close_btn.pack(expand=True, fill='both')
    
    def on_close_click(event=None):
        on_close()
    
    def on_close_enter(event=None):
        close_btn.config(bg=TITLE_HOVER_CLOSE)
        close_btn_frame.config(bg=TITLE_HOVER_CLOSE)
    
    def on_close_leave(event=None):
        close_btn.config(bg=TITLE_BG)
        close_btn_frame.config(bg=TITLE_BG)
    
    close_btn.bind('<Button-1>', on_close_click)
    close_btn_frame.bind('<Button-1>', on_close_click)
    close_btn.bind('<Enter>', on_close_enter)
    close_btn.bind('<Leave>', on_close_leave)
    close_btn_frame.bind('<Enter>', on_close_enter)
    close_btn_frame.bind('<Leave>', on_close_leave)
    
    # 窗口拖动
    def start_drag(event):
        dialog._drag_start_x = event.x
        dialog._drag_start_y = event.y
    
    def on_drag(event):
        try:
            x = dialog.winfo_x() + event.x - dialog._drag_start_x
            y = dialog.winfo_y() + event.y - dialog._drag_start_y
            dialog.geometry(f"+{x}+{y}")
        except Exception:
            pass
    
    title_bar.bind('<Button-1>', start_drag)
    title_bar.bind('<B1-Motion>', on_drag)
    title_text_widget.bind('<Button-1>', start_drag)
    title_text_widget.bind('<B1-Motion>', on_drag)
    
    # 创建主内容框架
    main_frame = tk.Frame(root_frame, padx=40, pady=40, bg='white', relief='flat')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 获取字体族（优先使用项目字体文件）
    try:
        import ui_utils
        font_family = ui_utils.get_font_family()
    except:
        font_family = 'Arial'
    
    # 标题
    # 获取 Medium 字体（用于标题）
    try:
        import ui_utils
        title_font_family = ui_utils.get_font_family_medium()
    except:
        title_font_family = font_family
    
    title_label = tk.Label(
        main_frame,
        text=t('select_intersection_type'),
        font=(title_font_family, 14),
        pady=20,
        bg='white',
        fg='#333333'
    )
    title_label.pack()
    dialog_components['title_label'] = title_label
    
    # 按钮框架（限制宽度，让启动界面更紧凑）
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=(10, 0))
    
    # 圆角主按钮：使用 Canvas 绘制（使用与主窗口视觉一致的深蓝主按钮配色）
    try:
        import ui_utils
        main_btn_font = ui_utils.get_font_family_medium()
    except:
        main_btn_font = 'Arial'
    
    # 统一按钮宽度设置
    MAIN_BTN_WIDTH = 260
    HELP_BTN_GAP = 12
    HELP_BTN_WIDTH = (MAIN_BTN_WIDTH - HELP_BTN_GAP) // 2
    
    # 深蓝主按钮配色（与主窗口底部按钮保持统一）
    BASE_BG = '#2C3E50'     # 默认背景
    HOVER_BG = '#34495E'    # 悬停背景
    FG_COLOR = '#FFFFFF'    # 文本颜色
    BORDER_COLOR = '#2C3E50'  # 边框颜色，与背景一致
    
    def create_rounded_button(parent, text, command, height=48, radius=0,
                              bg_color=BASE_BG, hover_color=HOVER_BG,
                              text_color=FG_COLOR, border_color=BORDER_COLOR,
                              width=None):
        if width is None:
            width = MAIN_BTN_WIDTH
        canvas = tk.Canvas(
            parent,
            height=height,
            width=width,
            bg='white',
            highlightthickness=0,
            bd=0,
            relief='flat',
            cursor='hand2'
        )
        
        def _draw(color):
            canvas.delete('all')
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w <= 1:
                w = width
            if h <= 1:
                h = height
            # 使用直角矩形，与主窗口按钮风格保持一致
            canvas.create_rectangle(
                0, 0, w, h,
                fill=color,
                outline=border_color,
                width=1
            )
            canvas.create_text(
                w // 2,
                h // 2,
                text=text,
                fill=text_color,
                font=(main_btn_font, 12),
                tags='btn_text'
            )
        
        def on_enter(event=None):
            _draw(hover_color)
        
        def on_leave(event=None):
            _draw(bg_color)
        
        def on_click(event=None):
            command()
        
        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        canvas.bind('<Configure>', lambda e: _draw(bg_color))
        # 初始绘制
        canvas.after(10, lambda: _draw(bg_color))
        return canvas
    
    btn1 = create_rounded_button(button_frame, t('btn_3way'), lambda: on_choice(3), width=MAIN_BTN_WIDTH)
    btn1.pack(pady=8)
    dialog_components['btn1'] = btn1
    
    btn2 = create_rounded_button(button_frame, t('btn_4way'), lambda: on_choice(4), width=MAIN_BTN_WIDTH)
    btn2.pack(pady=8)
    dialog_components['btn2'] = btn2
    
    btn3 = create_rounded_button(button_frame, t('btn_5way'), lambda: on_choice(5), width=MAIN_BTN_WIDTH)
    btn3.pack(pady=8)
    dialog_components['btn3'] = btn3
    
    btn4 = create_rounded_button(button_frame, t('btn_6way'), lambda: on_choice(6), width=MAIN_BTN_WIDTH)
    btn4.pack(pady=8)
    dialog_components['btn4'] = btn4
    
    btn5 = create_rounded_button(button_frame, t('btn_load_file'), lambda: on_choice('load_file'), width=MAIN_BTN_WIDTH)
    btn5.pack(pady=8)
    dialog_components['btn5'] = btn5
    
    # 分隔线框架（帮助和关于按钮与其他按钮隔离）
    separator_frame = tk.Frame(main_frame, bg='white', height=20)
    separator_frame.pack()
    
    # 帮助和关于按钮框架
    help_about_frame = tk.Frame(main_frame, bg='white')
    help_about_frame.pack(pady=(10, 0))
    dialog_components['toolbar'] = help_about_frame
    
    # 使用同样的圆角按钮样式创建「帮助」和「关于」按钮
    # 帮助 / 关于按钮与主按钮同高，宽度各占一半，中间留空
    help_btn = create_rounded_button(
        help_about_frame,
        t('btn_help'),
        show_help,
        height=48,
        radius=12,
        width=HELP_BTN_WIDTH
    )
    help_btn.pack(side=tk.LEFT, padx=(0, HELP_BTN_GAP // 2), pady=4)
    dialog_components['help_btn'] = help_btn
    
    # 关于按钮（启动界面采用消息框方式，避免不可见模态窗口残留）
    def show_about_wrapper():
        """包装show_about函数，添加错误处理"""
        try:
            # 检查 dialog 是否存在
            dialog_exists = False
            dialog_viewable = False
            if dialog:
                try:
                    dialog_exists = dialog.winfo_exists()
                except:
                    pass
                
                if dialog_exists:
                    try:
                        dialog_viewable = dialog.winfo_viewable()
                    except:
                        pass
            
            # 确保 dialog 可见且有效
            if dialog and dialog_exists:
                try:
                    # 确保 dialog 可见
                    if not dialog_viewable:
                        dialog.deiconify()
                        dialog.lift()
                        dialog.update()
                except:
                    pass
                
                # 调用 show_about，传入 dialog 作为父窗口
                try:
                    show_about(dialog)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise
            else:
                # 如果 dialog 不存在，使用 messagebox 作为后备
                show_about_simple()
        except Exception as e:
            try:
                # 如果出错，尝试显示简单的关于信息
                show_about_simple()
            except:
                try:
                    messagebox.showerror("错误", f"显示关于对话框时出错: {str(e)}")
                except:
                    pass
    
    def show_about_simple():
        """显示简单的关于信息（使用 messagebox）"""
        try:
            # 获取i18n变量
            i18n_vars = get_i18n()
            CURRENT_LANGUAGE = i18n_vars['CURRENT_LANGUAGE']
            
            # 检查更新检查模块是否可用
            try:
                import update_checker
                UPDATE_CHECKER_AVAILABLE = True
                get_current_version = update_checker.get_current_version
            except ImportError:
                UPDATE_CHECKER_AVAILABLE = False
                def get_current_version(): return None
            
            # 获取版本号
            version_info = ""
            if UPDATE_CHECKER_AVAILABLE:
                try:
                    current_version = get_current_version()
                    if current_version:
                        if CURRENT_LANGUAGE == 'zh_CN':
                            version_info = f"版本号：{current_version}\n\n"
                        else:
                            version_info = f"Version: {current_version}\n\n"
                except:
                    pass
            
            # 获取翻译函数
            t = i18n_vars.get('t', lambda x: x)
            
            if CURRENT_LANGUAGE == 'zh_CN':
                about_text = f"交叉口交通流量流向可视化工具\nIntersection Traffic Flow Visualize\n\n{version_info}版权所有 (C) \n\n本软件由 [江浦马保国] 开发，保留所有权利。\n欢迎复制、传播本软件。\n\nGitee 仓库：\nhttps://gitee.com/Chris_KLP/intersection-traffic-flow\n\nGitHub 仓库：\nhttps://github.com/chrisKLP-sys/intersection-traffic-flow"
            else:
                about_text = f"Intersection Traffic Flow Visualization Tool\n\n{version_info}Copyright (C) \n\nThis software is developed by [江浦马保国], all rights reserved.\nYou are welcome to copy and distribute this software.\n\nGitee Repository:\nhttps://gitee.com/Chris_KLP/intersection-traffic-flow\n\nGitHub Repository:\nhttps://github.com/chrisKLP-sys/intersection-traffic-flow"
            
            messagebox.showinfo(t('about'), about_text)
        except Exception as e:
            try:
                messagebox.showinfo("关于", "交叉口交通流量流向可视化工具\nIntersection Traffic Flow Visualization Tool")
            except:
                pass
    
    about_btn = create_rounded_button(
        help_about_frame,
        t('btn_about'),
        show_about_wrapper,
        height=48,
        radius=12,
        width=HELP_BTN_WIDTH
    )
    about_btn.pack(side=tk.LEFT, padx=(HELP_BTN_GAP // 2, 0), pady=4)
    dialog_components['about_btn'] = about_btn
    
    # 更新窗口以确保正确计算大小
    dialog.update_idletasks()
    dialog.update()
    
    # 在隐藏状态下设置居中位置
    center_window(dialog)
    
    # 再次更新以确保位置已设置
    dialog.update_idletasks()
    dialog.update()
    
    # 显示窗口（此时已经在正确位置了）
    dialog.deiconify()
    
    # 确保窗口在最前面（不使用topmost，避免闪烁）
    dialog.lift()
    dialog.focus_force()
    
    # 最后更新一次，确保窗口完全显示
    dialog.update()
    
    # 等待用户选择
    dialog.mainloop()
    
    return result['choice']


def show_donate_qrcode(parent=None):
    """显示打赏二维码窗口"""
    try:
        # 获取ui工具函数
        ui_utils_funcs = get_ui_utils()
        create_toplevel = ui_utils_funcs['create_toplevel']
        set_window_icon = ui_utils_funcs['set_window_icon']
        GUI_FONT_FAMILY = ui_utils_funcs['GUI_FONT_FAMILY']
        
        # 获取i18n变量
        i18n_vars = get_i18n()
        CURRENT_LANGUAGE = i18n_vars['CURRENT_LANGUAGE']
        _ui_components = i18n_vars['_ui_components']
        
        # 创建新窗口
        if not parent:
            parent = _ui_components.get('root')
        parent_window = parent if parent else tk._default_root
        
        if not parent_window:
            # 如果找不到父窗口，显示错误消息
            messagebox.showerror("错误", "无法找到父窗口")
            return
        
        donate_window = create_toplevel(parent_window)
        donate_window.title(t('donate_title'))
        # 设置窗口图标
        set_window_icon(donate_window)
        donate_window.resizable(False, False)
        
        # 立即隐藏对话框，避免在左上角闪现
        donate_window.withdraw()
        # 注意：transient 和 grab_set 在计算完尺寸后设置
        
        # 获取二维码图片路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        qrcode_path = os.path.join(base_path, 'qrcode.jpg')
        
        # 主容器
        main_frame = tk.Frame(donate_window, bg='white', padx=30, pady=20)
        main_frame.pack()
        
        # 左侧：二维码图片区域
        left_frame = tk.Frame(main_frame, bg='white')
        left_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # 获取字体族（优先使用项目字体文件）
        try:
            import ui_utils
            font_family = ui_utils.get_font_family()
        except:
            font_family = 'Arial'
        
        # 存储图片引用，避免被垃圾回收
        image_refs = []
        
        # 加载并显示二维码
        try:
            if os.path.exists(qrcode_path):
                # 尝试使用PIL加载JPG图片
                try:
                    from PIL import Image, ImageTk
                    pil_image = Image.open(qrcode_path)
                    # 需要在正确的Tkinter窗口上下文中创建PhotoImage
                    qr_image = ImageTk.PhotoImage(pil_image, master=donate_window)
                    image_refs.append(qr_image)  # 保持引用
                    qr_label = tk.Label(left_frame, image=qr_image, bg='white')
                    qr_label.image = qr_image  # 保持引用
                    qr_label.pack()
                except ImportError:
                    # 如果没有PIL，尝试使用PhotoImage（仅支持GIF/PNG）
                    from tkinter import PhotoImage
                    qr_image = PhotoImage(file=qrcode_path, master=donate_window)
                    image_refs.append(qr_image)  # 保持引用
                    qr_label = tk.Label(left_frame, image=qr_image, bg='white')
                    qr_label.image = qr_image  # 保持引用
                    qr_label.pack()
            else:
                error_label = tk.Label(left_frame, 
                                     text='二维码图片未找到\nQR code image not found',
                                     font=(font_family, 10),
                                     bg='white', fg='red')
                error_label.pack()
        except Exception as e:
            error_label = tk.Label(left_frame,
                                 text=f'加载图片失败\nFailed to load image: {e}',
                                 font=(font_family, 10),
                                 bg='white', fg='red')
            error_label.pack()
        
        # 右侧：说明文字
        right_frame = tk.Frame(main_frame, bg='white', width=300)
        right_frame.pack(side=tk.LEFT, fill='both', expand=True)
        
        message_label = tk.Label(right_frame,
                                text=t('donate_message'),
                                font=(font_family, 11),
                                bg='white', fg='#333333',
                                justify='left',
                                wraplength=280)
        message_label.pack(anchor='nw', pady=(0, 20))
        
        # 关闭按钮
        close_text = '关闭' if CURRENT_LANGUAGE == 'zh_CN' else 'Close'
        close_button = ttk.Button(right_frame,
                                 text=close_text,
                                 command=donate_window.destroy,
                                 width=15)
        close_button.pack(anchor='sw')
        
        # 计算窗口尺寸和居中位置（使用与 show_about 相同的方法）
        # 方法：先临时显示窗口在屏幕外，计算尺寸，然后隐藏，再设置正确位置
        # 这样可以确保 update_idletasks() 能正确计算窗口尺寸
        donate_window.geometry("1x1+-10000+-10000")
        donate_window.deiconify()  # 临时显示在屏幕外
        donate_window.update_idletasks()
        donate_window.update()
        
        # 等待一下，确保内容完全渲染
        donate_window.after(50, lambda: None)
        donate_window.update()
        
        # 获取实际尺寸
        width = donate_window.winfo_width()
        height = donate_window.winfo_height()
        
        # 如果尺寸仍然无效，使用 reqwidth 和 reqheight
        if width <= 1 or height <= 1:
            width = donate_window.winfo_reqwidth()
            height = donate_window.winfo_reqheight()
            # 如果请求尺寸也无效，使用默认尺寸
            if width <= 1 or height <= 1:
                width = 600
                height = 400
        
        # 再次隐藏窗口
        donate_window.withdraw()
        
        # 计算居中位置
        screen_width = donate_window.winfo_screenwidth()
        screen_height = donate_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 设置 transient 和 grab_set（在显示前设置）
        if parent:
            donate_window.transient(parent)
        
        # 设置正确的几何位置
        donate_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # 在显示打赏窗口前，暂时取消关于对话框的topmost（如果存在）
        about_topmost_restore = None
        try:
            global _about_dialog_instance
            if _about_dialog_instance and _about_dialog_instance.winfo_exists():
                try:
                    about_topmost_restore = _about_dialog_instance.attributes('-topmost')
                    if about_topmost_restore:
                        _about_dialog_instance.attributes('-topmost', False)
                except:
                    pass
        except:
            pass
        
        # 最后显示对话框
        donate_window.deiconify()
        if parent:
            donate_window.grab_set()
        
        # 确保窗口置顶（使用topmost属性，并保持置顶直到窗口关闭）
        try:
            donate_window.attributes('-topmost', True)
        except:
            pass
        donate_window.lift()
        donate_window.focus_force()
        donate_window.focus_set()
        
        # 确保窗口持续置顶（定期检查并重新设置）
        def maintain_topmost():
            """保持窗口置顶"""
            try:
                if donate_window.winfo_exists():
                    # 检查当前topmost状态，如果不是True则重新设置
                    try:
                        current_topmost = donate_window.attributes('-topmost')
                        if not current_topmost:
                            donate_window.attributes('-topmost', True)
                            donate_window.lift()
                    except:
                        donate_window.attributes('-topmost', True)
                        donate_window.lift()
                    # 继续检查
                    donate_window.after(200, maintain_topmost)
            except:
                pass
        
        # 开始保持置顶
        donate_window.after(200, maintain_topmost)
        
        # 窗口关闭时，恢复关于对话框的topmost（如果之前取消了）
        def on_donate_close(event=None):
            try:
                if about_topmost_restore is not None:
                    global _about_dialog_instance
                    if _about_dialog_instance and _about_dialog_instance.winfo_exists():
                        try:
                            _about_dialog_instance.attributes('-topmost', about_topmost_restore)
                        except:
                            pass
            except:
                pass
        
        donate_window.bind('<Destroy>', on_donate_close)
    except Exception as e:
        import traceback
        error_msg = f"显示打赏窗口时出错: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        try:
            messagebox.showerror("错误", f"显示打赏窗口时出错: {str(e)}")
        except:
            pass

def show_about(parent=None):
    """显示关于对话框，包含可点击的GitHub链接"""
    global _about_dialog_instance
    import webbrowser
    
    # 检查更新检查模块是否可用
    try:
        import update_checker
        UPDATE_CHECKER_AVAILABLE = True
        get_current_version = update_checker.get_current_version
    except ImportError:
        UPDATE_CHECKER_AVAILABLE = False
        def get_current_version(): return None
    
    # 获取更新管理函数
    def get_update_manager():
        """获取update_manager模块的函数"""
        try:
            import update_manager
            return {
                'check_for_updates': update_manager.check_for_updates
            }
        except:
            def check_for_updates(p): pass
            return {
                'check_for_updates': check_for_updates
            }
    
    update_manager_funcs = get_update_manager()
    check_for_updates = update_manager_funcs['check_for_updates']
    
    # 获取i18n变量和ui工具函数
    try:
        i18n_vars = get_i18n()
        CURRENT_LANGUAGE = i18n_vars['CURRENT_LANGUAGE']
        _ui_components = i18n_vars['_ui_components']
    except Exception as e:
        return
    
    try:
        ui_utils_funcs = get_ui_utils()
        create_toplevel = ui_utils_funcs['create_toplevel']
        set_window_icon = ui_utils_funcs['set_window_icon']
        center_window = ui_utils_funcs['center_window']
    except Exception as e:
        return
    
    # 获取父窗口：优先使用传入的parent，其次使用root，最后尝试获取当前活动窗口
    root_window = parent
    
    if not root_window:
        root_window = _ui_components.get('root')
    
    if not root_window:
        # 尝试获取当前活动的Tk窗口
        try:
            # 获取所有Tk窗口
            if tk._default_root:
                children = tk._default_root.winfo_children()
                for widget in children:
                    if isinstance(widget, (tk.Tk, tk.Toplevel)):
                        if widget.winfo_viewable():
                            root_window = widget
                            break
        except:
            pass
    
    # 如果父窗口不可见，尝试使其可见
    try:
        if root_window and hasattr(root_window, 'winfo_viewable'):
            if not root_window.winfo_viewable():
                # 尝试显示父窗口
                try:
                    if hasattr(root_window, 'deiconify'):
                        root_window.deiconify()
                    root_window.lift()
                    root_window.update()
                    # 再次检查是否可见
                    if not root_window.winfo_viewable():
                        root_window = None
                except:
                    root_window = None
    except:
        pass
    
    if not root_window:
        # 如果找不到父窗口，使用messagebox作为后备方案
        # 获取版本号
        version_info = ""
        if UPDATE_CHECKER_AVAILABLE:
            try:
                current_version = get_current_version()
                if current_version:
                    if CURRENT_LANGUAGE == 'zh_CN':
                        version_info = f"版本号：{current_version}\n\n"
                    else:
                        version_info = f"Version: {current_version}\n\n"
            except:
                pass
        
        if CURRENT_LANGUAGE == 'zh_CN':
            about_text = f"交叉口交通流量流向可视化工具\nIntersection Traffic Flow Visualize\n\n{version_info}版权所有 (C) \n\n本软件由 [江浦马保国] 开发，保留所有权利。\n欢迎复制、传播本软件。\n\nGitee 仓库：\nhttps://gitee.com/Chris_KLP/intersection-traffic-flow\n\nGitHub 仓库：\nhttps://github.com/chrisKLP-sys/intersection-traffic-flow"
        else:
            about_text = f"Intersection Traffic Flow Visualization Tool\n\n{version_info}Copyright (C) \n\nThis software is developed by [江浦马保国], all rights reserved.\nYou are welcome to copy and distribute this software.\n\nGitee Repository:\nhttps://gitee.com/Chris_KLP/intersection-traffic-flow\n\nGitHub Repository:\nhttps://github.com/chrisKLP-sys/intersection-traffic-flow"
        try:
            messagebox.showinfo(t('about'), about_text)
        except:
            pass
        return
    
    # 创建自定义对话框
    try:
        if _about_dialog_instance and _about_dialog_instance.winfo_exists():
            try:
                _about_dialog_instance.deiconify()
                _about_dialog_instance.lift()
                _about_dialog_instance.focus_set()
            except:
                pass
            return
    except:
        pass
    
    try:
        about_dialog = create_toplevel(root_window)
        # 立即隐藏对话框，避免在左上角闪现
        about_dialog.withdraw()
    except:
        return
    
    try:
        about_dialog.title(t('about'))
    except:
        pass
    
    # 设置窗口图标
    try:
        set_window_icon(about_dialog)
    except:
        pass
    
    try:
        about_dialog.resizable(False, False)
    except:
        pass
    
    # 确保窗口可见并在最前
    try:
        about_dialog.attributes('-topmost', True)
        about_dialog.lift()
    except:
        pass
    
    # 设置对话框背景
    try:
        about_dialog.configure(bg='white')
    except:
        pass
    
    # 创建主框架
    try:
        main_frame = tk.Frame(about_dialog, bg='white', padx=30, pady=20)
        main_frame.pack()
    except:
        return
    
    # 标题
    try:
        # 优先使用 get_font_family() 获取 HarmonyOS Sans 字体
        import ui_utils
        font_family = ui_utils.get_font_family()
        if not font_family:
            # 如果获取失败，使用 GUI_FONT_FAMILY 或安全字体
            GUI_FONT_FAMILY = ui_utils_funcs.get('GUI_FONT_FAMILY')
            if GUI_FONT_FAMILY:
                font_family = GUI_FONT_FAMILY
            else:
                font_family = ui_utils.get_safe_font_family()
    except:
        try:
            import ui_utils
            font_family = ui_utils.get_font_family() or 'Arial'
        except:
            font_family = 'Arial'
    
    # 获取 Medium 字体（用于标题）
    try:
        import ui_utils
        title_font_family = ui_utils.get_font_family_medium()
    except:
        title_font_family = font_family
    
    try:
        title_label = tk.Label(main_frame, 
                              text="交叉口交通流量流向可视化工具\nIntersection Traffic Flow Visualize",
                              font=(title_font_family, 12),
                              bg='white', fg='#333333')
        title_label.pack(pady=(0, 10))
    except:
        pass
    
    # 版本号
    version_text = ""
    if UPDATE_CHECKER_AVAILABLE:
        try:
            current_version = get_current_version()
            if current_version:
                if CURRENT_LANGUAGE == 'zh_CN':
                    version_text = f"版本号：{current_version}"
                else:
                    version_text = f"Version: {current_version}"
        except:
            pass
    
    if version_text:
        try:
            version_label = tk.Label(main_frame,
                                     text=version_text,
                                     font=(font_family, 10),
                                     bg='white', fg='#666666')
            version_label.pack(pady=(0, 15))
        except:
            pass
    
    # 版权信息
    try:
        if CURRENT_LANGUAGE == 'zh_CN':
            copyright_text = "版权所有 (C)\n\n本软件由 [江浦马保国] 开发，保留所有权利。\n欢迎复制、传播本软件。"
            gitee_label_text = "Gitee 仓库："
            github_label_text = "GitHub 仓库："
            email_label_text = "联系邮箱："
        else:
            copyright_text = "Copyright (C)\n\nThis software is developed by [江浦马保国], all rights reserved.\nYou are welcome to copy and distribute this software."
            gitee_label_text = "Gitee Repository:"
            github_label_text = "GitHub Repository:"
            email_label_text = "Contact Email:"
        
        copyright_label = tk.Label(main_frame, 
                                   text=copyright_text,
                                   font=(font_family, 10),
                                   bg='white', fg='#666666',
                                   justify='left')
        copyright_label.pack(pady=(0, 15))
    except:
        pass
    
    # Gitee链接框架（放在前面）
    try:
        gitee_frame = tk.Frame(main_frame, bg='white')
        gitee_frame.pack(pady=(0, 10))
        
        gitee_label = tk.Label(gitee_frame, 
                               text=gitee_label_text,
                               font=(font_family, 10),
                               bg='white', fg='#666666')
        gitee_label.pack(side=tk.LEFT)
        
        # 可点击的Gitee链接
        gitee_url = "https://gitee.com/Chris_KLP/intersection-traffic-flow"
        gitee_link_label = tk.Label(gitee_frame,
                             text=gitee_url,
                             font=(font_family, 10, 'underline'),
                             bg='white', fg='#0066cc',
                             cursor='hand2')
        gitee_link_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 绑定Gitee点击事件
        def open_gitee(event=None):
            webbrowser.open(gitee_url)
        
        gitee_link_label.bind('<Button-1>', open_gitee)
        gitee_link_label.bind('<Enter>', lambda e: gitee_link_label.config(fg='#004499'))
        gitee_link_label.bind('<Leave>', lambda e: gitee_link_label.config(fg='#0066cc'))
    except:
        pass
    
    # GitHub链接框架（放在后面）
    try:
        github_frame = tk.Frame(main_frame, bg='white')
        github_frame.pack(pady=(0, 10))
        
        github_label = tk.Label(github_frame, 
                               text=github_label_text,
                               font=(font_family, 10),
                               bg='white', fg='#666666')
        github_label.pack(side=tk.LEFT)
        
        # 可点击的GitHub链接
        github_url = "https://github.com/chrisKLP-sys/intersection-traffic-flow"
        github_link_label = tk.Label(github_frame,
                             text=github_url,
                             font=(font_family, 10, 'underline'),
                             bg='white', fg='#0066cc',
                             cursor='hand2')
        github_link_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 绑定GitHub点击事件
        def open_github(event=None):
            webbrowser.open(github_url)
        
        github_link_label.bind('<Button-1>', open_github)
        github_link_label.bind('<Enter>', lambda e: github_link_label.config(fg='#004499'))
        github_link_label.bind('<Leave>', lambda e: github_link_label.config(fg='#0066cc'))
    except:
        pass
    
    # 邮箱链接框架
    try:
        email_frame = tk.Frame(main_frame, bg='white')
        email_frame.pack(pady=(0, 15))
        
        email_label = tk.Label(email_frame, 
                              text=email_label_text,
                              font=(font_family, 10),
                              bg='white', fg='#666666')
        email_label.pack(side=tk.LEFT)
        
        # 可点击的邮箱链接
        email_address = "hqqcool@gmail.com"
        email_link_label = tk.Label(email_frame,
                                   text=email_address,
                                   font=(font_family, 10, 'underline'),
                                   bg='white', fg='#0066cc',
                                   cursor='hand2')
        email_link_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 绑定邮箱点击事件
        def open_email(event=None):
            webbrowser.open(f"mailto:{email_address}")
        
        email_link_label.bind('<Button-1>', open_email)
        email_link_label.bind('<Enter>', lambda e: email_link_label.config(fg='#004499'))
        email_link_label.bind('<Leave>', lambda e: email_link_label.config(fg='#0066cc'))
    except:
        pass
    
    # 按钮框架
    try:
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=(10, 0))
        
        # 检查更新按钮（如果更新检查模块可用）
        if UPDATE_CHECKER_AVAILABLE:
            check_update_text = t('btn_check_update')
            # 根据语言调整按钮宽度，英文文本较长需要更宽的按钮
            button_width = 20 if CURRENT_LANGUAGE == 'en_US' else 15
            
            # 创建检查更新按钮，使用包装函数确保正确捕获 root_window
            def on_check_update_click():
                """检查更新按钮点击事件处理"""
                try:
                    # 确保 root_window 存在
                    if root_window:
                        check_for_updates(root_window)
                    else:
                        # 如果 root_window 不存在，尝试从 _ui_components 获取
                        try:
                            root = _ui_components.get('root')
                            if root:
                                check_for_updates(root)
                            else:
                                messagebox.showerror("错误", "无法找到主窗口")
                        except Exception as e:
                            messagebox.showerror("错误", f"获取主窗口时出错: {e}")
                except Exception as e:
                    messagebox.showerror("错误", f"检查更新时出错: {e}")
            
            check_update_button = ttk.Button(button_frame, 
                                            text=check_update_text,
                                            command=on_check_update_click,
                                            width=button_width)
            check_update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 打赏按钮
        donate_text = t('btn_donate')
        donate_button_width = 15 if CURRENT_LANGUAGE == 'zh_CN' else 15
        
        # 创建打赏按钮，使用 lambda 确保正确捕获 root_window
        # 注意：使用 lambda 的默认参数来捕获当前作用域的 root_window
        def on_donate_click():
            """打赏按钮点击事件处理"""
            try:
                # 确保 root_window 存在
                if root_window:
                    show_donate_qrcode(root_window)
                else:
                    # 如果 root_window 不存在，尝试从 _ui_components 获取
                    try:
                        root = _ui_components.get('root')
                        if root:
                            show_donate_qrcode(root)
                        else:
                            messagebox.showerror("错误", "无法找到父窗口")
                    except Exception as e2:
                        messagebox.showerror("错误", f"无法找到父窗口: {e2}")
            except Exception as e:
                try:
                    messagebox.showerror("错误", f"打开打赏窗口时出错: {str(e)}")
                except:
                    pass
        
        donate_button = ttk.Button(button_frame,
                                  text=donate_text,
                                  command=on_donate_click,
                                  width=donate_button_width)
        donate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        
        # 关闭按钮
        close_text = '关闭' if CURRENT_LANGUAGE == 'zh_CN' else 'Close'
        close_button = ttk.Button(button_frame, 
                                 text=close_text,
                                 command=about_dialog.destroy,
                                 width=15)
        close_button.pack(side=tk.LEFT)
    except:
        pass
    
    # 在屏幕外临时显示对话框以计算正确的尺寸
    try:
        # 先设置一个屏幕外的位置，然后显示窗口
        about_dialog.geometry("1x1+-10000+-10000")
        about_dialog.deiconify()
        about_dialog.update_idletasks()
        about_dialog.update()
        
        # 获取实际尺寸
        width = about_dialog.winfo_width()
        height = about_dialog.winfo_height()
        
        # 如果尺寸太小，使用默认尺寸
        if width <= 1 or height <= 1:
            width = 500
            height = 400
        
        # 计算居中位置
        x = (about_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (height // 2)
        
        # 设置正确的位置，然后隐藏
        about_dialog.geometry(f'{width}x{height}+{x}+{y}')
        about_dialog.withdraw()
    except:
        pass
    
    # 设置 transient（在对话框显示前）
    if root_window:
        try:
            about_dialog.transient(root_window)
        except:
            pass
    
    try:
        _about_dialog_instance = about_dialog
        def on_close():
            try:
                if about_dialog.winfo_exists():
                    about_dialog.destroy()
            finally:
                try:
                    global _about_dialog_instance
                    _about_dialog_instance = None
                except:
                    pass
        
        about_dialog.protocol("WM_DELETE_WINDOW", on_close)
    except:
        pass
    
    # 最后显示对话框（此时已经在正确位置了）
    try:
        about_dialog.deiconify()
        
        # 设置 grab_set（在显示后）
        if root_window:
            try:
                about_dialog.grab_set()
            except:
                pass
        
        about_dialog.lift()
        about_dialog.attributes('-topmost', True)
        about_dialog.focus_set()
        about_dialog.update()
    except:
        pass

def show_help():
    """显示帮助文档"""
    import webbrowser
    import sys
    from urllib.request import pathname2url
    
    # 获取i18n变量
    i18n_vars = get_i18n()
    CURRENT_LANGUAGE = i18n_vars['CURRENT_LANGUAGE']
    
    # 获取帮助文档路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 根据当前语言选择帮助文档
    if CURRENT_LANGUAGE == 'zh_CN':
        help_file = os.path.join(base_path, '帮助文档_中文.html')
    else:
        help_file = os.path.join(base_path, '帮助文档_English.html')
    
    # 如果语言特定的帮助文档不存在，尝试通用名称
    if not os.path.exists(help_file):
        help_file = os.path.join(base_path, '帮助文档.html')
    
    # 检查文件是否存在
    if os.path.exists(help_file):
        try:
            # 获取绝对路径并转换为URL格式
            abs_path = os.path.abspath(help_file)
            # 使用pathname2url处理路径中的特殊字符（如中文）
            file_url = 'file://' + pathname2url(abs_path)
            # 使用系统默认浏览器打开
            webbrowser.open(file_url)
        except Exception as e:
            # 如果URL方式失败，尝试直接打开文件
            try:
                import subprocess
                import platform
                system = platform.system()
                if system == 'Darwin':  # macOS
                    subprocess.run(['open', help_file])
                elif system == 'Windows':
                    os.startfile(help_file)
                else:  # Linux
                    subprocess.run(['xdg-open', help_file])
            except Exception as e2:
                messagebox.showerror(t('file_load_error'), t('help_file_error', error=str(e), error2=str(e2), file=help_file))
    else:
        messagebox.showerror(t('file_load_error'), t('help_file_not_found', file=help_file))

def convert_to_float_list(string_list):
    """将字符串列表转换为浮点数列表，处理空值和无效值"""
    result = []
    for elem in string_list:
        if elem and elem.strip():  # 检查是否为空
            try:
                result.append(float(elem))
            except (ValueError, TypeError):
                result.append(0.0)  # 无效值默认为0
        else:
            result.append(0.0)  # 空值默认为0
    return result


