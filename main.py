# -*- coding: utf-8 -*-
"""
主程序入口
交叉口交通流量流向可视化工具
"""
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import re

# 显式导入matplotlib后端，确保PyInstaller打包时包含它们
import matplotlib.backends.backend_pdf
import matplotlib.backends._backend_pdf_ps
import matplotlib.backends.backend_svg

plt.ioff()

# 导入更新检查模块
try:
    import update_checker
    UPDATE_CHECKER_AVAILABLE = True
except ImportError:
    UPDATE_CHECKER_AVAILABLE = False

# 程序启动时检查待安装的更新
if UPDATE_CHECKER_AVAILABLE:
    try:
        has_pending, new_file_path, current_exe_path, version, language = update_checker.check_pending_update()
        if has_pending:
            # 执行待安装的更新
            success, error = update_checker.execute_pending_update()
            if success:
                # 安装成功，程序会启动新版本，当前程序退出
                os._exit(0)
            else:
                # 安装失败，继续运行当前程序
                print(f"自动安装更新失败: {error}")
    except Exception as e:
        # 检查更新时出错，继续运行当前程序
        print(f"检查待安装更新时出错: {e}")

# 导入项目模块
import i18n
import config
import ui_utils
import table_widget
import file_operations
import update_manager
import dialogs
import plotting


def main():
    """主函数"""
    # 创建主窗口（先不显示）
    root = ui_utils.create_window()
    root.title(i18n.t('app_title'))
    root.withdraw()  # 先隐藏窗口
    # 先设置一个临时位置（屏幕外），避免在左上角闪现
    root.geometry("1x1+-10000+-10000")
    
    # 设置现代化界面样式
    ui_font_family = ui_utils.setup_modern_style(root)
    
    # 将root保存到update_window_title函数中
    file_operations.update_window_title.root = root
    
    # 加载配置文件
    config_data = config.load_config()
    if 'language' in config_data:
        i18n.set_language(config_data['language'])
    
    # 选择交叉口类型或读取文件
    try:
        choice = dialogs.select_intersection_type()
    except Exception as e:
        print(f"选择对话框出错：{e}")
        root.destroy()
        sys.exit(1)
    
    if choice is None:
        root.destroy()
        sys.exit(0)
    
    num_entries = None
    auto_load_from_start = False
    
    if choice == 'load_file':
        # 启动界面选择“读取数据文件”：
        # 不在这里解析文件，只记下标记，后续统一走 on_load_data_click 的逻辑
        auto_load_from_start = True
        # 先用默认路数创建一个表格，具体路数由后续加载文件时自动调整
        num_entries = config_data.get('num_entries', 4) or 4
    else:
        num_entries = choice
    
    if num_entries is None:
        num_entries = 4
    
    traffic_rule = config_data.get('traffic_rule', 'right')
    
    # 创建表格
    table = table_widget.Table(root, num_entries=num_entries, traffic_rule=traffic_rule)
    table.pack()
    
    # 强制更新，确保表格完全渲染（包括提示框的对齐逻辑）
    root.update_idletasks()
    root.update()
    
    # 创建按钮框架
    button_frame = tk.Frame(root, bg='#f5f5f5')
    button_frame.pack(side='bottom', pady=10)
    
    # 创建按钮
    def on_about_click():
        try:
            # 优先使用本地 root 引用，避免全局引用未准备好
            root_ref = root
            if root_ref:
                try:
                    root_ref.after(0, lambda: dialogs.show_about(root_ref))
                except Exception:
                    dialogs.show_about(root_ref)
            else:
                dialogs.show_about(i18n._ui_components.get('root'))
        except Exception:
            try:
                dialogs.show_about(None)
            except Exception:
                try:
                    messagebox.showinfo(i18n.t('about'), 'Intersection Traffic Flow Visualize')
                except:
                    pass

    btn_configs = [
        ('new_file', i18n.t('btn_new_file'), file_operations.on_new_file_click),
        ('load', i18n.t('btn_load'), file_operations.on_load_data_click),
        ('clear_data', i18n.t('btn_clear_data'), file_operations.on_clear_data_click),
        ('save', i18n.t('btn_save'), file_operations.on_save_data_click),
        ('save_as', i18n.t('btn_save_as'), file_operations.on_save_data_as_click),
        ('plot', i18n.t('btn_draw'), lambda: plotting.plot_traffic_flow(i18n._ui_components.get('table'))),
        ('help', i18n.t('btn_help'), dialogs.show_help),
        ('about', i18n.t('btn_about'), on_about_click)
    ]
    
    for key, text, command in btn_configs:
        # 创建按钮，直接绑定命令函数
        # 使用默认参数捕获command，避免闭包问题
        def make_wrapper(cmd):
            """创建命令包装器，添加错误处理"""
            def wrapper():
                try:
                    cmd()
                except Exception as e:
                    import traceback
                    error_msg = f"按钮操作出错: {str(e)}\n\n{traceback.format_exc()}"
                    print(error_msg)
                    try:
                        messagebox.showerror("错误", f"按钮操作出错: {str(e)}")
                    except:
                        pass
            return wrapper
        
        btn = ttk.Button(button_frame, text=text, command=make_wrapper(command))
        btn.pack(side=tk.LEFT, padx=5)
        i18n._ui_components['buttons'][key] = btn
    
    # 创建菜单栏
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # 语言菜单
    language_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Language / 语言", menu=language_menu)
    language_menu.add_radiobutton(label="简体中文", command=lambda: i18n.change_language('zh_CN'))
    language_menu.add_radiobutton(label="English", command=lambda: i18n.change_language('en_US'))
    
    # 保存引用
    i18n._ui_components['table'] = table
    i18n._ui_components['root'] = root
    
    # 统一处理表格创建后的所有更新操作（从启动界面进入，不保持位置，居中显示）
    file_operations.finalize_table_creation(table, root, keep_position=False)
    
    # 如果是从启动界面选择了“读取数据文件”，自动调用与主窗口相同的读取逻辑
    if auto_load_from_start:
        try:
            file_operations.on_load_data_click()
            # 读取成功后，更新本地 table 引用
            try:
                table = i18n._ui_components.get('table', table)
            except Exception:
                pass
        except Exception:
            # 出错时保持现有空表格即可
            pass
    
    # 显示主窗口
    root.deiconify()
    root.lift()
    root.focus_force()
    root.update()
    
    # 设置图标
    ui_utils.set_window_icon(root)
    root.after(50, lambda: ui_utils.set_window_icon(root))
    
    # 启动更新检查
    if UPDATE_CHECKER_AVAILABLE:
        root.after(3000, update_manager.auto_check_update_background)
    
    # 添加关闭事件
    def on_main_window_close():
        try:
            config.save_config(table=table)
            plt.close('all')
            root.quit()
            root.destroy()
        except:
            pass
        finally:
            os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_main_window_close)
    
    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    main()

