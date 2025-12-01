# -*- coding: utf-8 -*-
"""表格组件模块"""
import tkinter as tk
from tkinter import ttk
import re

# 延迟导入i18n模块，避免循环依赖
def t(key, **kwargs):
    """翻译函数（延迟导入i18n）"""
    try:
        import i18n
        return i18n.t(key, **kwargs)
    except:
        return key

# 延迟导入其他模块
def normalize_angle(angle):
    """将角度归一化到0-360度范围"""
    try:
        angle = float(angle)
        normalized = angle % 360
        if normalized < 0:
            normalized += 360
        return normalized
    except (ValueError, TypeError):
        return angle

def save_config():
    """保存配置（延迟导入config模块）"""
    try:
        import config
        # 需要从外部传入table对象，这里暂时不调用
        pass
    except:
        pass

def update_window_title():
    """更新窗口标题（延迟导入i18n模块）"""
    try:
        import i18n
        i18n.update_ui_language()
    except:
        pass

class Table(tk.Frame):
    def __init__(self, parent, num_entries=4, traffic_rule='right'):
        tk.Frame.__init__(self, parent, bg='white', relief='flat', padx=10, pady=10)
        self.num_entries = num_entries
        self.traffic_rule = traffic_rule  # 'right' 或 'left'，默认为右行规则
        self._widgets = []
        self.row_labels = []  # 保存行标题引用，用于语言切换
        self.file_name = None
        self.is_modified = False
        
        # 初始化数据结构：names, angles, flow_0, flow_1, ..., flow_{N-1}
        # raw_data: 存储用户输入的原始数据（未归一化、未排序）
        # data: 存储处理后的数据（归一化、排序后），用于显示和绘制
        self.raw_data = {
            'names': [],
            'angles': []
        }
        self.data = {
            'names': [],
            'angles': []
        }
        for i in range(num_entries):
            self.raw_data[f'flow_{i}'] = []
            self.data[f'flow_{i}'] = []
        
        # 生成表头
        headings = [t('entry_number'), t('entry_name'), t('angle')]
        # 根据路数生成流向列标题
        if num_entries == 4:
            # 4路交叉口使用直观的表头
            # 左行规则下：掉头、右转、直行、左转（顺时针顺序）
            # 右行规则下：掉头、左转、直行、右转（逆时针顺序）
            if traffic_rule == 'left':
                headings.extend([t('u_turn'), t('right_turn'), t('straight'), t('left_turn')])
            else:
                headings.extend([t('u_turn'), t('left_turn'), t('straight'), t('right_turn')])
        else:
            # 其他路数使用流线X_Y格式
            # 对于每个进口X，流向顺序是：流线X_X, 流线X_X-1, ..., 流线X_1
            # 表头显示为通用格式，其中X表示当前行的进口编号
            for i in range(num_entries):
                # 计算出口编号：X, X-1, X-2, ..., 1（需要规整化）
                # 对于表头，我们显示相对位置：X, X-1, X-2, ..., X-(N-1)
                if i == 0:
                    headings.append(t('flow_line'))  # 掉头
                else:
                    headings.append(t('flow_line_n', n=i))  # 其他流向
        
        columns = len(headings)
        
        # 创建统一的提示信息容器 - 在计算完列数后添加，以便正确设置columnspan
        # 使用全局字体变量（延迟导入ui_utils，优先使用项目字体文件）
        try:
            import ui_utils
            font_family = ui_utils.get_font_family()
            # 获取 Medium 字体（用于标题）
            try:
                heading_font_family = ui_utils.get_font_family_medium()
            except:
                heading_font_family = font_family
        except:
            try:
                import ui_utils
                font_family = ui_utils.get_safe_font_family()
                heading_font_family = font_family
            except:
                font_family = 'Arial'
                heading_font_family = 'Arial'
        
        # 创建带边框的容器Frame
        notice_container = tk.Frame(self, 
                                    bg='#fff9e6',  # 浅黄色背景
                                    relief='solid',
                                    borderwidth=1,
                                    padx=12,
                                    pady=10)
        notice_container.grid(row=0, column=0, columnspan=columns, padx=5, pady=(5, 12), sticky='ew')
        self.notice_container = notice_container  # 保存引用以便更新语言
        
        # 标题：重要提醒（使用 Medium 字体）
        title_label = tk.Label(notice_container,
                               text=t('important_notice'),
                               bg='#fff9e6',
                               fg='#856404',
                               font=(heading_font_family, 10),
                               anchor='w')
        title_label.pack(fill='x', pady=(0, 8))
        self.notice_title_label = title_label  # 保存引用以便更新语言
        
        # 优化换行：确保标点符号不在行首的辅助函数
        def prevent_punctuation_at_line_start(text):
            """防止标点符号出现在行首"""
            # 中英文标点符号列表
            # 中文标点：，。、；：？！…—～·""''（）【】《》〈〉「」『』
            # 英文标点：, . ; : ? ! - — ( ) [ ] { } " ' 
            punctuation_chars = [
                # 中文标点
                '，', '。', '、', '；', '：', '？', '！', '…', '—', '～', '·',
                '"', '"', ''', ''', '（', '）', '【', '】', '《', '》', '〈', '〉', '「', '」', '『', '』',
                # 英文标点
                ',', '.', ';', ':', '?', '!', '-', '—', '(', ')', '[', ']', '{', '}', '"', "'"
            ]
            
            # 在标点符号前插入非断行空格（\u00A0），防止标点符号单独出现在行首
            result = text
            for punct in punctuation_chars:
                # 在空格后的标点符号前插入非断行空格
                result = re.sub(r' ' + re.escape(punct), '\u00A0' + punct, result)
                # 在行首的标点符号前插入非断行空格（但保留原有的换行）
                result = re.sub(r'^' + re.escape(punct), '\u00A0' + punct, result, flags=re.MULTILINE)
            
            return result
        
        # 提示信息（完整文本，中间用\n分隔）
        notice_text = t('notice_content').replace('\r\n', '\n').replace('\r', '\n')
        # 清理连续的多个换行符，只保留一个
        while '\n\n' in notice_text:
            notice_text = notice_text.replace('\n\n', '\n')
        # 防止在 "2." 后面换行：将 "2. " 替换为 "2.\u00A0"（非断行空格）
        # 这样可以确保 "2." 和后面的文字作为一个整体，不会在 "2." 后换行
        notice_text = notice_text.replace('2. ', '2.\u00A0')
        # 优化换行：确保标点符号不在行首
        notice_text = prevent_punctuation_at_line_start(notice_text)
        
        # 先计算一个合理的初始 wraplength，基于父窗口的宽度估算
        # 这样可以避免在用户眼前动态调整排版
        initial_wraplength = 300  # 使用一个较大的初始值，避免初始显示时换行过多
        try:
            # 尝试从父窗口获取宽度作为参考
            parent_width = self.winfo_width()
            if parent_width > 100:
                # 估算：父窗口宽度减去一些边距和padding
                initial_wraplength = max(100, parent_width - 100)
        except:
            pass
        
        notice_label = tk.Label(notice_container,
                                text=notice_text,
                                bg='#fff9e6',  # 与容器背景一致
                                fg='#856404',  # 深黄色文字
                                font=(font_family, 10),
                                justify='left',
                                anchor='nw',
                                wraplength=initial_wraplength)  # 使用合理的初始值
        notice_label.pack(fill='both', expand=True)
        self.notice_label = notice_label  # 保存引用以便更新语言
        
        # 创建函数来更新wraplength，使其随容器宽度变化
        # 使用标志位避免初始显示时的动态调整
        _wraplength_initialized = [False]  # 使用列表以便在闭包中修改
        _last_wraplength = [initial_wraplength]  # 使用列表以便在闭包中修改
        
        def update_wraplength(event=None, force=False):
            """更新提示标签的wraplength，使其适应容器宽度"""
            try:
                # 获取容器的实际宽度
                notice_container.update_idletasks()
                container_width = notice_container.winfo_width()
                if container_width > 1:  # 确保容器已显示
                    # 减去左右padding（12*2=24）和边距（5*2=10），留更多余量以避免在数字后换行
                    # 增加余量，确保 "2." 这样的短片段不会单独换行
                    available_width = container_width - 20  # 减少减去的值，增加可用宽度
                    if available_width > 100:  # 确保最小宽度
                        # 初始设置时，如果初始值已经合理，就不调整了
                        if not _wraplength_initialized[0]:
                            # 第一次设置：如果初始值和计算值差距不大（50像素内），就不调整
                            if abs(available_width - initial_wraplength) > 50:
                                if hasattr(self, 'notice_label') and self.notice_label:
                                    self.notice_label.config(wraplength=available_width)
                                    _last_wraplength[0] = available_width
                            _wraplength_initialized[0] = True
                        elif force or abs(available_width - _last_wraplength[0]) > 10:
                            # 后续更新：只有当宽度变化超过10像素时才更新，避免频繁调整
                            if hasattr(self, 'notice_label') and self.notice_label:
                                self.notice_label.config(wraplength=available_width)
                                _last_wraplength[0] = available_width
            except:
                pass
        
        # 保存函数引用以便后续调用
        self.update_notice_wraplength = lambda: update_wraplength(force=True)
        
        # 绑定容器大小变化事件（只在真正改变时更新）
        notice_container.bind('<Configure>', update_wraplength)
        # 延迟更新一次，确保在窗口完全显示后再调整（但只在必要时调整）
        def delayed_update():
            """延迟更新，确保在窗口完全显示后再调整一次（如果需要）"""
            try:
                update_wraplength(force=False)  # 不强制，让函数自己判断是否需要调整
            except:
                pass
        # 使用 after 延迟，确保窗口布局完成后再更新
        self.after(200, delayed_update)  # 增加延迟时间，确保窗口完全显示
        
        # 添加交通规则选择控件
        rule_frame = tk.Frame(self, bg='white')
        # 与数据表格左对齐：使用与列标题相同的 padx=5
        rule_frame.grid(row=2, column=0, columnspan=columns, padx=5, pady=5, sticky='w')
        # 获取字体族（优先使用项目字体文件，使用 Regular 字体，与数据表格一致）
        try:
            import ui_utils
            rule_font_family = ui_utils.get_font_family()
        except:
            rule_font_family = 'Arial'
        
        self.rule_label = tk.Label(rule_frame, text=t('traffic_rule'), bg='white', font=(rule_font_family, 10))
        self.rule_label.pack(side=tk.LEFT, padx=(0, 5))  # 左边距为0，右边距为5，与数据表格左对齐
        self.traffic_rule_var = tk.StringVar(value=traffic_rule)
        
        # 配置单选按钮字体（使用 Regular 字体，与数据表格一致）
        try:
            rule_style = ttk.Style()
            rule_style.configure('TrafficRule.TRadiobutton', font=(rule_font_family, 10))
        except:
            rule_style = None
        
        self.rule_right = ttk.Radiobutton(rule_frame, text=t('right_hand_rule'), variable=self.traffic_rule_var, 
                                     value='right', command=self.on_rule_change)
        if rule_style:
            try:
                self.rule_right.configure(style='TrafficRule.TRadiobutton')
            except:
                try:
                    self.rule_right.configure(font=(rule_font_family, 10))
                except:
                    pass
        else:
            try:
                self.rule_right.configure(font=(rule_font_family, 10))
            except:
                pass
        self.rule_right.pack(side=tk.LEFT, padx=5)
        
        self.rule_left = ttk.Radiobutton(rule_frame, text=t('left_hand_rule'), variable=self.traffic_rule_var, 
                                    value='left', command=self.on_rule_change)
        if rule_style:
            try:
                self.rule_left.configure(style='TrafficRule.TRadiobutton')
            except:
                try:
                    self.rule_left.configure(font=(rule_font_family, 10))
                except:
                    pass
        else:
            try:
                self.rule_left.configure(font=(rule_font_family, 10))
            except:
                pass
        self.rule_left.pack(side=tk.LEFT, padx=5)
        
        # 保存表头标签引用，以便在交通规则改变时更新
        self.heading_labels = []
        # 获取 Medium 字体（用于列标题）
        try:
            import ui_utils
            heading_font_family = ui_utils.get_font_family_medium()
        except:
            heading_font_family = font_family  # 如果获取失败，使用主字体
        
        # 配置列标题样式（使用 Medium 字体）
        try:
            heading_style = ttk.Style()
            # 为每个列标题创建唯一的样式名称，避免冲突
            heading_style.configure('TableHeading.TLabel', font=(heading_font_family, 10))
        except:
            heading_style = None
        
        for column in range(columns):
            label = ttk.Label(self, text=headings[column])
            # 配置列标题使用 Medium 字重
            if heading_style:
                try:
                    label.configure(style='TableHeading.TLabel')
                except:
                    # 如果样式配置失败，直接设置字体
                    try:
                        label.configure(font=(heading_font_family, 10))
                    except:
                        pass
            else:
                # 如果样式对象创建失败，直接设置字体
                try:
                    label.configure(font=(heading_font_family, 10))
                except:
                    pass
            # 表头对齐：第一列（进口编号）左对齐，其他列也左对齐以匹配Entry
            if column == 0:
                label.grid(row=3, column=column, padx=5, pady=5, sticky='w')
            else:
                label.grid(row=3, column=column, padx=5, pady=5, sticky='w')
            self.heading_labels.append(label)

        # 生成数据行（根据路数）
        # 计算方位角默认值（0-360度平均分布）
        angle_step = 360.0 / num_entries
        default_angles = [i * angle_step for i in range(num_entries)]
        
        for row in range(1, num_entries + 1):
            current_row = []
            # 获取 Regular 字体（用于行标题，与数据表格一致）
            try:
                import ui_utils
                row_font_family = ui_utils.get_font_family()
            except:
                row_font_family = font_family if 'font_family' in locals() else 'Arial'
            
            direction = ttk.Label(self, text=f"{t('entry')}{row}")
            # 配置行标题字体（使用 Regular 字体，与数据表格一致）
            try:
                row_style = ttk.Style()
                row_style.configure('RowLabel.TLabel', font=(row_font_family, 10))
                direction.configure(style='RowLabel.TLabel')
            except:
                try:
                    direction.configure(font=(row_font_family, 10))
                except:
                    pass
            direction.grid(row=row+3, column=0, padx=5, pady=5, sticky='w')  # row+3因为表头在row=3
            self.row_labels.append(direction)  # 保存行标题引用，用于语言切换
            for column in range(1, columns):
                entry = ttk.Entry(self, width=10)
                entry.bind('<KeyRelease>', self.mark_modified)
                # 数据框对齐：与表头保持一致，使用相同的padx和sticky
                entry.grid(row=row+3, column=column, padx=5, pady=5, sticky='w')  # row+3因为表头在row=3
                # 如果是方位角列（第3列，索引为2），设置默认值
                if column == 2:  # 方位角列（column 0是进口编号，column 1是进口名称，column 2是方位角）
                    default_angle = default_angles[row - 1]  # row从1开始，所以减1
                    entry.insert(0, str(int(default_angle)) if default_angle == int(default_angle) else str(default_angle))
                current_row.append(entry)
            self._widgets.append(current_row)
    
    def on_rule_change(self):
        """交通规则改变时的回调函数"""
        self.traffic_rule = self.traffic_rule_var.get()
        # 保存配置（延迟导入config模块）
        try:
            import config
            config.save_config(table=self)
        except:
            pass
        # 如果是4路交叉口，更新表头
        if self.num_entries == 4 and len(self.heading_labels) >= 7:
            # 获取 Medium 字体（用于列标题）
            try:
                import ui_utils
                heading_font_family = ui_utils.get_font_family_medium()
            except:
                try:
                    import ui_utils
                    heading_font_family = ui_utils.get_font_family()
                except:
                    heading_font_family = None
            
            # 表头顺序：['进口编号', '进口名称', '方位角', '掉头', '左转/右转', '直行', '右转/左转']
            if self.traffic_rule == 'left':
                # 左行规则：掉头、右转、直行、左转
                if len(self.heading_labels) >= 7:
                    self.heading_labels[3].config(text=t('u_turn'))
                    self.heading_labels[4].config(text=t('right_turn'))
                    self.heading_labels[5].config(text=t('straight'))
                    self.heading_labels[6].config(text=t('left_turn'))
                    # 确保字体正确应用
                    if heading_font_family:
                        for i in [3, 4, 5, 6]:
                            try:
                                self.heading_labels[i].configure(font=(heading_font_family, 10))
                            except:
                                pass
            else:
                # 右行规则：掉头、左转、直行、右转
                if len(self.heading_labels) >= 7:
                    self.heading_labels[3].config(text=t('u_turn'))
                    self.heading_labels[4].config(text=t('left_turn'))
                    self.heading_labels[5].config(text=t('straight'))
                    self.heading_labels[6].config(text=t('right_turn'))
                    # 确保字体正确应用
                    if heading_font_family:
                        for i in [3, 4, 5, 6]:
                            try:
                                self.heading_labels[i].configure(font=(heading_font_family, 10))
                            except:
                                pass
        self.mark_modified()
    
    def mark_modified(self, event=None):
        """标记数据已修改"""
        self.is_modified = True
        update_window_title()
    
    def update_language(self):
        """更新表格中的语言文本"""
        try:
            # 更新交通规则标签
            try:
                if hasattr(self, 'rule_label') and self.rule_label:
                    self.rule_label.config(text=t('traffic_rule'))
            except:
                pass
            try:
                if hasattr(self, 'rule_right') and self.rule_right:
                    self.rule_right.config(text=t('right_hand_rule'))
            except:
                pass
            try:
                if hasattr(self, 'rule_left') and self.rule_left:
                    self.rule_left.config(text=t('left_hand_rule'))
            except:
                pass
            
            # 更新表头
            try:
                # 获取 Medium 字体（用于列标题）
                try:
                    import ui_utils
                    heading_font_family = ui_utils.get_font_family_medium()
                except:
                    try:
                        import ui_utils
                        heading_font_family = ui_utils.get_font_family()
                    except:
                        heading_font_family = None
                
                if hasattr(self, 'heading_labels') and self.heading_labels and len(self.heading_labels) >= 3:
                    if len(self.heading_labels) > 0 and self.heading_labels[0]:
                        self.heading_labels[0].config(text=t('entry_number'))
                        if heading_font_family:
                            try:
                                self.heading_labels[0].configure(font=(heading_font_family, 10))
                            except:
                                pass
                    if len(self.heading_labels) > 1 and self.heading_labels[1]:
                        self.heading_labels[1].config(text=t('entry_name'))
                        if heading_font_family:
                            try:
                                self.heading_labels[1].configure(font=(heading_font_family, 10))
                            except:
                                pass
                    if len(self.heading_labels) > 2 and self.heading_labels[2]:
                        self.heading_labels[2].config(text=t('angle'))
                        if heading_font_family:
                            try:
                                self.heading_labels[2].configure(font=(heading_font_family, 10))
                            except:
                                pass
                    
                    # 如果是4路交叉口，更新流向表头
                    if self.num_entries == 4 and len(self.heading_labels) >= 7:
                        if self.traffic_rule == 'left':
                            if len(self.heading_labels) > 3 and self.heading_labels[3]:
                                self.heading_labels[3].config(text=t('u_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[3].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 4 and self.heading_labels[4]:
                                self.heading_labels[4].config(text=t('right_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[4].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 5 and self.heading_labels[5]:
                                self.heading_labels[5].config(text=t('straight'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[5].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 6 and self.heading_labels[6]:
                                self.heading_labels[6].config(text=t('left_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[6].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                        else:
                            if len(self.heading_labels) > 3 and self.heading_labels[3]:
                                self.heading_labels[3].config(text=t('u_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[3].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 4 and self.heading_labels[4]:
                                self.heading_labels[4].config(text=t('left_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[4].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 5 and self.heading_labels[5]:
                                self.heading_labels[5].config(text=t('straight'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[5].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                            if len(self.heading_labels) > 6 and self.heading_labels[6]:
                                self.heading_labels[6].config(text=t('right_turn'))
                                if heading_font_family:
                                    try:
                                        self.heading_labels[6].configure(font=(heading_font_family, 10))
                                    except:
                                        pass
                    else:
                        # 非4路交叉口，更新流线列标题（流线X_X, 流线X_X-1, 流线X_X-2, ...）
                        # 列标题顺序：entry_number(0), entry_name(1), angle(2), flow_line(3), flow_line_n(4), ...
                        if len(self.heading_labels) > 3:
                            # 第4列：流线X_X（掉头）
                            try:
                                if self.heading_labels[3]:
                                    self.heading_labels[3].config(text=t('flow_line'))
                                    if heading_font_family:
                                        try:
                                            self.heading_labels[3].configure(font=(heading_font_family, 10))
                                        except:
                                            pass
                            except:
                                pass
                        # 更新其他流线列标题（流线X_X-1, 流线X_X-2, ...）
                        for i in range(1, self.num_entries):
                            col_idx = 3 + i  # 从第4列开始（索引3）
                            if col_idx < len(self.heading_labels) and self.heading_labels[col_idx]:
                                try:
                                    self.heading_labels[col_idx].config(text=t('flow_line_n', n=i))
                                    if heading_font_family:
                                        try:
                                            self.heading_labels[col_idx].configure(font=(heading_font_family, 10))
                                        except:
                                            pass
                                except:
                                    pass
            except Exception as e:
                print(f"更新表头语言失败: {e}")
            
            # 更新行标题（进口1、进口2、进口3等）
            try:
                if hasattr(self, 'row_labels') and self.row_labels:
                    for idx, row_label in enumerate(self.row_labels, start=1):
                        if row_label:
                            try:
                                # 检查标签是否仍然有效
                                if hasattr(row_label, 'winfo_exists') and row_label.winfo_exists():
                                    row_label.config(text=f"{t('entry')}{idx}")
                            except:
                                pass
            except:
                pass
            
            # 更新重要提醒标题
            try:
                if hasattr(self, 'notice_title_label') and self.notice_title_label:
                    self.notice_title_label.config(text=t('important_notice'))
            except:
                pass
            
            # 更新提示信息（完整文本）
            try:
                if hasattr(self, 'notice_label') and self.notice_label:
                    notice_text = t('notice_content').replace('\r\n', '\n').replace('\r', '\n')
                    # 清理连续的多个换行符，只保留一个
                    while '\n\n' in notice_text:
                        notice_text = notice_text.replace('\n\n', '\n')
                    # 防止在 "2." 后面换行：将 "2. " 替换为 "2.\u00A0"（非断行空格）
                    notice_text = notice_text.replace('2. ', '2.\u00A0')
                    
                    # 优化换行：确保标点符号不在行首
                    def prevent_punctuation_at_line_start(text):
                        """防止标点符号出现在行首"""
                        # 中英文标点符号列表
                        punctuation_chars = [
                            # 中文标点
                            '，', '。', '、', '；', '：', '？', '！', '…', '—', '～', '·',
                            '"', '"', ''', ''', '（', '）', '【', '】', '《', '》', '〈', '〉', '「', '」', '『', '』',
                            # 英文标点
                            ',', '.', ';', ':', '?', '!', '-', '—', '(', ')', '[', ']', '{', '}', '"', "'"
                        ]
                        
                        # 在标点符号前插入非断行空格
                        result = text
                        for punct in punctuation_chars:
                            # 在空格后的标点符号前插入非断行空格
                            result = re.sub(r' ' + re.escape(punct), '\u00A0' + punct, result)
                            # 在行首的标点符号前插入非断行空格（但保留原有的换行）
                            result = re.sub(r'^' + re.escape(punct), '\u00A0' + punct, result, flags=re.MULTILINE)
                        
                        return result
                    
                    notice_text = prevent_punctuation_at_line_start(notice_text)
                    self.notice_label.config(text=notice_text)
            except:
                pass
            
            # 更新wraplength以适应新的文本
            try:
                if hasattr(self, 'update_notice_wraplength') and self.update_notice_wraplength:
                    self.after_idle(self.update_notice_wraplength)
            except:
                pass
        except Exception as e:
            print(f"更新表格语言时出错: {e}")

    def sort_by_angle(self):
        """根据归一化后的角度对所有进口数据进行排序，并更新UI显示"""
        if not self.data or 'angles' not in self.data or len(self.data['angles']) == 0:
            return
        
        # 获取所有数据列
        keys = list(self.data.keys())
        num_entries = len(self.data['angles'])
        
        # 创建包含所有数据的元组列表，每个元组代表一行数据
        # 元组格式：(归一化角度, 原始索引, names值, angles值, flow_0值, flow_1值, ...)
        data_rows = []
        for i in range(num_entries):
            try:
                angle = float(self.data['angles'][i])
                normalized_angle = normalize_angle(angle)
            except (ValueError, TypeError):
                normalized_angle = 0.0
            
            row_data = [normalized_angle]  # 第一个元素是归一化角度，用于排序
            row_data.append(i)  # 第二个元素是原始索引
            # 添加所有列的值
            for key in keys:
                if i < len(self.data[key]):
                    row_data.append(self.data[key][i])
                else:
                    row_data.append('')
            data_rows.append(row_data)
        
        # 根据归一化角度排序
        data_rows.sort(key=lambda x: x[0])
        
        # 重新组织排序后的数据
        for key in keys:
            self.data[key] = []
        
        for row_data in data_rows:
            # row_data格式: [归一化角度, 原始索引, names值, angles值, flow_0值, flow_1值, ...]
            # 跳过前两个元素（归一化角度和原始索引），从索引2开始是实际数据
            for idx, key in enumerate(keys):
                if idx + 2 < len(row_data):
                    self.data[key].append(row_data[idx + 2])
                else:
                    self.data[key].append('')
        
        # 更新UI显示（显示归一化后的角度）
        keys = list(self.data.keys())
        num_rows = min(len(self._widgets), len(self.data[keys[0]]) if keys else 0)
        for row in range(num_rows):
            for i, widget in enumerate(self._widgets[row]):
                if i < len(keys):
                    widget.delete(0, tk.END)
                    value = self.data[keys[i]][row] if row < len(self.data[keys[i]]) else ''
                    # 如果是角度列（索引为2），显示归一化后的值
                    if i == 2 and value:
                        try:
                            normalized = normalize_angle(value)
                            value = str(int(normalized)) if normalized == int(normalized) else str(normalized)
                        except:
                            pass
                    widget.insert(0, str(value))

    def set_data(self, data):
        # 清空字典
        for key in self.data:
            self.data[key].clear()
        for key in self.raw_data:
            self.raw_data[key].clear()

        # 保存原始数据（用于文件保存）- 保持用户输入的原始角度值和顺序
        for key in data:
            if key in self.raw_data:
                if isinstance(data[key], list):
                    self.raw_data[key] = [str(v) for v in data[key]]
                else:
                    self.raw_data[key] = [str(data[key])]
        
        # 设置处理后的数据（归一化角度）
        keys = list(data.keys())
        for key in keys:
            if key in self.data:
                if key == 'angles':
                    # 归一化角度
                    normalized_angles = []
                    for angle in data[key]:
                        try:
                            normalized = normalize_angle(angle)
                            normalized_angles.append(str(int(normalized)) if normalized == int(normalized) else str(normalized))
                        except:
                            normalized_angles.append(str(angle))
                    self.data[key] = normalized_angles
                else:
                    if isinstance(data[key], list):
                        self.data[key] = [str(v) for v in data[key]]
                    else:
                        self.data[key] = [str(data[key])]
        
        # 排序数据
        self.sort_by_angle()
        
        # 从文件加载数据后，清除修改标记
        self.is_modified = False

    def get(self):
        keys = list(self.data.keys())
        # 清空字典
        for key in self.data:
            self.data[key].clear()
        for key in self.raw_data:
            self.raw_data[key].clear()

        # 从UI获取数据（用户输入的值，可能是归一化后的，也可能是新的原始值）
        for row in self._widgets:
            for i, widget in enumerate(row):
                if i < len(keys):
                    try:
                        # 检查 widget 是否仍然有效（没有被销毁）
                        widget.winfo_exists()
                        value = widget.get()
                    except (tk.TclError, AttributeError):
                        # 如果 widget 已被销毁，跳过或使用空值
                        value = ""
                    
                    # 保存到raw_data（用户输入的值作为原始值）
                    if keys[i] in self.raw_data:
                        self.raw_data[keys[i]].append(value)
                    # 如果是角度列，归一化后保存到data；否则直接保存
                    if keys[i] == 'angles':
                        try:
                            normalized = normalize_angle(value)
                            normalized_str = str(int(normalized)) if normalized == int(normalized) else str(normalized)
                            self.data[keys[i]].append(normalized_str)
                        except:
                            self.data[keys[i]].append(value)
                    else:
                        self.data[keys[i]].append(value)
        
        # 排序数据（基于归一化后的角度）
        self.sort_by_angle()


    def save_to_file(self):
        if self.file_name:
            # 先更新原始数据（从UI获取最新值）
            self.get()
            # 使用原始数据保存（保持用户输入的原始角度值和顺序）
            with open(self.file_name, 'w', encoding='utf-8') as file:
                for key, values in self.raw_data.items():
                    file.write(','.join(values) + '\n')
        else:
            print(t('file_no_save_target'))


