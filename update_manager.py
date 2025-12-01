# -*- coding: utf-8 -*-
"""更新管理模块"""
import os
import sys
import threading
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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
            'create_toplevel': ui_utils.create_toplevel,
            'set_window_icon': ui_utils.set_window_icon,
            'GUI_FONT_FAMILY': getattr(ui_utils, 'GUI_FONT_FAMILY', None)
        }
    except:
        def create_toplevel(p): return tk.Toplevel(p) if p else tk.Toplevel()
        def set_window_icon(w): pass
        return {
            'create_toplevel': create_toplevel,
            'set_window_icon': set_window_icon,
            'GUI_FONT_FAMILY': None
        }

def get_i18n():
    """获取i18n模块的变量和函数"""
    try:
        import i18n
        return {
            'CURRENT_LANGUAGE': i18n.CURRENT_LANGUAGE,
            '_ui_components': i18n._ui_components
        }
    except:
        return {
            'CURRENT_LANGUAGE': 'zh_CN',
            '_ui_components': {'table': None, 'root': None}
        }

# 检查update_checker是否可用
try:
    import update_checker
    UPDATE_CHECKER_AVAILABLE = True
except ImportError:
    UPDATE_CHECKER_AVAILABLE = False
    update_checker = None

def check_for_updates(parent=None):
    """
    检查更新
    parent: 父窗口
    """
    if not UPDATE_CHECKER_AVAILABLE:
        return
    
    try:
        # 获取ui工具函数
        ui_utils_funcs = get_ui_utils()
        create_toplevel = ui_utils_funcs['create_toplevel']
        set_window_icon = ui_utils_funcs['set_window_icon']
        GUI_FONT_FAMILY = ui_utils_funcs['GUI_FONT_FAMILY']
        
        # 获取i18n变量
        i18n_vars = get_i18n()
        _ui_components = i18n_vars['_ui_components']
        
        # 获取父窗口
        root_window = parent
        if not root_window:
            root_window = _ui_components.get('root')
        
        # 创建更新源选择对话框
        parent_window = root_window if root_window else tk._default_root
        source_dialog = create_toplevel(parent_window)
        source_dialog.title(t('update_source_select'))
        # 设置窗口图标
        set_window_icon(source_dialog)
        source_dialog.resizable(False, False)
        
        # 立即隐藏对话框，避免在左上角闪现
        source_dialog.withdraw()
        # 注意：transient 和 grab_set 在计算完尺寸后设置
        
        source_dialog.configure(bg='white')
        main_frame = tk.Frame(source_dialog, bg='white', padx=30, pady=20)
        main_frame.pack()
        
        # 获取字体族（优先使用项目字体文件）
        try:
            import ui_utils
            font_family = ui_utils.get_font_family()
        except:
            font_family = 'Arial'
        label_text = t('update_source_select') + ':'
        label = tk.Label(main_frame, text=label_text, font=(font_family, 10), bg='white', fg='#333333')
        label.pack(pady=(0, 20))
        
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=(0, 15))
        
        # 从Gitee更新按钮
        def on_gitee_update():
            source_dialog.destroy()
            show_update_dialog(root_window, 'gitee')
        
        gitee_button = ttk.Button(button_frame, text=t('update_source_gitee_button'), 
                                  command=on_gitee_update, width=20)
        gitee_button.pack(pady=(0, 5))
        
        # Gitee备注
        gitee_note = tk.Label(button_frame, text=t('update_source_gitee_note'),
                             font=(font_family, 9), bg='white', fg='#666666')
        gitee_note.pack(pady=(0, 15))
        
        # 从GitHub更新按钮
        def on_github_update():
            source_dialog.destroy()
            show_update_dialog(root_window, 'github')
        
        github_button = ttk.Button(button_frame, text=t('update_source_github_button'), 
                                   command=on_github_update, width=20)
        github_button.pack(pady=(0, 5))
        
        # GitHub备注
        github_note = tk.Label(button_frame, text=t('update_source_github_note'),
                              font=(font_family, 9), bg='white', fg='#666666')
        github_note.pack(pady=(0, 10))
        
        # 取消按钮
        def on_cancel():
            source_dialog.destroy()
        
        cancel_button = ttk.Button(main_frame, text=t('update_cancel'), command=on_cancel, width=10)
        cancel_button.pack(pady=(10, 0))
    
        # 计算窗口尺寸和居中位置（使用与 show_about 相同的方法）
        # 方法：先临时显示窗口在屏幕外，计算尺寸，然后隐藏，再设置正确位置
        source_dialog.geometry("1x1+-10000+-10000")
        source_dialog.deiconify()  # 临时显示在屏幕外
        source_dialog.update_idletasks()
        source_dialog.update()
        
        # 等待一下，确保内容完全渲染
        source_dialog.after(50, lambda: None)
        source_dialog.update()
        
        # 获取实际尺寸
        width = source_dialog.winfo_width()
        height = source_dialog.winfo_height()
        
        # 如果尺寸仍然无效，使用 reqwidth 和 reqheight
        if width <= 1 or height <= 1:
            width = source_dialog.winfo_reqwidth()
            height = source_dialog.winfo_reqheight()
            # 如果请求尺寸也无效，使用默认尺寸
            if width <= 1 or height <= 1:
                width = 400
                height = 300
        
        # 再次隐藏窗口
        source_dialog.withdraw()
        
        # 计算居中位置
        screen_width = source_dialog.winfo_screenwidth()
        screen_height = source_dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 在显示更新源选择对话框前，暂时取消关于对话框的topmost（如果存在）
        about_topmost_restore = None
        try:
            from dialogs import _about_dialog_instance
            if _about_dialog_instance and _about_dialog_instance.winfo_exists():
                try:
                    about_topmost_restore = _about_dialog_instance.attributes('-topmost')
                    if about_topmost_restore:
                        _about_dialog_instance.attributes('-topmost', False)
                except:
                    pass
        except:
            pass
        
        # 设置 transient（在显示前设置）
        if root_window:
            source_dialog.transient(root_window)
        
        # 设置正确的几何位置
        source_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # 最后显示对话框
        source_dialog.deiconify()
        if root_window:
            source_dialog.grab_set()
        
        # 确保窗口置顶（使用topmost属性）
        try:
            source_dialog.attributes('-topmost', True)
        except:
            pass
        source_dialog.lift()
        source_dialog.focus_force()
        source_dialog.focus_set()
        
        # 等待窗口完全渲染
        source_dialog.update_idletasks()
        source_dialog.update()
        
        # 窗口关闭时，恢复关于对话框的topmost（如果之前取消了）
        def on_source_dialog_close(event=None):
            try:
                if about_topmost_restore is not None:
                    from dialogs import _about_dialog_instance
                    if _about_dialog_instance and _about_dialog_instance.winfo_exists():
                        try:
                            _about_dialog_instance.attributes('-topmost', about_topmost_restore)
                        except:
                            pass
            except:
                pass
        
        source_dialog.bind('<Destroy>', on_source_dialog_close)
    
    except Exception as e:
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", f"检查更新时出错: {e}")
        except:
            pass


def show_auto_update_notification(parent, version, current_version, source, release_notes=None):
    """
    显示自动检查更新的通知对话框
    parent: 父窗口
    version: 新版本号
    current_version: 当前版本号
    source: 更新源 ('gitee' 或 'github')
    release_notes: 更新说明（可选）
    """
    if not UPDATE_CHECKER_AVAILABLE:
        return
    
    # 获取ui工具函数
    ui_utils_funcs = get_ui_utils()
    create_toplevel = ui_utils_funcs['create_toplevel']
    set_window_icon = ui_utils_funcs['set_window_icon']
    GUI_FONT_FAMILY = ui_utils_funcs['GUI_FONT_FAMILY']
    
    # 获取i18n变量
    i18n_vars = get_i18n()
    _ui_components = i18n_vars['_ui_components']
    
    # 获取父窗口
    root_window = parent
    if not root_window:
        root_window = _ui_components.get('root')
    
    # 创建通知对话框
    parent_window = root_window if root_window else tk._default_root
    notify_dialog = create_toplevel(parent_window)
    notify_dialog.title(t('update_auto_available'))
    # 设置窗口图标
    set_window_icon(notify_dialog)
    notify_dialog.resizable(False, False)
    if root_window:
        notify_dialog.transient(root_window)
        notify_dialog.grab_set()
    
    notify_dialog.configure(bg='white')
    main_frame = tk.Frame(notify_dialog, bg='white', padx=30, pady=20)
    main_frame.pack()
    
    # 获取字体族（优先使用项目字体文件）
    try:
        import ui_utils
        font_family = ui_utils.get_font_family()
    except:
        font_family = 'Arial'
    
    # 显示更新信息
    source_name = t('update_source_gitee') if source.lower() == 'gitee' else t('update_source_github')
    info_text = t('update_auto_available_msg', version=version, current=current_version, source=source_name)
    if release_notes:
        # 只显示前200个字符
        notes_preview = release_notes[:200] + ('...' if len(release_notes) > 200 else '')
        info_text += f"\n\n{t('update_release_notes')}\n{notes_preview}"
    
    info_label = tk.Label(main_frame, text=info_text, font=(font_family, 10), 
                          bg='white', fg='#333333', justify='left', wraplength=450)
    info_label.pack(pady=(0, 20))
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack()
    
    # 立即更新按钮
    def on_update_now():
        notify_dialog.destroy()
        # 直接使用检测到的更新源打开更新对话框
        show_update_dialog(root_window, source)
    
    update_button = ttk.Button(button_frame, text=t('update_now'), 
                              command=on_update_now, width=15)
    update_button.pack(side=tk.LEFT, padx=5)
    
    # 稍后提醒按钮
    def on_later():
        notify_dialog.destroy()
    
    later_button = ttk.Button(button_frame, text=t('update_later'), 
                             command=on_later, width=15)
    later_button.pack(side=tk.LEFT, padx=5)
    
    # 居中显示
    notify_dialog.update_idletasks()
    width = notify_dialog.winfo_width()
    height = notify_dialog.winfo_height()
    x = (notify_dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (notify_dialog.winfo_screenheight() // 2) - (height // 2)
    notify_dialog.geometry(f'{width}x{height}+{x}+{y}')
    notify_dialog.focus_set()


def auto_check_update_background():
    """
    后台自动检查更新
    先尝试Gitee，失败则尝试GitHub
    如果发现新版本，在主线程中显示通知对话框
    如果没有更新或检查失败，静默处理
    """
    if not UPDATE_CHECKER_AVAILABLE:
        return
    
    # 获取 _ui_components 用于在主线程中显示通知
    i18n_vars = get_i18n()
    _ui_components = i18n_vars['_ui_components']
    
    def check_thread():
        try:
            # 获取当前版本
            current_version = update_checker.get_current_version()
            if not current_version:
                # 如果无法获取版本号，尝试从version_info.txt直接读取
                try:
                    import os
                    import re
                    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version_info.txt')
                    if os.path.exists(version_file):
                        with open(version_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            match = re.search(r'(?:filevers|prodvers)=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
                            if match:
                                current_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                except:
                    pass
                if not current_version:
                    current_version = "2.4.0"  # 最后的默认版本
            
            # 先尝试Gitee源
            result = None
            source_used = None
            gitee_success = False
            
            try:
                result = update_checker.check_update('gitee')
                # check_update 总是返回7个值: (success, version, download_url, release_notes, error_message, tag_name, filename)
                if len(result) >= 7:
                    success, version, download_url, release_notes, error, tag_name, filename = result[:7]
                elif len(result) >= 5:
                    success, version, download_url, release_notes, error = result[:5]
                    tag_name = None
                    filename = None
                else:
                    success = result[0] if len(result) > 0 else False
                    version = result[1] if len(result) > 1 else None
                    download_url = result[2] if len(result) > 2 else None
                    release_notes = result[3] if len(result) > 3 else None
                    error = result[4] if len(result) > 4 else None
                    tag_name = None
                    filename = None
                
                if success and version and download_url:
                    # 检查版本
                    comparison = update_checker.compare_versions(current_version, version)
                    if comparison < 0:
                        # 发现新版本，显示通知
                        root_window = _ui_components.get('root')
                        if root_window:
                            root_window.after(0, lambda: show_auto_update_notification(
                                root_window, version, current_version, 'gitee', release_notes
                            ))
                        return
                    else:
                        # 没有新版本，静默处理
                        return
            except Exception as e:
                # Gitee检查失败（网络错误等），继续尝试GitHub
                pass
            
            # 如果Gitee失败或没有成功检查到更新，尝试GitHub
            try:
                result = update_checker.check_update('github')
                # check_update 总是返回7个值: (success, version, download_url, release_notes, error_message, tag_name, filename)
                if len(result) >= 7:
                    success, version, download_url, release_notes, error, tag_name, filename = result[:7]
                elif len(result) >= 5:
                    success, version, download_url, release_notes, error = result[:5]
                    tag_name = None
                    filename = None
                else:
                    success = result[0] if len(result) > 0 else False
                    version = result[1] if len(result) > 1 else None
                    download_url = result[2] if len(result) > 2 else None
                    release_notes = result[3] if len(result) > 3 else None
                    error = result[4] if len(result) > 4 else None
                    tag_name = None
                    filename = None
                
                if success and version and download_url:
                    # 检查版本
                    comparison = update_checker.compare_versions(current_version, version)
                    if comparison < 0:
                        # 发现新版本，显示通知
                        root_window = _ui_components.get('root')
                        if root_window:
                            root_window.after(0, lambda: show_auto_update_notification(
                                root_window, version, current_version, 'github', release_notes
                            ))
            except Exception as e:
                # GitHub也失败，静默处理
                pass
        except Exception as e:
            # 所有异常都静默处理，不打扰用户
            pass
    
    # 在后台线程中运行
    thread = threading.Thread(target=check_thread, daemon=True)
    thread.start()


def show_update_dialog(parent, source='gitee'):
    """
    显示更新对话框
    parent: 父窗口
    source: 更新源 ('github' 或 'gitee')
    """
    if not UPDATE_CHECKER_AVAILABLE:
        return
    
    # 获取ui工具函数
    ui_utils_funcs = get_ui_utils()
    create_toplevel = ui_utils_funcs['create_toplevel']
    set_window_icon = ui_utils_funcs['set_window_icon']
    GUI_FONT_FAMILY = ui_utils_funcs['GUI_FONT_FAMILY']
    
    # 确保source有默认值并规范化
    if not source:
        source = 'gitee'
    source = source.lower().strip()
    if source not in ['github', 'gitee']:
        source = 'gitee'  # 默认使用gitee
    
    # 创建更新对话框
    parent_window = parent if parent else tk._default_root
    update_dialog = create_toplevel(parent_window)
    update_dialog.title(t('update_checking'))
    # 设置窗口图标
    set_window_icon(update_dialog)
    # 允许调整大小，以便显示长错误信息
    update_dialog.resizable(True, True)
    # 设置最小宽度，确保能容纳长文本
    update_dialog.minsize(500, 200)
    
    # 立即隐藏对话框，避免在左上角闪现
    update_dialog.withdraw()
    # 注意：transient 和 grab_set 在计算完尺寸后设置
    
    update_dialog.configure(bg='white')
    main_frame = tk.Frame(update_dialog, bg='white', padx=30, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # 获取字体族（优先使用项目字体文件）
    try:
        import ui_utils
        font_family = ui_utils.get_font_family()
    except:
        font_family = 'Arial'
    
    # 状态标签
    status_label = tk.Label(main_frame, 
                           text=t('update_checking_github') if source == 'github' else t('update_checking_gitee'),
                           font=(font_family, 10),
                           bg='white', fg='#333333')
    status_label.pack(pady=(0, 15))
    
    # 进度条 - 检查更新阶段使用确定模式
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, length=400, mode='determinate')
    progress_bar.pack(pady=(0, 15))
    progress_var.set(0)  # 初始化为0
    
    # 详细信息标签 - 增加wraplength以容纳长错误信息
    # 中英文错误信息可能较长，设置wraplength为500像素
    info_label = tk.Label(main_frame, text='', font=(font_family, 9), bg='white', fg='#666666', 
                         wraplength=500, justify='left', anchor='w')
    info_label.pack(pady=(0, 15), fill='x', padx=10)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=10)
    
    close_button = ttk.Button(button_frame, text=t('update_close'), 
                             command=update_dialog.destroy, width=12)
    close_button.pack(side=tk.LEFT, padx=5)
    
    download_button = None
    skip_button = None
    save_as_button = None
    
    # 计算窗口尺寸和居中位置（使用与 show_about 相同的方法）
    # 方法：先临时显示窗口在屏幕外，计算尺寸，然后隐藏，再设置正确位置
    update_dialog.geometry("1x1+-10000+-10000")
    update_dialog.deiconify()  # 临时显示在屏幕外
    update_dialog.update_idletasks()
    update_dialog.update()
    
    # 等待一下，确保内容完全渲染
    update_dialog.after(50, lambda: None)
    update_dialog.update()
    
    # 获取实际尺寸
    width = update_dialog.winfo_width()
    height = update_dialog.winfo_height()
    
    # 如果尺寸仍然无效，使用 reqwidth 和 reqheight
    if width <= 1 or height <= 1:
        width = update_dialog.winfo_reqwidth()
        height = update_dialog.winfo_reqheight()
        # 如果请求尺寸也无效，使用默认尺寸
        if width <= 1 or height <= 1:
            width = 500
            height = 200
    
    # 再次隐藏窗口
    update_dialog.withdraw()
    
    # 计算居中位置
    screen_width = update_dialog.winfo_screenwidth()
    screen_height = update_dialog.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # 在显示更新对话框前，暂时取消关于对话框和更新源选择对话框的topmost（如果存在）
    about_topmost_restore = None
    source_topmost_restore = None
    try:
        from dialogs import _about_dialog_instance
        if _about_dialog_instance and _about_dialog_instance.winfo_exists():
            try:
                about_topmost_restore = _about_dialog_instance.attributes('-topmost')
                if about_topmost_restore:
                    _about_dialog_instance.attributes('-topmost', False)
            except:
                pass
    except:
        pass
    
    # 设置 transient（在显示前设置）
    if parent:
        update_dialog.transient(parent)
    
    # 设置正确的几何位置
    update_dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    # 最后显示对话框
    update_dialog.deiconify()
    if parent:
        update_dialog.grab_set()
    
    # 确保窗口置顶（使用topmost属性）
    try:
        update_dialog.attributes('-topmost', True)
    except:
        pass
    update_dialog.lift()
    update_dialog.focus_force()
    update_dialog.focus_set()
    
    # 等待窗口完全渲染
    update_dialog.update_idletasks()
    update_dialog.update()
    
    # 窗口关闭时，恢复关于对话框的topmost（如果之前取消了）
    def on_update_dialog_close(event=None):
        try:
            if about_topmost_restore is not None:
                from dialogs import _about_dialog_instance
                if _about_dialog_instance and _about_dialog_instance.winfo_exists():
                    try:
                        _about_dialog_instance.attributes('-topmost', about_topmost_restore)
                    except:
                        pass
        except:
            pass
    
    update_dialog.bind('<Destroy>', on_update_dialog_close)
    
    # 获取主窗口用于线程安全调用
    root_window = parent if parent else tk._default_root
    
    # 在后台线程中检查更新
    def check_update_thread():
        # 保存source到局部变量，避免闭包问题，并确保是字符串
        update_source = str(source).lower().strip()
        if update_source not in ['github', 'gitee']:
            update_source = 'gitee'
        
        # 模拟检查进度（0-90%）
        def update_check_progress(percent):
            def update():
                try:
                    if update_dialog.winfo_exists():
                        progress_var.set(percent)
                        progress_bar['value'] = percent  # 直接设置值
                        progress_bar.update_idletasks()
                        update_dialog.update_idletasks()
                        update_dialog.update()  # 强制刷新
                except:
                    pass
            # 使用主窗口的after方法，确保线程安全
            if root_window and root_window.winfo_exists():
                try:
                    root_window.after(0, update)
                except:
                    pass
        
        try:
            # 开始检查，进度到30%
            update_check_progress(30)
            
            current_version = update_checker.get_current_version()
            if not current_version:
                # 如果无法获取版本号，尝试从version_info.txt直接读取
                try:
                    import os
                    import re
                    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version_info.txt')
                    if os.path.exists(version_file):
                        with open(version_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            match = re.search(r'(?:filevers|prodvers)=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
                            if match:
                                current_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                except:
                    pass
                if not current_version:
                    current_version = "2.4.0"  # 最后的默认版本
            
            # 进度到60%
            update_check_progress(60)
            
            # check_update 返回 7 个值: (success, version, download_url, release_notes, error_message, tag_name, filename)
            result = update_checker.check_update(update_source)
            if len(result) == 7:
                success, version, download_url, release_notes, error, tag_name, filename = result
            else:
                # 向后兼容：如果返回 5 个值
                success, version, download_url, release_notes, error = result[:5]
                tag_name = None
                filename = None
            
            # 进度到90%
            update_check_progress(90)
            
            # 更新UI（需要在主线程中执行）
            def update_ui():
                # 检查是否是网络连接错误
                is_network_error = False
                if error:
                    error_lower = str(error).lower()
                    network_keywords = ['timeout', 'connection', '网络', '连接', 'unreachable', 'dns', 'refused']
                    is_network_error = any(keyword in error_lower for keyword in network_keywords)
                
                if not success:
                    if is_network_error:
                        # 网络连接错误：进度条到80%，弹出错误对话框
                        progress_var.set(80)
                        progress_bar['value'] = 80  # 直接设置值
                        progress_bar.update_idletasks()
                        update_dialog.update_idletasks()
                        update_dialog.update()
                        
                        # 弹出错误对话框
                        from tkinter import messagebox
                        messagebox.showerror(
                            t('update_network_error'),
                            t('update_network_error_msg'),
                            parent=update_dialog
                        )
                        
                        status_label.config(text=t('update_network_error'), fg='#cc0000')
                        info_label.config(text=t('update_network_error_msg'))
                    else:
                        # 其他错误：进度条到100%，显示错误信息
                        progress_var.set(100)
                        progress_bar['value'] = 100  # 直接设置值
                        progress_bar.update_idletasks()
                        update_dialog.update_idletasks()
                        update_dialog.update()
                        status_label.config(text=t('update_error'), fg='#cc0000')
                        info_label.config(text=t('update_error_msg', error=error or 'Unknown error'))
                    return
                
                # 检查完成，进度条到100%
                progress_var.set(100)
                progress_bar.update_idletasks()
                update_dialog.update_idletasks()
                update_dialog.update()
                
                if not download_url:
                    status_label.config(text=t('update_no_download'), fg='#cc0000')
                    info_label.config(text=t('update_no_download_msg'))
                    return
                
                # 比较版本
                comparison = update_checker.compare_versions(current_version, version)
                
                if comparison < 0:
                    # 有新版本
                    status_label.config(text=t('update_available'), fg='#0066cc')
                    info_text = t('update_available_msg', version=version, current=current_version)
                    if release_notes:
                        info_text += f"\n\n{t('update_release_notes')}\n{release_notes[:200]}"
                    info_label.config(text=info_text)
                    # 保持100%显示，等待用户选择
                    
                    # 添加下载选项按钮
                    def on_download_and_install():
                        # 隐藏按钮
                        if download_button:
                            download_button.pack_forget()
                        if save_as_button:
                            save_as_button.pack_forget()
                        if skip_button:
                            skip_button.pack_forget()
                        update_dialog.update_idletasks()
                        
                        # 重置进度条，从0开始下载
                        progress_var.set(0)
                        progress_bar.update_idletasks()
                        download_update(update_dialog, status_label, info_label, progress_bar, progress_var,
                                      download_url, version, auto_install=True,
                                      buttons=(download_button, save_as_button, skip_button))
                    
                    def on_save_as():
                        # 隐藏按钮
                        if download_button:
                            download_button.pack_forget()
                        if save_as_button:
                            save_as_button.pack_forget()
                        if skip_button:
                            skip_button.pack_forget()
                        update_dialog.update_idletasks()
                        
                        # 重置进度条，从0开始下载
                        progress_var.set(0)
                        progress_bar.update_idletasks()
                        download_update(update_dialog, status_label, info_label, progress_bar, progress_var,
                                      download_url, version, auto_install=False,
                                      buttons=(download_button, save_as_button, skip_button))
                    
                    def on_skip():
                        update_dialog.destroy()
                    
                    nonlocal download_button, skip_button, close_button, save_as_button
                    
                    # 隐藏或销毁关闭按钮
                    try:
                        close_button.pack_forget()
                        close_button.destroy()
                        close_button = None
                    except:
                        pass
                    
                    # 如果按钮已存在，先销毁
                    try:
                        if download_button:
                            download_button.destroy()
                        if skip_button:
                            skip_button.destroy()
                        if save_as_button:
                            save_as_button.destroy()
                    except:
                        pass
                    
                    # 确保按钮框架可见
                    button_frame.pack(pady=15)
                    
                    # 创建新按钮：直接更新、另存为、跳过
                    download_button = ttk.Button(button_frame, text=t('update_download_and_install'), 
                                                command=on_download_and_install, width=15)
                    download_button.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    save_as_button = ttk.Button(button_frame, text=t('update_save_as'), 
                                                command=on_save_as, width=15)
                    save_as_button.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    skip_button = ttk.Button(button_frame, text=t('update_skip'), 
                                            command=on_skip, width=15)
                    skip_button.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    
                    # 强制更新对话框布局并显示
                    button_frame.update_idletasks()
                    main_frame.update_idletasks()
                    update_dialog.update_idletasks()
                    
                    # 调整对话框大小以适应新内容
                    update_dialog.update()
                    new_height = max(update_dialog.winfo_reqheight(), 350)
                    # 重新计算居中位置
                    screen_width = update_dialog.winfo_screenwidth()
                    screen_height = update_dialog.winfo_screenheight()
                    new_x = (screen_width // 2) - (initial_width // 2)
                    new_y = (screen_height // 2) - (new_height // 2)
                    update_dialog.geometry(f'{initial_width}x{new_height}+{new_x}+{new_y}')
                    update_dialog.update()
                    
                    # 再次强制刷新
                    update_dialog.update_idletasks()
                    update_dialog.update()
                else:
                    # 已是最新版本
                    status_label.config(text=t('update_latest'), fg='#00aa00')
                    info_label.config(text=t('update_latest_msg', version=current_version))
                    # 保持100%显示
            
            # 使用主窗口的after方法，确保线程安全
            if root_window and root_window.winfo_exists():
                try:
                    root_window.after(0, update_ui)
                except:
                    pass
            
        except Exception as e:
            # 捕获异常信息到局部变量，避免闭包问题
            error_msg = str(e)
            error_lower = str(error_msg).lower()
            network_keywords = ['timeout', 'connection', '网络', '连接', 'unreachable', 'dns', 'refused']
            is_network_error = any(keyword in error_lower for keyword in network_keywords)
            
            def show_error():
                try:
                    if not update_dialog.winfo_exists():
                        return
                    if is_network_error:
                        # 网络连接错误：进度条到80%，弹出错误对话框
                        progress_var.set(80)
                        progress_bar['value'] = 80  # 直接设置值
                        progress_bar.update_idletasks()
                        update_dialog.update_idletasks()
                        update_dialog.update()
                        
                        # 弹出错误对话框
                        from tkinter import messagebox
                        messagebox.showerror(
                            t('update_network_error'),
                            t('update_network_error_msg'),
                            parent=update_dialog
                        )
                        
                        status_label.config(text=t('update_network_error'), fg='#cc0000')
                        info_label.config(text=t('update_network_error_msg'))
                    else:
                        # 其他错误：进度条到100%，显示错误信息
                        progress_var.set(100)
                        progress_bar.update_idletasks()
                        status_label.config(text=t('update_error'), fg='#cc0000')
                        info_label.config(text=t('update_error_msg', error=error_msg))
                except:
                    pass
            # 使用主窗口的after方法，确保线程安全
            if root_window and root_window.winfo_exists():
                try:
                    root_window.after(0, show_error)
                except:
                    pass
    
    # 启动检查线程
    thread = threading.Thread(target=check_update_thread, daemon=True)
    thread.start()


def download_update(dialog, status_label, info_label, progress_bar, progress_var, download_url, version, auto_install=True, buttons=None):
    """
    下载更新
    auto_install: True=下载后自动安装, False=下载后另存为
    buttons: (download_button, save_as_button, skip_button) 按钮引用，用于在下载完成后重新显示
    """
    if not UPDATE_CHECKER_AVAILABLE:
        return
    
    # 更新窗口标题和状态
    dialog.title(t('update_downloading_title'))
    status_label.config(text=t('update_downloading'), fg='#0066cc')
    info_label.config(text='')
    
    # 停止不确定模式动画，切换到确定模式
    progress_bar.stop()
    progress_bar.config(mode='determinate', maximum=100)
    progress_var.set(0)
    progress_bar.update_idletasks()
    
    # 如果是另存为，先让用户选择保存位置
    if not auto_install:
        from tkinter import filedialog
        # 获取当前可执行文件的目录
        if getattr(sys, 'frozen', False):
            default_dir = os.path.dirname(sys.executable)
        else:
            default_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 建议的文件名（根据当前语言）
        if CURRENT_LANGUAGE == 'zh_CN':
            suggested_filename = f'交叉口交通流量流向可视化工具{version}.exe'
        else:
            suggested_filename = f'IntersectionTrafficFlowVisualize{version}.exe'
        
        # 打开文件保存对话框
        filetypes_text = [('Executable files', '*.exe'), ('All files', '*.*')] if CURRENT_LANGUAGE != 'zh_CN' else [('可执行文件', '*.exe'), ('所有文件', '*.*')]
        save_path = filedialog.asksaveasfilename(
            parent=dialog,
            title=t('update_save_as'),
            initialdir=default_dir,
            initialfile=suggested_filename,
            defaultextension='.exe',
            filetypes=filetypes_text
        )
        
        if not save_path:
            # 用户取消了保存
            status_label.config(text=t('update_cancel'), fg='#666666')
            info_label.config(text='')
            progress_bar.stop()
            return
        
        temp_file = save_path
    else:
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'update_{version}.exe')
    
    # 下载进度回调（在后台线程中调用，需要通过after在主线程中更新UI）
    downloaded_bytes = [0]
    total_bytes = [0]
    
    # 限制更新频率，避免过于频繁的UI更新（每100KB更新一次）
    last_update_size = [0]
    UPDATE_INTERVAL = 100 * 1024  # 100KB
    
    def progress_callback(downloaded, total):
        downloaded_bytes[0] = downloaded
        total_bytes[0] = total
        
        # 限制更新频率
        if downloaded - last_update_size[0] < UPDATE_INTERVAL and downloaded < total:
            return
        
        last_update_size[0] = downloaded
        
        # 格式化大小
        def format_size(size):
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f}KB"
            else:
                return f"{size/(1024*1024):.1f}MB"
        
        # 在主线程中更新UI
        def update_progress():
            try:
                if total > 0:
                    # 有总大小，显示百分比
                    percent = (downloaded / total) * 100
                    progress_var.set(percent)
                    # 同时直接设置进度条值，确保更新
                    progress_bar['value'] = percent
                    info_text = t('update_download_progress', 
                                 percent=f"{percent:.1f}",
                                 downloaded=format_size(downloaded),
                                 total=format_size(total))
                else:
                    # 没有总大小，显示不确定模式或已下载大小
                    # 使用一个估算的进度（基于已下载的大小）
                    # 假设文件大约在10-50MB之间，根据已下载大小估算
                    estimated_total = max(downloaded * 2, 10 * 1024 * 1024)  # 至少10MB
                    percent = min((downloaded / estimated_total) * 100, 95)  # 最多显示95%
                    progress_var.set(percent)
                    progress_bar['value'] = percent
                    info_text = f"已下载: {format_size(downloaded)}"
                
                info_label.config(text=info_text)
                # 强制更新进度条显示
                progress_bar.update_idletasks()
                dialog.update_idletasks()
                dialog.update()  # 强制刷新对话框
                
            except Exception as e:
                pass
        
        # 使用 after_idle 确保在主线程空闲时立即执行
        dialog.after_idle(update_progress)
    
    # 在后台线程中下载
    def download_thread():
        try:
            # 重置更新计数器
            last_update_size[0] = 0
            success, error = update_checker.download_file(download_url, temp_file, progress_callback)
            
            def update_ui():
                if not success:
                    status_label.config(text=t('update_download_failed'), fg='#cc0000')
                    info_label.config(text=t('update_download_failed_msg', error=error))
                    progress_bar.stop()
                    progress_var.set(0)  # 重置进度条
                    # 按钮保持隐藏，不再显示
                    return
                
                # 下载成功，确保进度条显示100%
                progress_var.set(100)
                progress_bar.update_idletasks()
                dialog.update_idletasks()
                dialog.update()  # 强制刷新对话框
                
                if auto_install:
                    # 下载成功，准备更新
                    # 在后台线程中准备更新文件
                    def prepare_thread():
                        current_exe = sys.executable
                        # version 参数已经在 download_update 函数的作用域中
                        prepare_success, prepare_error = update_checker.prepare_update_for_restart(
                            temp_file, current_exe, version, CURRENT_LANGUAGE
                        )
                        
                        def prepare_result():
                            if prepare_success:
                                # 准备成功，显示重启提示弹窗
                                update_dialog.destroy()  # 先关闭更新对话框
                                
                                # 创建重启提示弹窗（使用parent作为父窗口）
                                restart_dialog = create_toplevel(parent)
                                restart_dialog.title(t('update_prepared'))
                                # 设置窗口图标
                                set_window_icon(restart_dialog)
                                restart_dialog.resizable(False, False)
                                
                                # 设置窗口图标（如果有）
                                try:
                                    restart_dialog.iconbitmap(default='')
                                except:
                                    pass
                                
                                # 居中显示
                                restart_dialog.update_idletasks()
                                width = 400
                                height = 150
                                x = (restart_dialog.winfo_screenwidth() // 2) - (width // 2)
                                y = (restart_dialog.winfo_screenheight() // 2) - (height // 2)
                                restart_dialog.geometry(f'{width}x{height}+{x}+{y}')
                                
                                # 主框架
                                main_frame = tk.Frame(restart_dialog, bg='white')
                                main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                                
                                # 消息标签
                                # 获取字体（尝试从主窗口获取，如果没有则使用默认值）
                                try:
                                    main_font = tk.font.nametofont('TkDefaultFont')
                                    msg_font = (main_font.actual()['family'], 10)
                                except:
                                    try:
                                        import ui_utils
                                        safe_font = ui_utils.get_font_family()
                                        msg_font = (safe_font, 10)
                                    except:
                                        msg_font = ('Arial', 10)
                                
                                msg_label = tk.Label(
                                    main_frame, 
                                    text=t('update_prepared_msg'),
                                    font=msg_font,
                                    bg='white',
                                    fg='#333333',
                                    wraplength=350,
                                    justify='left'
                                )
                                msg_label.pack(pady=(0, 20))
                                
                                # 按钮框架
                                button_frame = tk.Frame(main_frame, bg='white')
                                button_frame.pack()
                                
                                def on_restart():
                                    # 执行重启
                                    restart_success, restart_error = update_checker.restart_with_update()
                                    if restart_success:
                                        # 延迟一下，确保批处理脚本已经启动
                                        restart_dialog.after(500, lambda: (
                                            restart_dialog.destroy(),
                                            os._exit(0)
                                        ))
                                    else:
                                        # 重启失败，显示错误
                                        from tkinter import messagebox
                                        messagebox.showerror(
                                            t('update_install_restart_failed'),
                                            t('update_install_restart_failed_msg', error=restart_error),
                                            parent=restart_dialog
                                        )
                                
                                # 立即重启软件按钮
                                restart_button = ttk.Button(
                                    button_frame,
                                    text=t('update_restart_now'),
                                    command=on_restart,
                                    width=20
                                )
                                restart_button.pack()
                                
                                # 关闭窗口时也执行重启
                                def on_close():
                                    on_restart()
                                
                                restart_dialog.protocol("WM_DELETE_WINDOW", on_close)
                                
                            else:
                                # 准备失败
                                status_label.config(text=t('update_install_failed'), fg='#cc0000')
                                info_label.config(text=t('update_install_failed_msg', error=prepare_error))
                                progress_bar.stop()
                                progress_var.set(0)
                        
                        dialog.after(0, prepare_result)
                    
                    # 启动准备线程
                    prepare_thread_obj = threading.Thread(target=prepare_thread, daemon=True)
                    prepare_thread_obj.start()
                else:
                    # 另存为模式：下载成功
                    # 确保进度条显示100%
                    progress_var.set(100)
                    progress_bar.update_idletasks()
                    dialog.update_idletasks()
                    dialog.update()
                    
                    status_label.config(text=t('update_save_success'), fg='#00aa00')
                    info_label.config(text=t('update_save_success_msg', path=temp_file))
                    # 不要调用stop()，保持进度条显示100%
                    # progress_bar.stop()  # 注释掉，保持显示100%
                    
                    # 2秒后自动关闭对话框
                    dialog.after(2000, dialog.destroy)
            
            dialog.after(0, update_ui)
            
        except Exception as e:
            def show_error():
                status_label.config(text=t('update_download_failed'), fg='#cc0000')
                info_label.config(text=t('update_download_failed_msg', error=str(e)))
                progress_bar.stop()
                progress_var.set(0)  # 重置进度条
            dialog.after(0, show_error)
    
    thread = threading.Thread(target=download_thread, daemon=True)
    thread.start()


