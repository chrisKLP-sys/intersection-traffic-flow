# -*- coding: utf-8 -*-
"""文件操作模块"""
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# 延迟导入模块，避免循环依赖
def t(key, **kwargs):
    """翻译函数（延迟导入i18n）"""
    try:
        import i18n
        return i18n.t(key, **kwargs)
    except:
        return key

def convert_to_float_list(string_list):
    """将字符串列表转换为浮点数列表，处理空值和无效值"""
    result = []
    for elem in string_list:
        if elem and elem.strip():
            try:
                result.append(float(elem))
            except (ValueError, TypeError):
                result.append(0.0)
        else:
            result.append(0.0)
    return result

# 模块级别的update_window_title函数，用于存储root引用
def update_window_title():
    """更新窗口标题（延迟导入i18n）"""
    try:
        import i18n
        i18n.update_ui_language()
    except:
        pass

def finalize_table_creation(table_instance, root_instance, keep_position=False):
    """
    统一处理表格创建后的所有更新操作，确保所有路径的效果完全一致
    
    参数:
        table_instance: 表格实例
        root_instance: 根窗口实例
        keep_position: 是否保持窗口位置（True=保持位置，False=居中显示）
    """
    try:
        import i18n
        _ui_components = i18n._ui_components
    except:
        _ui_components = {'table': None, 'root': None}
    
    try:
        import ui_utils
        adjust_window_size = ui_utils.adjust_window_size
        center_window = ui_utils.center_window
    except:
        def adjust_window_size(w, keep_position=False): pass
        def center_window(w): pass
    
    # 步骤1：更新引用
    _ui_components['table'] = table_instance
    
    # 步骤2：更新语言，确保所有标题正确显示
    try:
        import i18n
        i18n.update_ui_language()
    except:
        pass
    
    # 步骤3：更新窗口标题
    update_window_title()
    
    # 步骤4：强制更新，确保表格完全渲染
    root_instance.update_idletasks()
    root_instance.update()
    
    # 步骤5：调整窗口大小
    if keep_position:
        adjust_window_size(root_instance, keep_position=True)
    else:
        adjust_window_size(root_instance)
        center_window(root_instance)
    
    # 步骤6：等待提示框对齐逻辑执行后，再次调整窗口大小以确保完全对齐
    # 提示框的对齐逻辑在表格创建后延迟200ms执行
    def adjust_size_after_alignment():
        """在提示框对齐逻辑执行后再次调整窗口大小，确保完全对齐"""
        try:
            root_instance.update_idletasks()
            root_instance.update()
            if keep_position:
                adjust_window_size(root_instance, keep_position=True)
            else:
                adjust_window_size(root_instance)
                center_window(root_instance)
        except:
            pass
    
    root_instance.after(250, adjust_size_after_alignment)  # 250ms，略大于提示框的200ms延迟

def load_data_from_file(file_name, table_instance, root_instance):
    """从文件加载数据的内部函数"""
    # 延迟导入模块，避免循环依赖
    try:
        import table_widget
        Table = table_widget.Table
    except:
        Table = None
    
    try:
        import ui_utils
        adjust_window_size = ui_utils.adjust_window_size
    except:
        def adjust_window_size(w): pass
    
    try:
        import i18n
        _ui_components = i18n._ui_components
    except:
        _ui_components = {'table': None, 'root': None}
    
    if not file_name:
        return False, table_instance
    
    # 尝试多种编码读取文件
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
    lines = None
    for encoding in encodings:
        try:
            with open(file_name, 'r', encoding=encoding) as file:
                lines = file.readlines()
                break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # 解码失败或空文件，统一由外层提示“文件无法解析”
    if lines is None:
        return False, table_instance
    
    if len(lines) == 0:
        return False, table_instance
    
    try:
        # 解析第一行，获取路数声明和交通规则
        first_line = lines[0].strip()
        num_entries = None
        traffic_rule = 'right'  # 默认为右行规则
        
        # 尝试从第一行提取路数和交通规则
        # 新格式：本交叉口为X路交叉口，实行左/右行通行规则。
        match = re.search(r'本交叉口为(\d+)路交叉口', first_line)
        if match:
            num_entries = int(match.group(1))
            if num_entries < 3 or num_entries > 6:
                return False, table_instance
            # 尝试提取交通规则（新格式：实行左/右行通行规则）
            rule_match = re.search(r'实行([左右])行通行规则', first_line)
            if rule_match:
                if rule_match.group(1) == '左':
                    traffic_rule = 'left'
                else:
                    traffic_rule = 'right'
            else:
                # 向后兼容：尝试旧格式（交通规则：左/右行）
                rule_match_old = re.search(r'交通规则[：:]\s*([左右])行', first_line)
                if rule_match_old:
                    if rule_match_old.group(1) == '左':
                        traffic_rule = 'left'
                    else:
                        traffic_rule = 'right'
            # 跳过第一行声明
            data_lines = lines[1:]
        else:
            # 如果未声明路数，尝试从数据推断
            # 向后兼容：检查是否是旧格式
            if any('u_turns' in line or 'left_turns' in line for line in lines[:6]):
                num_entries = 4
                data_lines = lines
            else:
                # 尝试从数据长度推断路数
                # 跳过第一行（可能是声明或数据），从第二行开始解析
                if len(lines) > 1:
                    # 尝试解析第一行数据，看是否是数据行
                    first_data_line = lines[0].strip()
                    if first_data_line and ',' in first_data_line:
                        # 第一行可能是数据，尝试推断路数
                        values = [v.strip() for v in first_data_line.split(',')]
                        if len(values) >= 3:  # 至少包含names、angles或flow数据
                            # 从数据长度推断路数
                            num_entries = len(values)
                            if num_entries < 3 or num_entries > 6:
                                return False, table_instance
                            data_lines = lines  # 第一行也是数据
                        else:
                            return False, table_instance
                    else:
                        # 第一行不是数据，从第二行开始
                        data_lines = lines[1:]
                        if len(data_lines) > 0:
                            first_data_line = data_lines[0].strip()
                            if first_data_line and ',' in first_data_line:
                                values = [v.strip() for v in first_data_line.split(',')]
                                num_entries = len(values)
                                if num_entries < 3 or num_entries > 6:
                                    return False, table_instance
                            else:
                                return False, table_instance
                        else:
                            return False, table_instance
                else:
                    return False, table_instance
        
        # 解析数据（兼容旧格式和新格式）
        data = {}
        data['names'] = []
        data['angles'] = []
        for i in range(num_entries):
            data[f'flow_{i}'] = []
        
        # 解析数据行
        line_idx = 0
        for line in data_lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试解析：可能是 "key: value1,value2,..." 或直接是 "value1,value2,..."
            if ':' in line:
                # 旧格式：key: value1,value2,...
                parts = line.split(':', 1)
                key = parts[0].strip()
                values_str = parts[1] if len(parts) > 1 else ''
            else:
                # 新格式：直接是 value1,value2,...（按顺序：names, angles, flow_0, flow_1, ...）
                key = None
                values_str = line
            
            # 解析值（以逗号分隔）
            values = [v.strip() for v in values_str.split(',')]
            # 缺失数据视为0，超出数据截断
            values = [v if v else '0' for v in values[:num_entries]]
            # 如果数据不足，补0
            while len(values) < num_entries:
                values.append('0')
            
            # 映射到新格式
            if key:
                # 有key的情况（旧格式或带key的新格式）
                if key == 'names':
                    data['names'] = values[:num_entries]
                elif key == 'angles':
                    data['angles'] = values[:num_entries]
                elif key == 'u_turns':
                    data['flow_0'] = values[:num_entries]
                elif key == 'left_turns':
                    data['flow_1'] = values[:num_entries]
                elif key == 'straights':
                    data['flow_2'] = values[:num_entries]
                elif key == 'right_turns':
                    data['flow_3'] = values[:num_entries]
                elif key.startswith('flow_'):
                    try:
                        flow_idx = int(key.split('_')[1])
                        if flow_idx < num_entries:
                            data[f'flow_{flow_idx}'] = values[:num_entries]
                    except:
                        pass
            else:
                # 没有key的情况（新格式，按顺序）
                if line_idx == 0:
                    data['names'] = values[:num_entries]
                elif line_idx == 1:
                    data['angles'] = values[:num_entries]
                else:
                    flow_idx = line_idx - 2
                    if flow_idx < num_entries:
                        data[f'flow_{flow_idx}'] = values[:num_entries]
                line_idx += 1
        
        # 确保所有数据都有足够的长度
        for key in data:
            while len(data[key]) < num_entries:
                data[key].append('0')
            data[key] = data[key][:num_entries]
        
        # 如果当前表格路数与文件路数不一致，或者交通规则不一致，需要重新创建表格
        if table_instance.num_entries != num_entries or getattr(table_instance, 'traffic_rule', 'right') != traffic_rule:
            # 优雅地销毁旧表格：先移除，再销毁，确保一次性完成
            old_table = table_instance
            
            # 步骤1：先从界面移除旧表格（立即从布局中移除）
            old_table.pack_forget()
            # 强制更新，确保界面立即刷新（旧表格消失）
            root_instance.update_idletasks()
            root_instance.update()
            
            # 步骤2：彻底销毁旧表格及其所有子组件
            old_table.destroy()
            # 再次强制更新，确保销毁操作完成
            root_instance.update_idletasks()
            root_instance.update()
            
            # 步骤3：查找按钮框架，确保新表格pack在按钮框架之前
            button_frame = None
            for widget in root_instance.winfo_children():
                if isinstance(widget, tk.Frame):
                    # 检查这个Frame是否包含按钮（通过检查子组件）
                    # Table也是Frame，但Table包含Entry和Label，按钮框架只包含按钮
                    children = widget.winfo_children()
                    if children:
                        # 如果所有子组件都是按钮，则这是按钮框架
                        all_buttons = all(isinstance(child, (ttk.Button, tk.Button)) for child in children)
                        if all_buttons and len(children) > 0:
                            button_frame = widget
                            break
            
            # 步骤4：创建新表格（传递交通规则）
            if Table is None:
                # 如果Table未导入，尝试从外部获取
                try:
                    import table_widget
                    Table = table_widget.Table
                except:
                    raise ImportError("无法导入Table类")
            table_instance = Table(root_instance, num_entries=num_entries, traffic_rule=traffic_rule)
            
            # 步骤5：将新表格添加到界面
            if button_frame:
                table_instance.pack(before=button_frame)
            else:
                table_instance.pack()
            
            # 步骤6：统一处理表格创建后的所有更新操作
            finalize_table_creation(table_instance, root_instance, keep_position=True)
        
        # 设置数据
        table_instance.set_data(data)
        table_instance.file_name = file_name
        # 更新交通规则（即使表格已存在）
        table_instance.traffic_rule = traffic_rule
        # 更新交通规则选择控件
        if hasattr(table_instance, 'traffic_rule_var'):
            table_instance.traffic_rule_var.set(traffic_rule)
        table_instance.is_modified = False
        # 如果表格是新创建的，已经通过finalize_table_creation处理了
        # 如果表格已存在，只需要更新引用和窗口标题
        if table_instance.num_entries == num_entries and getattr(table_instance, 'traffic_rule', 'right') == traffic_rule:
            # 表格未重新创建，只更新引用和标题
            _ui_components['table'] = table_instance
            update_window_title()
            try:
                import i18n
                i18n.update_ui_language()
            except:
                pass
            root_instance.update_idletasks()
            root_instance.update()
            adjust_window_size(root_instance, keep_position=True)
        
        return True, table_instance
        
    except Exception:
        # 任何解析异常都视为无法解析，由外层统一给出提示
        return False, table_instance


def on_load_data_click():
    """读取数据文件"""
    # 延迟导入模块
    try:
        import i18n
        _ui_components = i18n._ui_components
        table = _ui_components.get('table')
        root = _ui_components.get('root')
    except:
        messagebox.showerror(t('file_load_error'), '无法访问表格对象')
        return
    
    if table is None or root is None:
        messagebox.showerror(t('file_load_error'), '表格或窗口对象未找到')
        return
    
    # 循环选择文件，直到成功加载或用户取消
    while True:
        file_name = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not file_name:
            # 用户取消选择，直接退出
            return
        
        success, new_table = load_data_from_file(file_name, table, root)
        if success:
            # load_data_from_file 内部已经通过 finalize_table_creation 处理了所有更新
            # 这里只需要显示成功消息
            messagebox.showinfo(t('file_saved_success'), t('file_load_success', num=new_table.num_entries))
            return
        else:
            # 按既有的兼容方案仍无法正确解析文件，提示并重新弹出文件选择框
            messagebox.showerror(t('file_load_error'), t('file_cannot_parse'))


def on_save_data_click():
    """保存数据到当前文件"""
    # 延迟导入模块
    try:
        import i18n
        _ui_components = i18n._ui_components
        table = _ui_components.get('table')
    except:
        messagebox.showerror(t('file_load_error'), '无法访问表格对象')
        return
    
    if table is None:
        messagebox.showerror(t('file_load_error'), t('file_no_save_target'))
        return
    
    table.get()
    if hasattr(table, 'file_name') and table.file_name:
        try:
            with open(table.file_name, 'w', encoding='utf-8') as file:
                # 写入第一行声明（包含交通规则）
                traffic_rule_text = t('left_hand') if table.traffic_rule == 'left' else t('right_hand')
                file.write(t('file_declaration', num=table.num_entries, rule=traffic_rule_text) + '\n')
                # 写入数据（以逗号分隔）
                for key in ['names', 'angles']:
                    if key in table.data:
                        file.write(','.join(table.data[key]) + '\n')
                # 写入流向数据
                for i in range(table.num_entries):
                    key = f'flow_{i}'
                    if key in table.data:
                        file.write(','.join(table.data[key]) + '\n')
            table.is_modified = False  # 保存后清除修改标记
            try:
                import i18n
                i18n.update_ui_language()
            except:
                pass
            messagebox.showinfo(t('file_saved_success'), t('file_saved', file=table.file_name))
        except Exception as e:
            messagebox.showerror(t('file_load_error'), t('file_save_error', error=str(e)))
    else:
        # 如果没有文件名，调用另存为
        on_save_data_as_click()


def on_save_data_as_click():
    """数据另存为"""
    # 延迟导入模块
    try:
        import i18n
        _ui_components = i18n._ui_components
        table = _ui_components.get('table')
    except:
        messagebox.showerror(t('file_load_error'), '无法访问表格对象')
        return
    
    if table is None:
        messagebox.showerror(t('file_load_error'), t('file_no_save_target'))
        return
    
    table.get()
    file_name = filedialog.asksaveasfilename(
        defaultextension='.txt',
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_name:
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                # 写入第一行声明（包含交通规则）
                traffic_rule_text = t('left_hand') if table.traffic_rule == 'left' else t('right_hand')
                file.write(t('file_declaration', num=table.num_entries, rule=traffic_rule_text) + '\n')
                # 写入数据（以逗号分隔）
                for key in ['names', 'angles']:
                    if key in table.data:
                        file.write(','.join(table.data[key]) + '\n')
                # 写入流向数据
                for i in range(table.num_entries):
                    key = f'flow_{i}'
                    if key in table.data:
                        file.write(','.join(table.data[key]) + '\n')
            table.file_name = file_name
            if not hasattr(table, 'loaded_file'):
                table.loaded_file = file_name
            table.is_modified = False  # 另存为后清除修改标记
            try:
                import i18n
                i18n.update_ui_language()
            except:
                pass
            messagebox.showinfo(t('file_saved_success'), t('file_saved', file=file_name))
        except Exception as e:
            messagebox.showerror(t('file_load_error'), t('file_save_error', error=str(e)))


def on_clear_data_click():
    """清空数据"""
    # 延迟导入模块
    try:
        import i18n
        _ui_components = i18n._ui_components
        table = _ui_components.get('table')
    except:
        messagebox.showerror(t('file_load_error'), '无法访问表格对象')
        return
    
    if table is None:
        messagebox.showerror(t('file_load_error'), t('data_empty'))
        return
    
    # 确认操作
    if messagebox.askyesno(t('confirm'), t('confirm_clear')):
        # 清空所有输入框
        for row in table._widgets:
            for widget in row:
                widget.delete(0, tk.END)
        # 清除文件名和修改标记
        table.file_name = None
        table.is_modified = False
        try:
            import i18n
            i18n.update_ui_language()
        except:
            pass
        messagebox.showinfo(t('file_saved_success'), t('data_cleared'))


def on_new_file_click():
    """新建文件"""
    # 延迟导入模块
    try:
        import i18n
        _ui_components = i18n._ui_components
        root = _ui_components.get('root')
        table = _ui_components.get('table')
    except:
        messagebox.showerror(t('file_load_error'), '无法访问主窗口或表格对象')
        return
    
    if root is None or table is None:
        messagebox.showerror(t('file_load_error'), '无法访问主窗口或表格对象')
        return
    
    try:
        import ui_utils
        create_toplevel = ui_utils.create_toplevel
        set_window_icon = ui_utils.set_window_icon
        adjust_window_size = ui_utils.adjust_window_size
        get_gui_font_family = lambda: ui_utils.GUI_FONT_FAMILY if hasattr(ui_utils, 'GUI_FONT_FAMILY') else None
    except:
        def create_toplevel(p): return tk.Toplevel(p) if p else tk.Toplevel()
        def set_window_icon(w): pass
        def adjust_window_size(w): pass
        get_gui_font_family = lambda: None
    
    try:
        import table_widget
        Table = table_widget.Table
    except:
        messagebox.showerror(t('file_load_error'), '无法导入Table类')
        return
    
    try:
        import config
        load_config = config.load_config
    except:
        def load_config(): return {'traffic_rule': 'right'}
    
    try:
        import i18n
        CURRENT_LANGUAGE = i18n.CURRENT_LANGUAGE
        set_language = i18n.set_language
        update_ui_language = i18n.update_ui_language
    except:
        CURRENT_LANGUAGE = 'zh_CN'
        def set_language(c): return False
        def update_ui_language(): pass
    
    # 确认操作
    if table.is_modified:
        if not messagebox.askyesno(t('confirm'), t('confirm_new_file')):
            return
    
    # 创建简单的对话框选择交叉口类型
    dialog = create_toplevel(root)
    dialog.title(t('select_intersection_type'))
    # 设置窗口图标
    set_window_icon(dialog)
    dialog.resizable(False, False)
    
    # 立即隐藏对话框，避免在左上角闪现
    dialog.withdraw()
    dialog.geometry("1x1+-10000+-10000")
    
    dialog.transient(root)  # 设置为父窗口的临时窗口
    # 注意：grab_set 在显示后设置
    
    result = {'choice': None}
    
    def on_choice(choice):
        result['choice'] = choice
        dialog.destroy()
    
    def on_close():
        result['choice'] = None
        dialog.destroy()
    
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
    }
    
    def update_dialog_language():
        """更新对话框中的语言文本"""
        if dialog_components['title_label']:
            dialog_components['title_label'].config(text=t('select_intersection_type'))
        # 根据语言调整按钮宽度（英文文本通常更长）
        btn_width = 25 if CURRENT_LANGUAGE == 'en_US' else 20
        if dialog_components['btn1']:
            dialog_components['btn1'].config(text=t('btn_3way'), width=btn_width)
        if dialog_components['btn2']:
            dialog_components['btn2'].config(text=t('btn_4way'), width=btn_width)
        if dialog_components['btn3']:
            dialog_components['btn3'].config(text=t('btn_5way'), width=btn_width)
        if dialog_components['btn4']:
            dialog_components['btn4'].config(text=t('btn_6way'), width=btn_width)
        dialog.title(t('select_intersection_type'))
    
    def change_dialog_language(lang_code):
        """切换对话框语言（全局生效）"""
        if set_language(lang_code):
            update_dialog_language()
            # 重新调整对话框大小以适应新的文本长度
            dialog.update_idletasks()
            dialog_width = dialog.winfo_reqwidth()
            dialog_height = dialog.winfo_reqheight()
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
            dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            # 同时更新主界面（如果已创建）
            if _ui_components.get('root'):
                update_ui_language()
                root = _ui_components.get('root')
                if root:
                    adjust_window_size(root, keep_position=True)
            return True
        return False
    
    # 创建菜单栏
    menubar = tk.Menu(dialog)
    dialog.config(menu=menubar)
    
    # 语言菜单
    language_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Language / 语言", menu=language_menu)
    language_menu.add_radiobutton(label="简体中文", command=lambda: change_dialog_language('zh_CN'))
    language_menu.add_radiobutton(label="English", command=lambda: change_dialog_language('en_US'))
    
    # 创建主框架
    main_frame = tk.Frame(dialog, padx=40, pady=40, bg='white', relief='flat')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 标题
    # 获取字体族（优先使用项目字体文件）
    try:
        import ui_utils
        font_family = ui_utils.get_font_family()
    except:
        font_family = 'Arial'
    title_label = tk.Label(main_frame, text=t('select_intersection_type'), 
                          font=(font_family, 14, 'bold'), pady=20, bg='white', fg='#333333')
    title_label.pack()
    dialog_components['title_label'] = title_label
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack()
    
    # 创建按钮（使用ttk.Button以获得现代化样式）
    # 英文文本通常更长，使用更大的宽度或自适应
    btn_width = 25 if CURRENT_LANGUAGE == 'en_US' else 20
    btn1 = ttk.Button(button_frame, text=t('btn_3way'), width=btn_width, 
                     command=lambda: on_choice(3))
    btn1.pack(pady=6)
    dialog_components['btn1'] = btn1
    
    btn2 = ttk.Button(button_frame, text=t('btn_4way'), width=btn_width, 
                     command=lambda: on_choice(4))
    btn2.pack(pady=6)
    dialog_components['btn2'] = btn2
    
    btn3 = ttk.Button(button_frame, text=t('btn_5way'), width=btn_width, 
                     command=lambda: on_choice(5))
    btn3.pack(pady=6)
    dialog_components['btn3'] = btn3
    
    btn4 = ttk.Button(button_frame, text=t('btn_6way'), width=btn_width, 
                     command=lambda: on_choice(6))
    btn4.pack(pady=6)
    dialog_components['btn4'] = btn4
    
    # 在隐藏状态下计算尺寸和居中位置
    dialog.update_idletasks()
    dialog_width = dialog.winfo_reqwidth()
    dialog_height = dialog.winfo_reqheight()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - dialog_width) // 2
    y = (screen_height - dialog_height) // 2
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # 最后显示对话框
    dialog.deiconify()
    dialog.grab_set()  # 模态对话框
    dialog.focus_set()
    
    # 等待用户选择
    dialog.wait_window()
    
    choice = result['choice']
    if choice is None:
        return
    
    num_entries = choice
    
    # 如果路数不同，需要重新创建表格
    if table.num_entries != num_entries:
        # 优雅地销毁旧表格：先移除，再销毁，确保一次性完成
        old_table = table
        
        # 步骤1：先从界面移除旧表格（立即从布局中移除）
        old_table.pack_forget()
        # 强制更新，确保界面立即刷新（旧表格消失）
        root.update_idletasks()
        root.update()
        
        # 步骤2：彻底销毁旧表格及其所有子组件
        old_table.destroy()
        # 再次强制更新，确保销毁操作完成
        root.update_idletasks()
        root.update()
        
        # 步骤3：查找按钮框架位置
        button_frame = None
        for widget in root.winfo_children():
            if isinstance(widget, tk.Frame):
                children = widget.winfo_children()
                if children:
                    all_buttons = all(isinstance(child, (ttk.Button, tk.Button)) for child in children)
                    if all_buttons and len(children) > 0:
                        button_frame = widget
                        break
        
        # 步骤4：创建新表格（使用配置中的通行规则）
        config = load_config()
        traffic_rule = config.get('traffic_rule', 'right')
        table = Table(root, num_entries=num_entries, traffic_rule=traffic_rule)
        
        # 步骤5：将新表格添加到界面
        if button_frame:
            table.pack(before=button_frame)
        else:
            table.pack()
        
        # 步骤6：统一处理表格创建后的所有更新操作
        finalize_table_creation(table, root, keep_position=True)
        
        # 步骤7：重新绑定按钮
        if 'plot_button' in globals():
            plot_button.config(command=lambda: plot_traffic_flow(table))
    
    # 清空数据并设置默认方位角
    # 计算方位角默认值（0-360度平均分布）
    angle_step = 360.0 / num_entries
    default_angles = [i * angle_step for i in range(num_entries)]
    
    for row_idx, row in enumerate(table._widgets):
        for col_idx, widget in enumerate(row):
            widget.delete(0, tk.END)
            # 如果是方位角列（第2列，索引为1），设置默认值
            # 注意：在_widgets中，col_idx=0对应进口名称，col_idx=1对应方位角
            if col_idx == 1:  # 方位角列
                default_angle = default_angles[row_idx]
                widget.insert(0, str(int(default_angle)) if default_angle == int(default_angle) else str(default_angle))
    table.file_name = None
    table.is_modified = False
    # 确保_ui_components中的table引用是最新的（如果表格未重新创建）
    if table.num_entries == num_entries:
        _ui_components['table'] = table
        update_window_title()
    messagebox.showinfo(t('file_saved_success'), t('new_table_created', num=num_entries))



