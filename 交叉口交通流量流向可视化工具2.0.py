import matplotlib.font_manager as fm
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox  
from matplotlib.text import TextPath
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# 显式导入PDF后端，确保PyInstaller打包时包含它
import matplotlib.backends.backend_pdf
import matplotlib.backends._backend_pdf_ps
# 显式导入SVG后端，确保PyInstaller打包时包含它
import matplotlib.backends.backend_svg
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import font as tkfont
import re
import platform
import os
import sys



plt.ioff()

# ==================== 几何参数常量 ====================
# 以下常量是经过调试得出的经验值，用于控制交叉口绘图的几何形状
INNER_RADIUS_COEFF = 25 * np.sqrt(35)  # 内圆半径系数
OUTER_RADIUS_COEFF = 100 * np.sqrt(7)  # 外圆半径系数
CENTER_OFFSET = 25  # 中心偏移量
ROAD_WIDTH_OFFSET = 25  # 道路宽度偏移量
MIDDLE_RADIUS_COEFF = 75 * np.sqrt(35)  # 中间半径系数（用于路径计算）

# 标注位置偏移量（相对于进口道中心线）
LABEL_OFFSET_U_TURN = 18  # 掉头标注偏移
LABEL_OFFSET_LEFT = 6     # 左转标注偏移
LABEL_OFFSET_STRAIGHT = -6  # 直行标注偏移
LABEL_OFFSET_RIGHT = -18    # 右转标注偏移

# 名称标注偏移
NAME_LABEL_OFFSET = 20

# 绘图参数
MAX_LINE_WIDTH = 10  # 最大线宽倍数
PLOT_XLIM = (-375, 375)  # 绘图X轴范围
PLOT_YLIM = (-375, 375)  # 绘图Y轴范围
FIGURE_SIZE = (10, 10)  # 图形尺寸
FIGURE_DPI = 100  # 图形分辨率

# 颜色配置（扩展到6种颜色以支持3-6路交叉口）
ENTRY_COLORS = ['red', '#27a5d6', '#d161a3', 'orange', 'green', 'purple']

# 转向类型配置（出口索引偏移量）
TURN_EXIT_OFFSET = {
    'left': 3,      # 左转：(i+3)%4
    'straight': 2,  # 直行：(i+2)%4
    'right': 1     # 右转：(i+1)%4
}

# ==================== GUI界面字体加载函数 ====================
def load_ui_font():
    """加载用于GUI界面的字体（优先使用嵌入字体）"""
    # 获取字体文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 优先使用嵌入的字体文件
    embedded_fonts = [
        os.path.join(base_path, 'fonts', 'SourceHanSansCN-Regular.otf'),
        os.path.join(base_path, 'fonts', 'SourceHanSansCN-Regular.ttf'),
        os.path.join(base_path, 'fonts', 'NotoSansCJK-Regular.ttf'),
        os.path.join(base_path, 'fonts', 'wqy-microhei.ttc'),
    ]
    
    for font_path in embedded_fonts:
        if os.path.exists(font_path):
            return font_path
    
    # 回退到系统字体
    system = platform.system()
    if system == 'Windows':
        # Windows系统优先使用微软雅黑
        system_fonts = ['Microsoft YaHei UI', 'Microsoft YaHei', 'SimHei']
        for font_name in system_fonts:
            try:
                # 尝试创建字体对象来验证字体是否存在
                test_font = tkfont.Font(family=font_name, size=10)
                actual = test_font.actual()
                # 检查字体是否真的加载成功（避免回退到宋体）
                if actual.get('family') == font_name or 'YaHei' in actual.get('family', '') or 'Hei' in actual.get('family', ''):
                    return font_name
            except:
                continue
        # 如果都失败，返回微软雅黑（让系统自动选择）
        return 'Microsoft YaHei UI'
    elif system == 'Darwin':
        return 'PingFang SC'  # macOS
    else:
        return 'WenQuanYi Micro Hei'  # Linux
    
    return 'Arial'  # 最终回退

def setup_modern_style(root):
    """设置现代化的界面样式"""
    style = ttk.Style()
    
    # 设置主题（根据系统选择）
    system = platform.system()
    if system == 'Windows':
        try:
            style.theme_use('vista')  # Windows Vista/7/10/11 风格
        except:
            style.theme_use('clam')  # 回退到clam主题
    else:
        style.theme_use('clam')  # 跨平台现代风格
    
    # 获取字体
    ui_font_path = load_ui_font()
    
    # Tkinter 不支持直接从文件加载字体，需要使用系统字体名称
    # 如果返回的是字体文件路径，尝试使用系统字体
    font_family = None
    system = platform.system()
    
    if os.path.exists(ui_font_path):
        # 如果是字体文件路径，直接使用系统字体（Windows上优先使用微软雅黑）
        if system == 'Windows':
            # 尝试微软雅黑
            try:
                test_font = tkfont.Font(family="Microsoft YaHei UI", size=10)
                actual = test_font.actual()
                if actual.get('family') == 'Microsoft YaHei UI' or 'YaHei' in str(actual.get('family', '')):
                    font_family = 'Microsoft YaHei UI'
                else:
                    font_family = 'Microsoft YaHei'
            except:
                font_family = 'Microsoft YaHei'
        elif system == 'Darwin':
            font_family = 'PingFang SC'
        else:
            font_family = 'WenQuanYi Micro Hei'
    else:
        # 使用系统字体名称
        font_family = ui_font_path
        # 验证字体是否存在
        try:
            test_font = tkfont.Font(family=font_family, size=10)
            actual = test_font.actual()
            # 如果字体不存在，回退到默认字体
            if system == 'Windows':
                font_family = 'Microsoft YaHei UI'
            elif system == 'Darwin':
                font_family = 'PingFang SC'
            else:
                font_family = 'WenQuanYi Micro Hei'
        except:
            if system == 'Windows':
                font_family = 'Microsoft YaHei UI'
            elif system == 'Darwin':
                font_family = 'PingFang SC'
            else:
                font_family = 'WenQuanYi Micro Hei'
    
    # 配置默认字体
    try:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=font_family, size=10)
        
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=font_family, size=10)
        
        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family=font_family, size=10)
    except Exception as e:
        print(f"配置默认字体失败: {e}")
    
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
    
    # 配置主窗口背景
    try:
        root.configure(bg='#f5f5f5')
    except:
        pass
    
    # 更新全局字体变量
    global GUI_FONT_FAMILY
    GUI_FONT_FAMILY = font_family
    
    return font_family

# ==================== 跨平台字体查找函数（用于matplotlib绘图）====================
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

# 全局变量：存储GUI界面使用的字体族名称
GUI_FONT_FAMILY = None

class Table(tk.Frame):
    def __init__(self, parent, num_entries=4, traffic_rule='right'):
        tk.Frame.__init__(self, parent, bg='white', relief='flat', padx=10, pady=10)
        self.num_entries = num_entries
        self.traffic_rule = traffic_rule  # 'right' 或 'left'，默认为右行规则
        self._widgets = []
        self.file_name = None
        self.is_modified = False
        
        # 初始化数据结构：names, angles, flow_0, flow_1, ..., flow_{N-1}
        self.data = {
            'names': [],
            'angles': []
        }
        for i in range(num_entries):
            self.data[f'flow_{i}'] = []
        
        # 生成表头
        headings = ['进口编号', '进口名称', '方位角']
        # 根据路数生成流向列标题
        if num_entries == 4:
            # 4路交叉口使用直观的表头
            # 左行规则下：掉头、右转、直行、左转（顺时针顺序）
            # 右行规则下：掉头、左转、直行、右转（逆时针顺序）
            if traffic_rule == 'left':
                headings.extend(['掉头', '右转', '直行', '左转'])
            else:
                headings.extend(['掉头', '左转', '直行', '右转'])
        else:
            # 其他路数使用流线X_Y格式
            # 对于每个进口X，流向顺序是：流线X_X, 流线X_X-1, ..., 流线X_1
            # 表头显示为通用格式，其中X表示当前行的进口编号
            for i in range(num_entries):
                # 计算出口编号：X, X-1, X-2, ..., 1（需要规整化）
                # 对于表头，我们显示相对位置：X, X-1, X-2, ..., X-(N-1)
                if i == 0:
                    headings.append('流线X_X')  # 掉头
                else:
                    headings.append(f'流线X_X-{i}')  # 其他流向
        
        columns = len(headings)
        
        # 添加方位角提示标签（醒目提示）- 在计算完列数后添加，以便正确设置columnspan
        # 使用全局字体变量
        global GUI_FONT_FAMILY
        font_family = GUI_FONT_FAMILY if GUI_FONT_FAMILY else 'Microsoft YaHei UI'
        notice_label = tk.Label(self, 
                                text="⚠ 注意：'方位角'以正东方向为0度，逆时针增加。例如：0度 = 正东，90度 = 正北，180度 = 正西，270度 = 正南。",
                                bg='#fff3cd',  # 黄色背景
                                fg='#856404',  # 深黄色文字
                                font=(font_family, 9, 'bold'),
                                padx=10,
                                pady=8,
                                relief='solid',
                                borderwidth=1,
                                justify='left')
        notice_label.grid(row=0, column=0, columnspan=columns, padx=5, pady=(5, 10), sticky='ew')
        
        # 添加交通规则选择控件
        rule_frame = tk.Frame(self, bg='white')
        rule_frame.grid(row=1, column=0, columnspan=columns, padx=5, pady=5, sticky='w')
        tk.Label(rule_frame, text="交通规则：", bg='white').pack(side=tk.LEFT, padx=5)
        self.traffic_rule_var = tk.StringVar(value=traffic_rule)
        rule_right = ttk.Radiobutton(rule_frame, text="右行规则", variable=self.traffic_rule_var, 
                                     value='right', command=self.on_rule_change)
        rule_right.pack(side=tk.LEFT, padx=5)
        rule_left = ttk.Radiobutton(rule_frame, text="左行规则", variable=self.traffic_rule_var, 
                                    value='left', command=self.on_rule_change)
        rule_left.pack(side=tk.LEFT, padx=5)
        
        # 保存表头标签引用，以便在交通规则改变时更新
        self.heading_labels = []
        for column in range(columns):
            label = ttk.Label(self, text=headings[column])
            label.grid(row=2, column=column, padx=5, pady=5, sticky='w')  # 改为row=2，因为提示标签和规则选择占用了row=0和row=1
            self.heading_labels.append(label)

        # 生成数据行（根据路数）
        # 计算方位角默认值（0-360度平均分布）
        angle_step = 360.0 / num_entries
        default_angles = [i * angle_step for i in range(num_entries)]
        
        for row in range(1, num_entries + 1):
            current_row = []
            direction = ttk.Label(self, text=f'进口{row}')
            direction.grid(row=row+2, column=0, padx=5, pady=5, sticky='w')  # row+2因为表头在row=2
            for column in range(1, columns):
                entry = ttk.Entry(self, width=10)
                entry.bind('<KeyRelease>', self.mark_modified)
                entry.grid(row=row+2, column=column, padx=5, pady=5)  # row+2因为表头在row=2
                # 如果是方位角列（第3列，索引为2），设置默认值
                if column == 2:  # 方位角列（column 0是进口编号，column 1是进口名称，column 2是方位角）
                    default_angle = default_angles[row - 1]  # row从1开始，所以减1
                    entry.insert(0, str(int(default_angle)) if default_angle == int(default_angle) else str(default_angle))
                current_row.append(entry)
            self._widgets.append(current_row)
    
    def on_rule_change(self):
        """交通规则改变时的回调函数"""
        self.traffic_rule = self.traffic_rule_var.get()
        # 如果是4路交叉口，更新表头
        if self.num_entries == 4 and len(self.heading_labels) >= 7:
            # 表头顺序：['进口编号', '进口名称', '方位角', '掉头', '左转/右转', '直行', '右转/左转']
            if self.traffic_rule == 'left':
                # 左行规则：掉头、右转、直行、左转
                if len(self.heading_labels) >= 7:
                    self.heading_labels[3].config(text='掉头')
                    self.heading_labels[4].config(text='右转')
                    self.heading_labels[5].config(text='直行')
                    self.heading_labels[6].config(text='左转')
            else:
                # 右行规则：掉头、左转、直行、右转
                if len(self.heading_labels) >= 7:
                    self.heading_labels[3].config(text='掉头')
                    self.heading_labels[4].config(text='左转')
                    self.heading_labels[5].config(text='直行')
                    self.heading_labels[6].config(text='右转')
        self.mark_modified()
    
    def mark_modified(self, event=None):
        """标记数据已修改"""
        self.is_modified = True
        update_window_title()

    def set_data(self, data):
        # 清空字典
        for key in self.data:
            self.data[key].clear()

        # 设置新数据
        self.data = data
        keys = list(self.data.keys())
        # 确保数据长度匹配
        num_rows = min(len(self._widgets), len(self.data[keys[0]]) if keys else 0)
        for row in range(num_rows):
            for i, widget in enumerate(self._widgets[row]):
                if i < len(keys):
                    widget.delete(0, tk.END)
                    value = self.data[keys[i]][row] if row < len(self.data[keys[i]]) else ''
                    widget.insert(0, str(value))
        
        # 从文件加载数据后，清除修改标记
        self.is_modified = False

    def get(self):
        keys = list(self.data.keys())
        # 清空字典
        for key in self.data:
            self.data[key].clear()

        for row in self._widgets:
            for i, widget in enumerate(row):
                if i < len(keys):
                    self.data[keys[i]].append(widget.get())


    def save_to_file(self):
        if self.file_name:
            with open(self.file_name, 'w') as file:
                for key, values in self.data.items():
                    file.write(','.join(values) + '\n')
        else:
            print("No file to save to. Please load a file first.")

def adjust_window_size(window):
    """调整窗口大小以适应内容，并居中显示"""
    # 更新窗口以确保正确计算大小
    window.update_idletasks()
    window.update()
    
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
    
    # 计算居中位置
    x = (screen_width - req_width) // 2
    y = (screen_height - req_height) // 2
    
    # 确保窗口不会超出屏幕边界
    x = max(0, min(x, screen_width - req_width))
    y = max(0, min(y, screen_height - req_height))
    
    # 设置窗口geometry并居中
    window.geometry(f"{req_width}x{req_height}+{x}+{y}")
    window.update_idletasks()

def center_window(window):
    """将窗口居中显示在当前显示器上（保留旧函数以兼容）"""
    adjust_window_size(window)

def select_intersection_type():
    """选择交叉口类型或读取文件"""
    # 直接创建一个独立的对话框窗口
    dialog = tk.Tk()
    dialog.title("选择交叉口类型")
    dialog.resizable(False, False)
    
    # 立即隐藏窗口，避免闪现
    dialog.withdraw()
    
    # 先设置一个临时位置（屏幕外），避免在左上角闪现
    dialog.geometry("1x1+-10000+-10000")
    
    # 为对话框也应用字体设置
    setup_modern_style(dialog)
    
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
    
    # 创建主框架
    main_frame = tk.Frame(dialog, padx=40, pady=40, bg='white', relief='flat')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 标题
    global GUI_FONT_FAMILY
    font_family = GUI_FONT_FAMILY if GUI_FONT_FAMILY else 'Microsoft YaHei UI'
    title_label = tk.Label(main_frame, text="请选择交叉口类型或读取文件：", 
                          font=(font_family, 14, 'bold'), pady=20, bg='white', fg='#333333')
    title_label.pack()
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack()
    
    # 创建按钮（使用ttk.Button以获得现代化样式）
    btn1 = ttk.Button(button_frame, text="3路交叉口", width=20, 
                     command=lambda: on_choice(3))
    btn1.pack(pady=6)
    
    btn2 = ttk.Button(button_frame, text="4路交叉口", width=20, 
                     command=lambda: on_choice(4))
    btn2.pack(pady=6)
    
    btn3 = ttk.Button(button_frame, text="5路交叉口", width=20, 
                     command=lambda: on_choice(5))
    btn3.pack(pady=6)
    
    btn4 = ttk.Button(button_frame, text="6路交叉口", width=20, 
                     command=lambda: on_choice(6))
    btn4.pack(pady=6)
    
    btn5 = ttk.Button(button_frame, text="读取数据文件", width=20, 
                     command=lambda: on_choice('load_file'))
    btn5.pack(pady=6)
    
    # 更新窗口以确保正确计算大小
    dialog.update_idletasks()
    
    # 在隐藏状态下设置居中位置
    center_window(dialog)
    
    # 显示窗口（此时已经在正确位置了）
    dialog.deiconify()
    
    # 确保窗口在最前面（不使用topmost，避免闪烁）
    dialog.lift()
    dialog.focus_force()
    
    # 等待用户选择
    dialog.mainloop()
    
    return result['choice']

def update_window_title():
    """更新主窗口标题"""
    if not hasattr(update_window_title, 'root') or update_window_title.root is None:
        return
    
    if table.file_name:
        # 去掉文件扩展名显示
        file_name = os.path.basename(table.file_name)
        file_name_without_ext = os.path.splitext(file_name)[0]
        if table.is_modified:
            update_window_title.root.title(f"{file_name_without_ext} - 未保存")
        else:
            update_window_title.root.title(file_name_without_ext)
    else:
        if table.is_modified:
            update_window_title.root.title("交叉口交通流量流向可视化工具 - 未保存")
        else:
            update_window_title.root.title("交叉口交通流量流向可视化工具")

def load_data_from_file(file_name, table_instance, root_instance):
    """从文件加载数据的内部函数"""
    global table, plot_button
    
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
    
    if lines is None:
        messagebox.showerror("错误", f"无法读取文件 {file_name}，请检查文件编码。")
        return
    
    if len(lines) == 0:
        messagebox.showerror("错误", "文件为空。")
        return
    
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
                messagebox.showerror("错误", "交叉口路数错误，请核对数据后再读取")
                return
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
                                messagebox.showerror("错误", f"无法从数据推断路数，推断结果为{num_entries}路，不在有效范围内（3-6路）")
                                return
                            data_lines = lines  # 第一行也是数据
                        else:
                            messagebox.showerror("错误", "文件格式不正确，无法推断交叉口路数。")
                            return
                    else:
                        # 第一行不是数据，从第二行开始
                        data_lines = lines[1:]
                        if len(data_lines) > 0:
                            first_data_line = data_lines[0].strip()
                            if first_data_line and ',' in first_data_line:
                                values = [v.strip() for v in first_data_line.split(',')]
                                num_entries = len(values)
                                if num_entries < 3 or num_entries > 6:
                                    messagebox.showerror("错误", f"无法从数据推断路数，推断结果为{num_entries}路，不在有效范围内（3-6路）")
                                    return
                            else:
                                messagebox.showerror("错误", "文件格式不正确，无法推断交叉口路数。")
                                return
                        else:
                            messagebox.showerror("错误", "文件格式不正确，无法推断交叉口路数。")
                            return
                else:
                    messagebox.showerror("错误", "文件格式不正确，无法推断交叉口路数。")
                    return
        
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
            # 销毁旧表格
            table_instance.destroy()
            # 查找按钮框架，确保新表格pack在按钮框架之前
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
            # 创建新表格（传递交通规则）
            table_instance = Table(root_instance, num_entries=num_entries, traffic_rule=traffic_rule)
            # 如果找到按钮框架，确保表格pack在它之前
            if button_frame:
                table_instance.pack(before=button_frame)
            else:
                table_instance.pack()
            # 更新全局table引用
            table = table_instance
            # 重新绑定按钮
            if 'plot_button' in globals():
                plot_button.config(command=lambda: plot_traffic_flow(table))
            # 调整窗口大小以适应新表格
            root_instance.update_idletasks()
            root_instance.update()
            adjust_window_size(root_instance)
        
        # 设置数据
        table_instance.set_data(data)
        table_instance.file_name = file_name
        # 更新交通规则（即使表格已存在）
        table_instance.traffic_rule = traffic_rule
        # 更新交通规则选择控件
        if hasattr(table_instance, 'traffic_rule_var'):
            table_instance.traffic_rule_var.set(traffic_rule)
        table_instance.is_modified = False
        if hasattr(update_window_title, 'root'):
            update_window_title()
        # 调整窗口大小以适应内容
        root_instance.update_idletasks()
        root_instance.update()
        adjust_window_size(root_instance)
        return True, table_instance
        
    except Exception as e:
        messagebox.showerror("错误", f"解析数据时出错：{str(e)}")
        return False, table_instance

def on_load_data_click():
    """读取数据文件"""
    global table, plot_button, root
    
    file_name = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_name:
        success, new_table = load_data_from_file(file_name, table, root)
        if success:
            table = new_table
            # 调整窗口大小以适应新内容
            adjust_window_size(root)
            messagebox.showinfo("成功", f"数据加载成功！已识别为{table.num_entries}路交叉口。")

def on_save_data_click():
    """保存数据到当前文件"""
    table.get()
    if hasattr(table, 'file_name') and table.file_name:
        try:
            with open(table.file_name, 'w', encoding='utf-8') as file:
                # 写入第一行声明（包含交通规则）
                traffic_rule_text = '左' if table.traffic_rule == 'left' else '右'
                file.write(f'本交叉口为{table.num_entries}路交叉口，实行{traffic_rule_text}行通行规则。\n')
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
            update_window_title()
            messagebox.showinfo("成功", f"数据已保存到 {table.file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错：{str(e)}")
    else:
        # 如果没有文件名，调用另存为
        on_save_data_as_click()

def on_save_data_as_click():
    """数据另存为"""
    table.get()
    file_name = filedialog.asksaveasfilename(
        defaultextension='.txt',
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_name:
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                # 写入第一行声明（包含交通规则）
                traffic_rule_text = '左' if table.traffic_rule == 'left' else '右'
                file.write(f'本交叉口为{table.num_entries}路交叉口，实行{traffic_rule_text}行通行规则。\n')
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
            update_window_title()
            messagebox.showinfo("成功", f"数据已保存到 {file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错：{str(e)}")

def on_clear_data_click():
    """清空数据"""
    global table
    # 确认操作
    if messagebox.askyesno("确认", "确定要清空所有数据吗？"):
        # 清空所有输入框
        for row in table._widgets:
            for widget in row:
                widget.delete(0, tk.END)
        # 清除文件名和修改标记
        table.file_name = None
        table.is_modified = False
        update_window_title()
        messagebox.showinfo("成功", "数据已清空")

def on_new_file_click():
    """新建文件"""
    global table, root
    # 确认操作
    if table.is_modified:
        if not messagebox.askyesno("确认", "当前数据已修改，确定要新建文件吗？未保存的修改将丢失。"):
            return
    
    # 创建简单的对话框选择交叉口类型
    dialog = tk.Toplevel(root)
    dialog.title("选择交叉口类型")
    dialog.resizable(False, False)
    dialog.transient(root)  # 设置为父窗口的临时窗口
    dialog.grab_set()  # 模态对话框
    
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
    
    # 创建主框架
    main_frame = tk.Frame(dialog, padx=40, pady=40, bg='white', relief='flat')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 标题
    global GUI_FONT_FAMILY
    font_family = GUI_FONT_FAMILY if GUI_FONT_FAMILY else 'Microsoft YaHei UI'
    title_label = tk.Label(main_frame, text="请选择交叉口类型：", 
                          font=(font_family, 14, 'bold'), pady=20, bg='white', fg='#333333')
    title_label.pack()
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack()
    
    # 创建按钮（使用ttk.Button以获得现代化样式）
    btn1 = ttk.Button(button_frame, text="3路交叉口", width=20, 
                     command=lambda: on_choice(3))
    btn1.pack(pady=6)
    
    btn2 = ttk.Button(button_frame, text="4路交叉口", width=20, 
                     command=lambda: on_choice(4))
    btn2.pack(pady=6)
    
    btn3 = ttk.Button(button_frame, text="5路交叉口", width=20, 
                     command=lambda: on_choice(5))
    btn3.pack(pady=6)
    
    btn4 = ttk.Button(button_frame, text="6路交叉口", width=20, 
                     command=lambda: on_choice(6))
    btn4.pack(pady=6)
    
    # 居中显示对话框
    dialog.update_idletasks()
    dialog_width = dialog.winfo_reqwidth()
    dialog_height = dialog.winfo_reqheight()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - dialog_width) // 2
    y = (screen_height - dialog_height) // 2
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # 等待用户选择
    dialog.wait_window()
    
    choice = result['choice']
    if choice is None:
        return
    
    num_entries = choice
    
    # 如果路数不同，需要重新创建表格
    if table.num_entries != num_entries:
        # 销毁旧表格
        table.destroy()
        # 查找按钮框架
        button_frame = None
        for widget in root.winfo_children():
            if isinstance(widget, tk.Frame):
                children = widget.winfo_children()
                if children:
                    all_buttons = all(isinstance(child, (ttk.Button, tk.Button)) for child in children)
                    if all_buttons and len(children) > 0:
                        button_frame = widget
                        break
        # 创建新表格（默认右行规则）
        table = Table(root, num_entries=num_entries, traffic_rule='right')
        if button_frame:
            table.pack(before=button_frame)
        else:
            table.pack()
        # 重新绑定按钮
        if 'plot_button' in globals():
            plot_button.config(command=lambda: plot_traffic_flow(table))
        # 调整窗口大小
        root.update_idletasks()
        root.update()
        adjust_window_size(root)
    
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
    update_window_title()
    messagebox.showinfo("成功", f"已创建新的{num_entries}路交叉口数据表格")


def show_about():
    about_text = "交叉口交通流量流向可视化工具\nIntersection Traffic Flow Visualize\n\n版权所有 (C) \n\n本软件由 [江浦马保国] 开发，保留所有权利。\n欢迎复制、传播本软件。"
    messagebox.showinfo("关于", about_text)

def show_help():
    """显示帮助文档"""
    import webbrowser
    import sys
    from urllib.request import pathname2url
    
    # 获取帮助文档路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
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
                messagebox.showerror("错误", f"无法打开帮助文档：{str(e)}\n\n备用方法也失败：{str(e2)}\n\n帮助文档位置：{help_file}")
    else:
        messagebox.showerror("错误", f"未找到帮助文档文件。\n\n预期位置：{help_file}\n\n请确保帮助文档.html文件与程序在同一目录。")

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

def normalize_index(idx, num_entries):
    """
    规整化索引：如果idx < 1，则加上num_entries
    用于处理流线编号的循环（编号从1开始）
    
    参数:
        idx: 原始编号（可能小于1）
        num_entries: 交叉口路数
    
    返回:
        规整化后的编号（1到num_entries之间）
    """
    while idx < 1:
        idx += num_entries
    while idx > num_entries:
        idx -= num_entries
    return idx

# 定义函数，画直线宽度条
def draw_line_with_width(ax, start, end, width, color):
    # 将输入坐标转换为浮点数
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    # 计算线条的方向向量
    direction = end - start

    # 计算垂直于线条方向的单位向量
    normal = np.array([-direction[1], direction[0]])
    normal /= np.linalg.norm(normal)

    # 计算线条宽度的一半在垂直方向上的偏移量
    offset = normal * width / 2

    # 计算带宽度直线的四个顶点
    p1 = start - offset
    p2 = end - offset
    p3 = end + offset
    p4 = start + offset

    # 生成Path对象表示带宽直线
    vertices = np.vstack((p1, p2, p3, p4, p1))
    codes = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # 使用PathPatch添加带宽直线
    patch = PathPatch(path, edgecolor=color, facecolor=color, lw=0)
    ax.add_patch(patch)

# 定义函数，绘制实心箭头
def draw_arrow(ax, start, end, width, color):
    """
    绘制实心箭头
    
    参数:
        ax: matplotlib轴对象
        start: 箭头起点坐标 (x, y)
        end: 箭头终点坐标 (x, y)
        width: 箭头宽度（底边宽度）
        color: 箭头颜色
    """
    # 将输入坐标转换为numpy数组
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    
    # 计算箭头方向向量
    direction = end - start
    direction_norm = np.linalg.norm(direction)
    
    # 如果方向向量长度为0，不绘制箭头
    if direction_norm < 1e-10:
        return
    
    # 归一化方向向量
    direction_unit = direction / direction_norm
    
    # 计算垂直于方向的单位向量（用于构建箭头底边）
    normal = np.array([-direction_unit[1], direction_unit[0]])
    
    # 计算箭头三个顶点
    # 顶点：end（箭头尖端）
    # 底边两个点：在start位置，垂直于方向，宽度为width
    base_center = start
    half_width = width / 2
    base_left = base_center - normal * half_width
    base_right = base_center + normal * half_width
    
    # 构建箭头三角形（三个顶点：base_left, base_right, end）
    arrow_vertices = np.array([base_left, base_right, end, base_left])
    
    # 使用Polygon绘制实心箭头
    arrow_patch = patches.Polygon(arrow_vertices, closed=True, facecolor=color, edgecolor=color, linewidth=0)
    ax.add_patch(arrow_patch)

# 定义函数，画反向圆弧，平滑连接两条平行直线
def create_line(p1, p2):
    a = p2[1] - p1[1]
    b = p1[0] - p2[0]
    c = p2[0] * p1[1] - p1[0] * p2[1]
    return {'a': a, 'b': b, 'c': c}

def create_perpendicular_line(line, point):
    a, b = line['b'], -line['a']
    c = -(a * point[0] + b * point[1])
    return {'a': a, 'b': b, 'c': c}

def find_intersection(line1, line2):
    A1, B1, C1 = line1["a"], line1["b"], line1["c"]
    A2, B2, C2 = line2["a"], line2["b"], line2["c"]

    det = A2 * B1 - A1 * B2
    # 使用epsilon比较，避免浮点数精度问题
    if abs(det) < 1e-10:
        return None

    x = (C1 * B2 - C2 * B1) / det
    y = (A1 * C2 - A2 * C1) / det
    return np.array([x, y])

def arc_points(center, radius, start_angle, end_angle, num_points=100):
    start_angle = start_angle % 360
    end_angle = end_angle % 360

    if end_angle <= start_angle:
        end_angle += 360

    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return np.column_stack((x, y))

def transfor_arc_to_width_bar(arc, width, color='blue', ax=None, num_points=100):
    if ax is None:
        ax = plt.gca()

    # 计算圆弧的点集
    arc_points_outer = arc_points(arc["center"], arc["radius"] + 0.5 * width, arc["start_angle"], arc["end_angle"], num_points=num_points)
    arc_points_inner = arc_points(arc["center"], arc["radius"] - 0.5 * width, arc["start_angle"], arc["end_angle"], num_points=num_points)

    # 创建宽度条
    width_bar = np.vstack((arc_points_outer, arc_points_inner[::-1]))

    poly = patches.Polygon(width_bar, closed=True,  facecolor=color, edgecolor=color, linewidth=0)
    ax.add_patch(poly)

def are_collinear(p1, p2, p3, epsilon=1e-3):
    AB = np.array([p2[0] - p1[0], p2[1] - p1[1]])
    AC = np.array([p3[0] - p1[0], p3[1] - p1[1]])
    
    cross_product = AB[0] * AC[1] - AB[1] * AC[0]
    
    return abs(cross_product) < epsilon

def create_parallel_arcs_with_width(ax, p1, p2, p3, p4, width=0.1, color='red'):
    if are_collinear(p1, p2, p3):    # 如果共线，就用直线连接
        draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=width, color=color)
        return  # 共线情况已处理，直接返回
       
    # 计算中点Q和H1，H2
    Q = (p2 + p3) / 2
    H1 = (p2 + Q) / 2
    H2 = (p3 + Q) / 2

    # 计算与p1p2和p3p4垂直的线段L2和L3
    L2 = create_perpendicular_line(create_line(p1, p2), p2)
    L3 = create_perpendicular_line(create_line(p3, p4), p3)

    # 计算垂直于p2Q和p3Q的线段L22和L23
    L22 = create_perpendicular_line(create_line(p2, Q), H1)
    L23 = create_perpendicular_line(create_line(p3, Q), H2)

    # 计算两条弧线的圆心O1和O2
    O1 = find_intersection(L2, L22)
    O2 = find_intersection(L3, L23)

    # 检查交点是否存在（处理平行线情况）
    if O1 is None or O2 is None:
        # 如果无法找到圆心，使用直线连接作为备用方案
        draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=width, color=color)
        return

    # 计算两条弧线的半径r1和r2
    r1 = np.linalg.norm(O1 - p2)
    r2 = np.linalg.norm(O2 - p3)
    
    # 检查半径是否有效（避免零半径或异常大的半径）
    if r1 <= 0 or r2 <= 0 or r1 > 1e6 or r2 > 1e6:
        # 如果半径无效，使用直线连接作为备用方案
        draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=width, color=color)
        return

    # 计算起始角度和终止角度
    start_angle1 = np.degrees(np.arctan2(p2[1] - O1[1], p2[0] - O1[0]))
    end_angle1 = np.degrees(np.arctan2(Q[1] - O1[1], Q[0] - O1[0]))

    start_angle2 = np.degrees(np.arctan2(Q[1] - O2[1], Q[0] - O2[0]))
    end_angle2 = np.degrees(np.arctan2(p3[1] - O2[1], p3[0] - O2[0]))

    # 确保起始角度和终止角度正确
    vector_p2_tangent = np.array([np.cos(np.radians(start_angle1 + 90)), np.sin(np.radians(start_angle1 + 90))])
    vector_p2_p1 = p2 - p1
    vector_p3_tangent = np.array([np.cos(np.radians(end_angle2 - 90)), np.sin(np.radians(end_angle2 - 90))])
    vector_p3_p4 = p3 - p4

    if np.dot(vector_p2_tangent, vector_p2_p1) < 0:
        start_angle1, end_angle1 = end_angle1, start_angle1

    if np.dot(vector_p3_tangent, vector_p3_p4) < 0:
        start_angle2, end_angle2 = end_angle2, start_angle2

    arc11 ={
        "center": O1,
        "radius": r1,
        "start_angle": start_angle1,
        "end_angle": end_angle1,
    }

    arc22 ={
        "center": O2,
        "radius": r2,
        "start_angle": start_angle2,
        "end_angle": end_angle2,
    }    
    transfor_arc_to_width_bar(arc11, width=width, color=color, ax=ax)
    transfor_arc_to_width_bar(arc22, width=width, color=color, ax=ax)

# 定义函数，执行圆角操作，在两条直线间创建圆弧，并对直线修饰
def create_wide_line_with_arc(ax, p1, p2, p3, p4, start_angle,end_angle,line_width=0.1,color='red'):
    line_p1p2 = create_line(p1, p2)
    line_p3p4 = create_line(p3, p4)

    intersection = find_intersection(line_p1p2, line_p3p4)

    # 检查交点是否存在（处理平行线情况）
    if intersection is None:
        # 如果两条线平行，使用直线连接作为备用方案
        draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
        return

    dist_Op2 = np.linalg.norm(intersection - p2)
    dist_Op3 = np.linalg.norm(intersection - p3)
    
    # 检查距离是否有效（避免除0）
    if dist_Op2 < 1e-10 or dist_Op3 < 1e-10:
        # 如果距离过小，使用直线连接作为备用方案
        draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
        return
    
    if dist_Op2 < dist_Op3:
        # 检查向量长度，避免除0
        vec_p3_intersection = p3 - intersection
        vec_norm = np.linalg.norm(vec_p3_intersection)
        if vec_norm < 1e-10:
            # 如果向量长度为0，使用直线连接
            draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
            return
        
        candidates = [
            intersection + vec_p3_intersection / vec_norm * dist_Op2,
            intersection - vec_p3_intersection / vec_norm * dist_Op2
        ]

        p5 = min(candidates, key=lambda point: np.linalg.norm(point - p3))

        line_p2_perpendicular = create_perpendicular_line(line_p1p2, p2)
        line_p5_perpendicular = create_perpendicular_line(line_p3p4, p5)

        Q = find_intersection(line_p2_perpendicular, line_p5_perpendicular)

        # 检查Q是否存在
        if Q is None:
            # 如果无法找到圆心，使用直线连接
            draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
            return

        arc_center = Q
        arc_radius = np.linalg.norm(arc_center - p2)

        start_x=p3[0]
        end_x=p5[0]
        start_y=p3[1]
        end_y=p5[1]

    elif dist_Op2 == dist_Op3:
        p5 =p3
        line_p2_perpendicular = create_perpendicular_line(line_p1p2, p2)
        line_p5_perpendicular = create_perpendicular_line(line_p3p4, p5)

        Q = find_intersection(line_p2_perpendicular, line_p5_perpendicular)

        # 检查Q是否存在
        if Q is None:
            # 如果无法找到圆心，使用直线连接
            draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
            return

        arc_center = Q
        arc_radius = np.linalg.norm(arc_center - p2)

    else:
        # 检查向量长度，避免除0
        vec_p2_intersection = p2 - intersection
        vec_norm = np.linalg.norm(vec_p2_intersection)
        if vec_norm < 1e-10:
            # 如果向量长度为0，使用直线连接
            draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
            return
        
        candidates = [
            intersection + vec_p2_intersection / vec_norm * dist_Op3,
            intersection - vec_p2_intersection / vec_norm * dist_Op3
        ]

        p5 = min(candidates, key=lambda point: np.linalg.norm(point - p2))

        line_p3_perpendicular = create_perpendicular_line(line_p3p4, p3)
        line_p5_perpendicular = create_perpendicular_line(line_p1p2, p5)

        Q = find_intersection(line_p3_perpendicular, line_p5_perpendicular)

        # 检查Q是否存在
        if Q is None:
            # 如果无法找到圆心，使用直线连接
            draw_line_with_width(ax, start=(p2[0], p2[1]), end=(p3[0], p3[1]), width=line_width, color=color)
            return

        arc_center = Q
        arc_radius = np.linalg.norm(arc_center - p3)

        start_x=p2[0]
        end_x=p5[0]
        start_y=p2[1]
        end_y=p5[1]

    if dist_Op2 != dist_Op3:
        # 计算直线两侧的点坐标
        normal_vector = np.array([-(end_y - start_y), end_x - start_x])
        normal_norm = np.linalg.norm(normal_vector)
        
        # 检查法向量长度，避免除0
        if normal_norm < 1e-10:
            # 如果法向量长度为0（起点和终点重合），跳过直线绘制
            pass
        else:
            normal_vector = normal_vector / normal_norm * line_width / 2
            line_points = np.array([
                [start_x, start_y] + normal_vector,
                [start_x, start_y] - normal_vector,
                [end_x, end_y] - normal_vector,
                [end_x, end_y] + normal_vector
            ])

            # 添加直线作为一个多边形
            line_patch = Polygon(line_points, closed=True, facecolor=color, edgecolor=color, linewidth=0)
            ax.add_patch(line_patch)

    # 创建圆弧
    # 检查半径是否有效
    if arc_radius <= 0 or arc_radius > 1e6:
        # 如果半径无效，只绘制直线部分（如果存在）
        return
    
    inner_radius = arc_radius - line_width / 2
    outer_radius = arc_radius + line_width / 2
    
    # 确保内半径为正
    if inner_radius <= 0:
        inner_radius = line_width / 4  # 使用一个小的正值
    if start_angle < end_angle:
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    else:
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle) + 2 * np.pi, 100)
    inner_points = np.column_stack((arc_center[0] + inner_radius * np.cos(theta), arc_center[1] + inner_radius * np.sin(theta)))
    outer_points = np.column_stack((arc_center[0] + outer_radius * np.cos(theta[::-1]), arc_center[1] + outer_radius * np.sin(theta[::-1])))

    # 生成Path对象表示带宽圆弧
    vertices = np.vstack((inner_points, outer_points, inner_points[0]))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # 使用PathPatch添加带宽圆弧
    patch = PathPatch(path, edgecolor=color, facecolor=color, lw=0)
    ax.add_patch(patch)

# 定义函数，画圆弧宽度条
def draw_arc_with_width(ax, center, radius, start_angle, end_angle, width, color):
    # 检查半径是否有效
    if radius <= 0 or radius > 1e6:
        # 如果半径无效，不绘制
        return
    
    inner_radius = radius - width / 2
    outer_radius = radius + width / 2
    
    # 确保内半径为正
    if inner_radius <= 0:
        inner_radius = width / 4  # 使用一个小的正值

    # 归一化角度到0-360度范围内
    start_angle = start_angle % 360
    end_angle = end_angle % 360

    if start_angle < end_angle:
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle), 100)
    else:
        theta = np.linspace(np.radians(start_angle), np.radians(end_angle) + 2 * np.pi, 100)

    inner_points = np.column_stack((center[0] + inner_radius * np.cos(theta), center[1] + inner_radius * np.sin(theta)))
    outer_points = np.column_stack((center[0] + outer_radius * np.cos(theta[::-1]), center[1] + outer_radius * np.sin(theta[::-1])))

    # 生成Path对象表示带宽圆弧
    vertices = np.vstack((inner_points, outer_points, inner_points[0]))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(vertices, codes)

    # 使用PathPatch添加带宽圆弧
    patch = PathPatch(path, edgecolor=color, facecolor=color, lw=0)
    ax.add_patch(patch)

# ==================== 统一的转向路径绘制函数 ====================
def draw_turn_path(ax, entry_index, exit_index, entry_angles, exit_angles, 
                   entry_volumes, exit_volumes, turn_volume, line_width_multiplier, 
                   max_volume, color, turn_type, u_turns, left_turns, straights):
    """
    统一的转向路径绘制函数（左转/直行/右转）
    
    参数:
        ax: matplotlib轴对象
        entry_index: 进口索引 (0-3)
        exit_index: 出口索引 (0-3)
        entry_angles: 所有进口角度列表
        exit_angles: 所有出口角度列表
        entry_volumes: 所有进口总量列表
        exit_volumes: 所有出口总量列表
        turn_volume: 转向交通量
        line_width_multiplier: 线宽倍数
        max_volume: 最大交通量
        color: 路径颜色
        turn_type: 转向类型 ('left', 'straight', 'right')
        u_turns: 所有掉头交通量列表
        left_turns: 所有左转交通量列表
        straights: 所有直行交通量列表
    """
    entry_angle = entry_angles[entry_index]
    exit_angle = exit_angles[exit_index]
    entry_angle_rad = entry_angle * np.pi / 180
    exit_angle_rad = exit_angle * np.pi / 180
    
    volume_ratio = line_width_multiplier / max_volume
    
    # 根据转向类型计算偏移量（考虑已绘制的转向累积影响）
    if turn_type == 'left':
        entry_offset = 0.5 * (entry_volumes[entry_index] - turn_volume - 2 * u_turns[entry_index]) * volume_ratio
        exit_offset = 0.5 * (exit_volumes[exit_index] - turn_volume - 2 * u_turns[exit_index]) * volume_ratio
    elif turn_type == 'straight':
        entry_offset = 0.5 * (entry_volumes[entry_index] - turn_volume - 2 * left_turns[entry_index] - 2 * u_turns[entry_index]) * volume_ratio
        exit_offset = 0.5 * (exit_volumes[exit_index] - turn_volume - 2 * left_turns[(entry_index+3)%4] - 2 * u_turns[exit_index]) * volume_ratio
    else:  # right
        entry_offset = 0.5 * (entry_volumes[entry_index] - turn_volume - 2 * straights[entry_index] - 2 * left_turns[entry_index] - 2 * u_turns[entry_index]) * volume_ratio
        exit_offset = 0.5 * (exit_volumes[exit_index] - turn_volume - 2 * straights[(entry_index+3)%4] - 2 * left_turns[(entry_index+2)%4] - 2 * u_turns[exit_index]) * volume_ratio
    
    # 计算路径的四个关键点
    p1 = np.array([
        -CENTER_OFFSET * np.sin(entry_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(entry_angle_rad) + entry_offset * np.sin(entry_angle_rad),
        MIDDLE_RADIUS_COEFF * np.sin(entry_angle_rad) + CENTER_OFFSET * np.cos(entry_angle_rad) - entry_offset * np.cos(entry_angle_rad)
    ])
    p2 = np.array([
        -CENTER_OFFSET * np.sin(entry_angle_rad) + INNER_RADIUS_COEFF * np.cos(entry_angle_rad) + entry_offset * np.sin(entry_angle_rad),
        INNER_RADIUS_COEFF * np.sin(entry_angle_rad) + CENTER_OFFSET * np.cos(entry_angle_rad) - entry_offset * np.cos(entry_angle_rad)
    ])
    p3 = np.array([
        CENTER_OFFSET * np.sin(exit_angle_rad) + INNER_RADIUS_COEFF * np.cos(exit_angle_rad) - exit_offset * np.sin(exit_angle_rad),
        INNER_RADIUS_COEFF * np.sin(exit_angle_rad) - CENTER_OFFSET * np.cos(exit_angle_rad) + exit_offset * np.cos(exit_angle_rad)
    ])
    p4 = np.array([
        CENTER_OFFSET * np.sin(exit_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(exit_angle_rad) - exit_offset * np.sin(exit_angle_rad),
        MIDDLE_RADIUS_COEFF * np.sin(exit_angle_rad) - CENTER_OFFSET * np.cos(exit_angle_rad) + exit_offset * np.cos(exit_angle_rad)
    ])
    
    path_width = turn_volume * volume_ratio
    
    # 判断是否需要使用圆弧连接
    if abs(exit_angle - entry_angle) % 180 == 0:
        # 共线或对向，使用平行弧连接
        create_parallel_arcs_with_width(ax, p1, p2, p3, p4, path_width, color)
    else:
        # 需要圆角连接
        if (exit_angle - entry_angle) % 360 < 180:
            start_angle = (90 + exit_angle) % 360
            end_angle = (-90 + entry_angle) % 360
        else:
            start_angle = (90 + entry_angle) % 360
            end_angle = (-90 + exit_angle) % 360
        create_wide_line_with_arc(ax, p1, p2, p3, p4, start_angle, end_angle, path_width, color)

# ==================== 通用的转向路径绘制函数（支持任意路数）====================
def draw_turn_path_generic(ax, entry_index, exit_index, entry_angles, exit_angles, 
                           entry_volumes, exit_volumes, turn_volume, line_width_multiplier, 
                           max_volume, color, flows, num_entries, traffic_rule='right'):
    """
    通用的转向路径绘制函数（支持任意路数）
    
    参数:
        ax: matplotlib轴对象
        entry_index: 进口索引（0-based，对应进口编号entry_index+1）
        exit_index: 出口索引（0-based，对应出口编号exit_index+1）
        entry_angles: 所有进口角度列表
        exit_angles: 所有出口角度列表
        entry_volumes: 所有进口总量列表
        exit_volumes: 所有出口总量列表
        turn_volume: 转向交通量
        line_width_multiplier: 线宽倍数
        max_volume: 最大交通量
        color: 路径颜色
        flows: 所有流向数据列表 flows[entry_idx][exit_idx]
        num_entries: 交叉口路数
        traffic_rule: 交通规则，'right'（右行）或'left'（左行），默认为'right'
    """
    entry_angle = entry_angles[entry_index]
    exit_angle = exit_angles[exit_index]
    entry_angle_rad = entry_angle * np.pi / 180
    exit_angle_rad = exit_angle * np.pi / 180
    
    volume_ratio = line_width_multiplier / max_volume
    
    entry_num = entry_index + 1  # 进口编号（1-based）
    exit_num = exit_index + 1    # 出口编号（1-based）
    
    # 根据交通规则计算流线顺序
    if traffic_rule == 'left':
        # 左行规则：流线顺序是顺时针方向
        # 在进口X处，从左到右依次是：流线X_X, 流线X_X+1, 流线X_X+2, ..., 流线X_1（顺时针递增）
        entry_order = 0
        for order in range(num_entries):
            target_exit_num = normalize_index(entry_num + order, num_entries)
            if target_exit_num == exit_num:
                entry_order = order
                break
        
        # 在出口X处，从左到右依次是：流线X+1_X, 流线X+2_X, ..., 流线X_X（顺时针递增）
        exit_order = 0
        for order in range(num_entries):
            # 从exit_num+1开始，顺时针递增：exit_num+1, exit_num+2, ..., exit_num
            target_entry_num = normalize_index(exit_num + 1 + order, num_entries)
            if target_entry_num == entry_num:
                exit_order = order
                break
        
        # 计算已绘制的前面流线的累积影响（在进口处）
        previous_flows_sum_entry = 0.0
        for order in range(entry_order):
            target_exit_num = normalize_index(entry_num + order, num_entries)
            target_exit_idx = target_exit_num - 1
            previous_flows_sum_entry += flows[entry_index][target_exit_idx]
        
        # 计算已绘制的前面流线的累积影响（在出口处）
        previous_flows_sum_exit = 0.0
        # 计算 order > exit_order 的流线（后面的流线，从右到左）
        for order in range(exit_order + 1, num_entries):
            # 从exit_num+1开始，顺时针递增：exit_num+1, exit_num+2, ..., exit_num
            target_entry_num = normalize_index(exit_num + 1 + order, num_entries)
            target_entry_idx = target_entry_num - 1
            previous_flows_sum_exit += flows[target_entry_idx][exit_index]
    else:
        # 右行规则（默认）：流线顺序是逆时针方向
        # 在进口X处，从左到右依次是：流线X_X, 流线X_X-1, 流线X_X-2, ..., 流线X_1
        # 流线X_Y在进口X处的顺序位置是：从X开始逆时针数到Y的位置
        entry_order = 0
        for order in range(num_entries):
            target_exit_num = normalize_index(entry_num - order, num_entries)
            if target_exit_num == exit_num:
                entry_order = order
                break
        
        # 计算在出口处的顺序位置
        # 在出口X处，从左到右依次是：流线X-1_X, 流线X-2_X, ..., 流线X_X
        # 流线Y_X在出口X处的顺序位置是：从X-1开始逆时针数到Y的位置
        # 注意：顺序是从X-1, X-2, ..., 最后是X（掉头在最右边）
        exit_order = 0
        for order in range(num_entries):
            # 从exit_num-1开始，逆时针递减：exit_num-1, exit_num-2, ..., exit_num
            target_entry_num = normalize_index(exit_num - 1 - order, num_entries)
            if target_entry_num == entry_num:
                exit_order = order
                break
        
        # 计算已绘制的前面流线的累积影响（在进口处）
        previous_flows_sum_entry = 0.0
        for order in range(entry_order):
            target_exit_num = normalize_index(entry_num - order, num_entries)
            target_exit_idx = target_exit_num - 1
            previous_flows_sum_entry += flows[entry_index][target_exit_idx]
        
        # 计算已绘制的前面流线的累积影响（在出口处）
        # 在出口X处，从左到右依次是：流线X-1_X, 流线X-2_X, ..., 流线X_X
        # 我们需要计算"从右到左"的累积，即计算后面流线的累积
        # exit_order 表示当前流线在从左到右的顺序（0是最左边，num_entries-1是最右边）
        previous_flows_sum_exit = 0.0
        # 计算 order > exit_order 的流线（后面的流线，从右到左）
        for order in range(exit_order + 1, num_entries):
            # 从exit_num-1开始，逆时针递减：exit_num-1, exit_num-2, ..., exit_num
            target_entry_num = normalize_index(exit_num - 1 - order, num_entries)
            target_entry_idx = target_entry_num - 1
            previous_flows_sum_exit += flows[target_entry_idx][exit_index]
    
    # 对于非掉头流线，不需要额外加上掉头流线，因为掉头流线已经在上面循环中计算了
    # （掉头流线的order=num_entries-1，如果当前流线的order < num_entries-1，掉头流线会在循环中计算）
    
    # 计算偏移量
    entry_offset = 0.5 * (entry_volumes[entry_index] - turn_volume - 2 * previous_flows_sum_entry) * volume_ratio
    exit_offset = 0.5 * (exit_volumes[exit_index] - turn_volume - 2 * previous_flows_sum_exit) * volume_ratio
    
    # 计算路径的四个关键点
    # 左行规则下，进出口位置对调：进口在左侧（+CENTER_OFFSET），出口在右侧（-CENTER_OFFSET）
    if traffic_rule == 'left':
        # 左行规则：进口在左侧，出口在右侧
        p1 = np.array([
            CENTER_OFFSET * np.sin(entry_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(entry_angle_rad) - entry_offset * np.sin(entry_angle_rad),
            MIDDLE_RADIUS_COEFF * np.sin(entry_angle_rad) - CENTER_OFFSET * np.cos(entry_angle_rad) + entry_offset * np.cos(entry_angle_rad)
        ])
        p2 = np.array([
            CENTER_OFFSET * np.sin(entry_angle_rad) + INNER_RADIUS_COEFF * np.cos(entry_angle_rad) - entry_offset * np.sin(entry_angle_rad),
            INNER_RADIUS_COEFF * np.sin(entry_angle_rad) - CENTER_OFFSET * np.cos(entry_angle_rad) + entry_offset * np.cos(entry_angle_rad)
        ])
        p3 = np.array([
            -CENTER_OFFSET * np.sin(exit_angle_rad) + INNER_RADIUS_COEFF * np.cos(exit_angle_rad) + exit_offset * np.sin(exit_angle_rad),
            INNER_RADIUS_COEFF * np.sin(exit_angle_rad) + CENTER_OFFSET * np.cos(exit_angle_rad) - exit_offset * np.cos(exit_angle_rad)
        ])
        p4 = np.array([
            -CENTER_OFFSET * np.sin(exit_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(exit_angle_rad) + exit_offset * np.sin(exit_angle_rad),
            MIDDLE_RADIUS_COEFF * np.sin(exit_angle_rad) + CENTER_OFFSET * np.cos(exit_angle_rad) - exit_offset * np.cos(exit_angle_rad)
        ])
    else:
        # 右行规则（默认）：进口在右侧，出口在左侧
        p1 = np.array([
            -CENTER_OFFSET * np.sin(entry_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(entry_angle_rad) + entry_offset * np.sin(entry_angle_rad),
            MIDDLE_RADIUS_COEFF * np.sin(entry_angle_rad) + CENTER_OFFSET * np.cos(entry_angle_rad) - entry_offset * np.cos(entry_angle_rad)
        ])
        p2 = np.array([
            -CENTER_OFFSET * np.sin(entry_angle_rad) + INNER_RADIUS_COEFF * np.cos(entry_angle_rad) + entry_offset * np.sin(entry_angle_rad),
            INNER_RADIUS_COEFF * np.sin(entry_angle_rad) + CENTER_OFFSET * np.cos(entry_angle_rad) - entry_offset * np.cos(entry_angle_rad)
        ])
        p3 = np.array([
            CENTER_OFFSET * np.sin(exit_angle_rad) + INNER_RADIUS_COEFF * np.cos(exit_angle_rad) - exit_offset * np.sin(exit_angle_rad),
            INNER_RADIUS_COEFF * np.sin(exit_angle_rad) - CENTER_OFFSET * np.cos(exit_angle_rad) + exit_offset * np.cos(exit_angle_rad)
        ])
        p4 = np.array([
            CENTER_OFFSET * np.sin(exit_angle_rad) + MIDDLE_RADIUS_COEFF * np.cos(exit_angle_rad) - exit_offset * np.sin(exit_angle_rad),
            MIDDLE_RADIUS_COEFF * np.sin(exit_angle_rad) - CENTER_OFFSET * np.cos(exit_angle_rad) + exit_offset * np.cos(exit_angle_rad)
        ])
    
    path_width = turn_volume * volume_ratio
    
    # 判断是否需要使用圆弧连接
    if abs(exit_angle - entry_angle) % 180 == 0:
        # 共线或对向，使用平行弧连接
        create_parallel_arcs_with_width(ax, p1, p2, p3, p4, path_width, color)
    else:
        # 需要圆角连接
        if (exit_angle - entry_angle) % 360 < 180:
            start_angle = (90 + exit_angle) % 360
            end_angle = (-90 + entry_angle) % 360
        else:
            start_angle = (90 + entry_angle) % 360
            end_angle = (-90 + exit_angle) % 360
        create_wide_line_with_arc(ax, p1, p2, p3, p4, start_angle, end_angle, path_width, color)

# ==================== 统一的标注函数 ====================
def draw_traffic_volume_labels(ax, entry_index, entry_angle, flow_volumes, num_entries, traffic_rule='right'):
    """
    统一绘制单个进口的所有转向交通量标注
    0流量的转向不标注，非0标注自动靠紧（保持相对间距，整体向中心靠拢）
    
    参数:
        ax: matplotlib轴对象
        entry_index: 进口索引
        entry_angle: 进口角度
        flow_volumes: 流向交通量列表 [flow_0, flow_1, ..., flow_{N-1}]
        num_entries: 交叉口路数
        traffic_rule: 交通规则，'right'（右行）或'left'（左行），默认为'right'
    """
    # 定义偏移量映射（4路使用传统偏移，其他路数使用均匀分布）
    if num_entries == 4:
        offset_map = {
            0: LABEL_OFFSET_U_TURN,    # 掉头
            1: LABEL_OFFSET_LEFT,      # 左转
            2: LABEL_OFFSET_STRAIGHT,  # 直行
            3: LABEL_OFFSET_RIGHT      # 右转
        }
    else:
        # 其他路数：均匀分布在-18到18之间
        offset_map = {}
        if num_entries > 1:
            spacing = 36.0 / (num_entries - 1)
            for i in range(num_entries):
                offset_map[i] = 18 - i * spacing
    
    # 收集所有非0转向及其原始偏移量
    non_zero_labels = []
    for flow_idx, volume in enumerate(flow_volumes):
        if volume != 0 and flow_idx in offset_map:
            non_zero_labels.append((flow_idx, volume, offset_map[flow_idx]))
    
    # 如果所有转向都为0，不绘制任何标注
    if len(non_zero_labels) == 0:
        return
    
    # 计算非0标注的新位置（保持间距12，重新排列消除空位）
    if len(non_zero_labels) == 1:
        # 只有一个非0标注，将其放在中心位置（偏移为0）
        adjusted_labels = [(flow_idx, volume, 0) for flow_idx, volume, _ in non_zero_labels]
    else:
        # 按原始偏移量从大到小排序（保持原始顺序）
        sorted_labels = sorted(non_zero_labels, key=lambda x: x[2], reverse=True)
        
        # 计算需要重新排列的位置
        # 保持间距12，以0为中心对称分布
        num_labels = len(sorted_labels)
        spacing = 12  # 保持原始间距12
        
        # 计算起始位置：如果有奇数个，最中间的为0；如果有偶数个，从-spacing/2开始
        if num_labels % 2 == 1:
            # 奇数个：中心位置为0，向两侧扩展
            start_offset = spacing * (num_labels // 2)
        else:
            # 偶数个：从spacing/2开始，向两侧扩展
            start_offset = spacing * (num_labels // 2) - spacing / 2
        
        # 重新分配位置，保持间距12，消除空位
        adjusted_labels = []
        for i, (flow_idx, volume, original_offset) in enumerate(sorted_labels):
            new_offset = start_offset - i * spacing
            adjusted_labels.append((flow_idx, volume, new_offset))
    
    # 绘制标注
    entry_angle_rad = entry_angle * np.pi / 180
    # 根据交通规则计算标注基准位置
    if traffic_rule == 'left':
        # 左行规则：进口在左侧（+CENTER_OFFSET）
        base_x = CENTER_OFFSET * np.sin(entry_angle_rad) + INNER_RADIUS_COEFF * np.cos(entry_angle_rad)
        base_y = INNER_RADIUS_COEFF * np.sin(entry_angle_rad) - CENTER_OFFSET * np.cos(entry_angle_rad)
    else:
        # 右行规则（默认）：进口在右侧（-CENTER_OFFSET）
        base_x = -CENTER_OFFSET * np.sin(entry_angle_rad) + INNER_RADIUS_COEFF * np.cos(entry_angle_rad)
        base_y = INNER_RADIUS_COEFF * np.sin(entry_angle_rad) + CENTER_OFFSET * np.cos(entry_angle_rad)
    label_angle = (entry_angle + 90) % 180 - 90
    
    # 绘制标注（只显示数字）
    for flow_idx, volume, offset in adjusted_labels:
        # 根据交通规则调整偏移方向
        if traffic_rule == 'left':
            # 左行规则：偏移方向相反
            label_x = base_x - offset * np.sin(entry_angle_rad)
            label_y = base_y + offset * np.cos(entry_angle_rad)
        else:
            # 右行规则（默认）
            label_x = base_x + offset * np.sin(entry_angle_rad)
            label_y = base_y - offset * np.cos(entry_angle_rad)
        draw_text(ax, str(int(volume)), 12, (label_x, label_y), label_angle, "black")

# 定义函数，创建矢量图文字
def draw_text(ax, text, fontsize, center, angle, color, fontname=None):
    # 如果没有指定字体，使用全局字体设置
    if fontname is None:
        font_prop = font
    elif os.path.exists(fontname):
        font_prop = fm.FontProperties(fname=fontname, size=fontsize)
    else:
        # 如果路径不存在，尝试使用字体名称
        font_prop = fm.FontProperties(family=fontname, size=fontsize)
    
    # 确保center是numpy数组或可以转换为标量的值
    if isinstance(center, (list, tuple)):
        center = np.array(center, dtype=float)
    elif not isinstance(center, np.ndarray):
        center = np.array([float(center[0]), float(center[1])])
    
    # 确保center是1D数组，并提取标量值
    center = np.asarray(center).flatten()
    if len(center) < 2:
        raise ValueError(f"center must have at least 2 elements, got {center}")
    center_x = float(center[0])
    center_y = float(center[1])
    
    # 创建一个TextPath对象并指定字体
    text_path = TextPath((0, 0), text, size=fontsize, prop=font_prop)
    
    # 计算文本的宽度和高度
    extent = text_path.get_extents()
    text_width, text_height = extent.width, extent.height

    # 创建旋转和平移矩阵（使用标量值）
    transform = Affine2D().translate(-text_width / 2, -0.45*text_height).rotate_deg(angle).translate(center_x, center_y)

    # 将TextPath对象转换为PathPatch对象
    text_patch = PathPatch(text_path, lw=0, edgecolor=None, facecolor=color, transform=transform + ax.transData)

    # 将PathPatch对象添加到轴上
    ax.add_patch(text_patch)

def plot_traffic_flow(table_instance):
    """绘制交通流量图"""
    # 获取表格数据
    table_instance.get()
    data = table_instance.data
    num_entries = table_instance.num_entries
    
    # 验证数据完整性
    required_keys = ['names', 'angles'] + [f'flow_{i}' for i in range(num_entries)]
    if not data or not all(key in data for key in required_keys):
        messagebox.showerror("错误", "数据不完整，请先输入或加载数据")
        return
    
    # 验证数据是否为空
    if not any(data.get(key) for key in required_keys):
        messagebox.showerror("错误", "数据为空，请先输入或加载数据")
        return
    
    try:
        # 转换数据
        names = data['names']
        angles = convert_to_float_list(data['angles'])
        
        # 获取所有流向数据（旧格式：flows[flow_idx][entry_idx]）
        old_flows = []
        for i in range(num_entries):
            flow_key = f'flow_{i}'
            old_flows.append(convert_to_float_list(data.get(flow_key, [])))
        
        # 确保所有列表长度一致
        min_length = min(len(names), len(angles), *[len(f) for f in old_flows])
        if min_length < num_entries:
            messagebox.showerror("错误", f"数据不足，至少需要{num_entries}个进口的数据，当前只有 {min_length} 个")
            return
        
        # 截取到正确的路数
        names = names[:num_entries]
        angles = angles[:num_entries]
        # 如果进口名称为空，使用进口编号作为默认名称
        for i in range(num_entries):
            if not names[i] or names[i].strip() == '':
                names[i] = f'进口{i+1}'
        for i in range(num_entries):
            old_flows[i] = old_flows[i][:num_entries] if len(old_flows[i]) >= num_entries else old_flows[i] + [0.0] * (num_entries - len(old_flows[i]))
        
        # 获取交通规则
        traffic_rule = getattr(table_instance, 'traffic_rule', 'right')
        
        # 重新组织为flows[entry_idx][exit_idx]格式（编号从1开始，内部索引从0开始）
        # flows[entry_idx][exit_idx] 表示从entry_idx+1到exit_idx+1的流量
        flows = [[0.0] * num_entries for _ in range(num_entries)]
        for entry_idx in range(num_entries):  # entry_idx是0-based，对应进口编号entry_idx+1
            for flow_idx in range(num_entries):  # flow_idx是0-based，对应流向顺序
                # 根据交通规则计算出口编号
                if traffic_rule == 'left':
                    # 左行规则：从entry_idx+1开始，顺时针递增
                    exit_num_1based = normalize_index((entry_idx + 1) + flow_idx, num_entries)
                else:
                    # 右行规则（默认）：从entry_idx+1开始，逆时针递减
                    exit_num_1based = normalize_index((entry_idx + 1) - flow_idx, num_entries)
                exit_idx = exit_num_1based - 1  # 转换为0-based索引
                flows[entry_idx][exit_idx] = old_flows[flow_idx][entry_idx]
        
        # 计算各方向进口总量、出口总量
        entry_total_volumes = [0.0] * num_entries
        exit_total_volumes = [0.0] * num_entries
        for entry_idx in range(num_entries):
            # 进口总量：所有流向之和
            entry_total_volumes[entry_idx] = sum(flows[entry_idx])
            # 出口总量：从所有进口流向该出口的流量之和
            for exit_idx in range(num_entries):
                exit_total_volumes[exit_idx] += flows[entry_idx][exit_idx]
        
        # 创建画布
        fig = plt.figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_aspect('equal')
        
        # 计算最大交通量用于线宽归一化
        max_volume = float('-inf')
        for flow_list in flows:
            if len(flow_list) > 0:
                max_volume_in_list = max(flow_list)
                if max_volume_in_list > max_volume:
                    max_volume = max_volume_in_list
        
        # 防止除零错误
        if max_volume <= 0:
            max_volume = 1.0
        
        line_width_multiplier = MAX_LINE_WIDTH
        
        # 绘制进口和出口流量线
        # 左行规则下，进出口位置对调：进口在左侧，出口在右侧
        for i in range(num_entries):
            angle_rad = angles[i] * np.pi / 180
            
            if traffic_rule == 'left':
                # 左行规则：进口在左侧（+CENTER_OFFSET），出口在右侧（-CENTER_OFFSET）
                # 计算进口流量线坐标
                entry_inner_x = CENTER_OFFSET * np.sin(angle_rad) + INNER_RADIUS_COEFF * np.cos(angle_rad)
                entry_inner_y = INNER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
                entry_outer_x = CENTER_OFFSET * np.sin(angle_rad) + OUTER_RADIUS_COEFF * np.cos(angle_rad)
                entry_outer_y = OUTER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
                
                # 计算延长后的终点坐标（向外延长45单位）
                entry_direction = np.array([entry_outer_x - entry_inner_x, entry_outer_y - entry_inner_y])
                entry_direction_norm = np.linalg.norm(entry_direction)
                if entry_direction_norm > 1e-10:
                    entry_direction_unit = entry_direction / entry_direction_norm
                    entry_outer_extended_x = entry_outer_x + entry_direction_unit[0] * 45
                    entry_outer_extended_y = entry_outer_y + entry_direction_unit[1] * 45
                else:
                    entry_outer_extended_x = entry_outer_x
                    entry_outer_extended_y = entry_outer_y
                
                entry_line_width = entry_total_volumes[i] * line_width_multiplier / max_volume
                draw_line_with_width(ax, start=(entry_inner_x, entry_inner_y), end=(entry_outer_extended_x, entry_outer_extended_y), 
                                    width=entry_line_width, color=ENTRY_COLORS[i])
                
                # 计算出口流量线坐标
                exit_inner_x = -CENTER_OFFSET * np.sin(angle_rad) + INNER_RADIUS_COEFF * np.cos(angle_rad)
                exit_inner_y = INNER_RADIUS_COEFF * np.sin(angle_rad) + CENTER_OFFSET * np.cos(angle_rad)
                exit_outer_x = -CENTER_OFFSET * np.sin(angle_rad) + OUTER_RADIUS_COEFF * np.cos(angle_rad)
                exit_outer_y = OUTER_RADIUS_COEFF * np.sin(angle_rad) + CENTER_OFFSET * np.cos(angle_rad)
            else:
                # 右行规则（默认）：进口在右侧（-CENTER_OFFSET），出口在左侧（+CENTER_OFFSET）
                # 计算进口流量线坐标
                entry_inner_x = -CENTER_OFFSET * np.sin(angle_rad) + INNER_RADIUS_COEFF * np.cos(angle_rad)
                entry_inner_y = INNER_RADIUS_COEFF * np.sin(angle_rad) + CENTER_OFFSET * np.cos(angle_rad)
                entry_outer_x = -CENTER_OFFSET * np.sin(angle_rad) + OUTER_RADIUS_COEFF * np.cos(angle_rad)
                entry_outer_y = OUTER_RADIUS_COEFF * np.sin(angle_rad) + CENTER_OFFSET * np.cos(angle_rad)
                
                # 计算延长后的终点坐标（向外延长45单位）
                entry_direction = np.array([entry_outer_x - entry_inner_x, entry_outer_y - entry_inner_y])
                entry_direction_norm = np.linalg.norm(entry_direction)
                if entry_direction_norm > 1e-10:
                    entry_direction_unit = entry_direction / entry_direction_norm
                    entry_outer_extended_x = entry_outer_x + entry_direction_unit[0] * 45
                    entry_outer_extended_y = entry_outer_y + entry_direction_unit[1] * 45
                else:
                    entry_outer_extended_x = entry_outer_x
                    entry_outer_extended_y = entry_outer_y
                
                entry_line_width = entry_total_volumes[i] * line_width_multiplier / max_volume
                draw_line_with_width(ax, start=(entry_inner_x, entry_inner_y), end=(entry_outer_extended_x, entry_outer_extended_y), 
                                    width=entry_line_width, color=ENTRY_COLORS[i])
                
                # 计算出口流量线坐标
                exit_inner_x = CENTER_OFFSET * np.sin(angle_rad) + INNER_RADIUS_COEFF * np.cos(angle_rad)
                exit_inner_y = INNER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
                exit_outer_x = CENTER_OFFSET * np.sin(angle_rad) + OUTER_RADIUS_COEFF * np.cos(angle_rad)
                exit_outer_y = OUTER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
            
            exit_line_width = exit_total_volumes[i] * line_width_multiplier / max_volume
            draw_line_with_width(ax, start=(exit_inner_x, exit_inner_y), end=(exit_outer_x, exit_outer_y), 
                                width=exit_line_width, color=ENTRY_COLORS[i])
            
            # 在出口宽度条末端添加箭头
            # 计算箭头方向向量（从exit_inner指向exit_outer）
            exit_direction = np.array([exit_outer_x - exit_inner_x, exit_outer_y - exit_inner_y])
            exit_direction_norm = np.linalg.norm(exit_direction)
            if exit_direction_norm > 1e-10:
                exit_direction_unit = exit_direction / exit_direction_norm
                # 箭头起点：exit_outer
                # 箭头终点：exit_outer + 方向向量 * 45
                arrow_start = (exit_outer_x, exit_outer_y)
                arrow_end = (exit_outer_x + exit_direction_unit[0] * 45, 
                            exit_outer_y + exit_direction_unit[1] * 45)
                # 箭头宽度：exit_line_width * 1.8
                arrow_width = exit_line_width * 1.8
                # 绘制箭头（颜色与出口宽度条一致）
                draw_arrow(ax, start=arrow_start, end=arrow_end, width=arrow_width, color=ENTRY_COLORS[i])
            
            # 标注进口名称、进口道总量、出口道总量
            # 进口名称：只要进口总量或出口总量不为0就显示
            if entry_total_volumes[i] + exit_total_volumes[i] != 0:
                # 进口名称沿方位角方向向外移动45单位
                name_x = (exit_outer_x + entry_outer_x) / 2 + (NAME_LABEL_OFFSET + 45) * np.cos(angle_rad)
                name_y = (exit_outer_y + entry_outer_y) / 2 + (NAME_LABEL_OFFSET + 45) * np.sin(angle_rad)
                name_angle = (angles[i] % 180 + 270) % 360
                draw_text(ax, names[i], 15, (name_x, name_y), name_angle, "black")
            
            # 进口总量标注：只有当进口总量不为0时才显示
            if entry_total_volumes[i] != 0:
                entry_label_x = (entry_inner_x + entry_outer_x) / 2
                entry_label_y = (entry_inner_y + entry_outer_y) / 2
                entry_label_angle = (angles[i] + 90) % 180 - 90
                draw_text(ax, str(int(entry_total_volumes[i])), 12, (entry_label_x, entry_label_y), entry_label_angle, "black")
            
            # 出口总量标注：只有当出口总量不为0时才显示
            if exit_total_volumes[i] != 0:
                exit_label_x = (exit_inner_x + exit_outer_x) / 2
                exit_label_y = (exit_inner_y + exit_outer_y) / 2
                exit_label_angle = (angles[i] + 90) % 180 - 90
                draw_text(ax, str(int(exit_total_volumes[i])), 12, (exit_label_x, exit_label_y), exit_label_angle, "black")
        
        # 绘制掉头路径（流线X_X，即flows[entry_idx][entry_idx]）
        for entry_idx in range(num_entries):
            exit_idx = entry_idx  # 掉头：出口编号等于进口编号
            if flows[entry_idx][exit_idx] != 0:
                entry_angle_rad = angles[entry_idx] * np.pi / 180
                volume_ratio = line_width_multiplier / max_volume
                # 获取交通规则
                traffic_rule = getattr(table_instance, 'traffic_rule', 'right')
                
                # 计算已绘制的前面流线的累积影响（在进口处，掉头是最左边的）
                previous_flows_sum_entry = 0.0  # 掉头是最左边的，前面没有流线
                # 计算已绘制的前面流线的累积影响（在出口处）
                exit_num = exit_idx + 1  # 出口编号（1-based）
                previous_flows_sum_exit = 0.0
                if traffic_rule == 'left':
                    # 左行规则：在出口X处，从左到右依次是：流线X+1_X, 流线X+2_X, ..., 流线X_X
                    # 掉头（流线X_X）是最右边的，所以前面应该有流线X+1_X, X+2_X, ..., 1_X
                    for order in range(num_entries - 1):  # 掉头是最后一个，所以前面有num_entries-1个流线
                        target_entry_num = normalize_index(exit_num + 1 + order, num_entries)
                        target_entry_idx = target_entry_num - 1
                        previous_flows_sum_exit += flows[target_entry_idx][exit_idx]
                else:
                    # 右行规则：在出口X处，从左到右依次是：流线X-1_X, 流线X-2_X, ..., 流线X_X
                    # 掉头（流线X_X）是最右边的，所以前面应该有流线X-1_X, X-2_X, ..., 1_X
                    for order in range(num_entries - 1):  # 掉头是最后一个，所以前面有num_entries-1个流线
                        target_entry_num = normalize_index(exit_num - 1 - order, num_entries)
                        target_entry_idx = target_entry_num - 1
                        previous_flows_sum_exit += flows[target_entry_idx][exit_idx]
                # 根据交通规则计算掉头路径的中心和半径
                if traffic_rule == 'left':
                    # 左行规则：进口在左侧，出口在右侧，掉头路径中心需要调整
                    center_x = INNER_RADIUS_COEFF * np.cos(entry_angle_rad) - volume_ratio * 0.25 * (entry_total_volumes[entry_idx] - exit_total_volumes[exit_idx]) * np.sin(entry_angle_rad)
                    center_y = INNER_RADIUS_COEFF * np.sin(entry_angle_rad) + volume_ratio * 0.25 * (entry_total_volumes[entry_idx] - exit_total_volumes[exit_idx]) * np.cos(entry_angle_rad)
                    arc_radius = CENTER_OFFSET - volume_ratio * ((entry_total_volumes[entry_idx] + exit_total_volumes[exit_idx]) / 2 - flows[entry_idx][exit_idx]) / 2
                else:
                    # 右行规则（默认）
                    center_x = INNER_RADIUS_COEFF * np.cos(entry_angle_rad) + volume_ratio * 0.25 * (entry_total_volumes[entry_idx] - exit_total_volumes[exit_idx]) * np.sin(entry_angle_rad)
                    center_y = INNER_RADIUS_COEFF * np.sin(entry_angle_rad) - volume_ratio * 0.25 * (entry_total_volumes[entry_idx] - exit_total_volumes[exit_idx]) * np.cos(entry_angle_rad)
                    arc_radius = CENTER_OFFSET - volume_ratio * ((entry_total_volumes[entry_idx] + exit_total_volumes[exit_idx]) / 2 - flows[entry_idx][exit_idx]) / 2
                u_turn_width = flows[entry_idx][exit_idx] * volume_ratio
                # 检查半径和宽度是否有效
                if arc_radius > 0 and u_turn_width > 0:
                    # 掉头路径角度处理：由于中心位置已经根据交通规则对调，角度保持和右行规则一样即可
                    # （算法里可能藏着一个负负得正，最后的效果就是不用改）
                    draw_arc_with_width(ax, center=(center_x, center_y), radius=arc_radius, 
                                       start_angle=angles[entry_idx]+90, end_angle=angles[entry_idx]+270, 
                                       width=u_turn_width, color=ENTRY_COLORS[entry_idx % len(ENTRY_COLORS)])
        
        # 绘制其他流向路径（流线X_Y，其中X != Y）
        # 根据交通规则确定流线顺序
        traffic_rule = getattr(table_instance, 'traffic_rule', 'right')
        for entry_idx in range(num_entries):  # entry_idx是0-based，对应进口编号entry_idx+1
            entry_num = entry_idx + 1  # 进口编号（1-based）
            # 计算该进口的所有流向顺序
            for flow_order in range(num_entries):  # flow_order表示在进口处的顺序（0是最左边）
                # 根据交通规则计算出口编号
                if traffic_rule == 'left':
                    # 左行规则：从X开始顺时针递增：X, X+1, X+2, ..., 1
                    exit_num = normalize_index(entry_num + flow_order, num_entries)
                else:
                    # 右行规则：从X开始逆时针递减：X, X-1, X-2, ..., 1
                    exit_num = normalize_index(entry_num - flow_order, num_entries)
                exit_idx = exit_num - 1  # 转换为0-based索引
                
                # 跳过掉头（已经在上面绘制了）
                if entry_idx == exit_idx:
                    continue
                
                if flows[entry_idx][exit_idx] != 0:
                    draw_turn_path_generic(ax, entry_idx, exit_idx, angles, angles, entry_total_volumes, exit_total_volumes, 
                                          flows[entry_idx][exit_idx], line_width_multiplier, max_volume, 
                                          ENTRY_COLORS[entry_idx % len(ENTRY_COLORS)], flows, num_entries, traffic_rule)
        
        # 标注各流向交通量
        # 根据交通规则确定流线顺序
        traffic_rule = getattr(table_instance, 'traffic_rule', 'right')
        for entry_idx in range(num_entries):
            entry_num = entry_idx + 1  # 进口编号（1-based）
            flow_volumes = []
            for order in range(num_entries):
                # 根据交通规则计算出口编号
                if traffic_rule == 'left':
                    # 左行规则：从X开始顺时针递增：X, X+1, X+2, ..., 1
                    exit_num = normalize_index(entry_num + order, num_entries)
                else:
                    # 右行规则：从X开始逆时针递减：X, X-1, X-2, ..., 1
                    exit_num = normalize_index(entry_num - order, num_entries)
                exit_idx = exit_num - 1
                flow_volumes.append(flows[entry_idx][exit_idx])
            draw_traffic_volume_labels(ax, entry_idx, angles[entry_idx], flow_volumes, num_entries, traffic_rule)
        
        plt.xlim(PLOT_XLIM[0], PLOT_XLIM[1])
        plt.ylim(PLOT_YLIM[0], PLOT_YLIM[1])
        plt.gca().set_axis_off()
        plt.tight_layout()
        
        # 创建新的tkinter窗口来显示图形
        plot_window = tk.Toplevel(root)
        
        # 立即隐藏窗口，避免闪现
        plot_window.withdraw()
        # 先设置一个临时位置（屏幕外），避免在左上角闪现
        plot_window.geometry("1x1+-10000+-10000")
        
        if table_instance.file_name:
            # 去掉文件扩展名显示
            file_name = os.path.basename(table_instance.file_name)
            plot_title = os.path.splitext(file_name)[0]
        else:
            plot_title = "交叉口交通流量流向可视化图"
        plot_window.title(plot_title)
        
        # 将matplotlib图形嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # 创建自定义工具栏，只包含导出按钮
        toolbar_frame = tk.Frame(plot_window, bg='#f5f5f5', relief='flat', padx=10, pady=5)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 导出按钮
        def export_figure():
            # 定义文件类型
            filetypes = [
                ("SVG 矢量图", "*.svg"),  # SVG作为默认格式
                ("PDF 文档", "*.pdf"),
                ("PNG 图片", "*.png"),
                ("JPG 图片", "*.jpg"),
                ("TIF 图片", "*.tif"),
            ]
            
            # 获取默认文件名
            if table_instance.file_name:
                default_name = os.path.splitext(os.path.basename(table_instance.file_name))[0]
            else:
                default_name = "交叉口交通流量流向可视化图"
            
            # 打开保存对话框
            filename = filedialog.asksaveasfilename(
                defaultextension='.svg',  # SVG作为默认格式
                filetypes=filetypes,
                initialfile=default_name,
                title="导出图片"
            )
            
            if filename:
                try:
                    # 根据文件扩展名确定格式
                    ext = os.path.splitext(filename)[1].lower()
                    if ext == '.svg':
                        format = 'svg'
                    elif ext == '.pdf':
                        format = 'pdf'
                    elif ext == '.png':
                        format = 'png'
                    elif ext == '.jpg' or ext == '.jpeg':
                        format = 'jpg'
                    elif ext == '.tif' or ext == '.tiff':
                        format = 'tiff'  # matplotlib使用'tiff'格式
                    else:
                        messagebox.showerror("错误", f"不支持的格式：{ext}\n仅支持：svg, pdf, png, jpg, tif")
                        return
                    
                    # 保存图形
                    fig.savefig(filename, format=format, dpi=FIGURE_DPI, bbox_inches='tight', pad_inches=0.1)
                    messagebox.showinfo("成功", f"图片已保存到：\n{filename}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存图片时出错：{str(e)}")
        
        export_button = ttk.Button(toolbar_frame, text="导出图片", command=export_figure)
        export_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 添加窗口关闭事件处理，确保清理资源
        def on_plot_window_close():
            """绘图窗口关闭时的清理函数"""
            try:
                # 清理matplotlib资源
                plt.close(fig)
                # 断开画布与figure的连接
                fig.set_canvas(None)
                # 销毁画布
                canvas.get_tk_widget().destroy()
                # 清理画布对象
                del canvas
                # 销毁窗口
                plot_window.destroy()
            except Exception as e:
                # 即使出错也要确保窗口被销毁
                try:
                    plot_window.destroy()
                except:
                    pass
        
        plot_window.protocol("WM_DELETE_WINDOW", on_plot_window_close)
        
        # 更新窗口以确保正确计算大小
        plot_window.update_idletasks()
        
        # 在隐藏状态下设置居中位置
        center_window(plot_window)
        
        # 显示窗口（此时已经在正确位置了）
        plot_window.deiconify()
        
    except Exception as e:
        messagebox.showerror("错误", f"绘制图形时出错：{str(e)}")

# 创建主窗口（先不显示）
root = tk.Tk()
root.title("交叉口交通流量流向可视化工具")
root.withdraw()  # 先隐藏窗口
# 先设置一个临时位置（屏幕外），避免在左上角闪现
root.geometry("1x1+-10000+-10000")

# 设置现代化界面样式（必须在创建组件之前调用）
ui_font_family = setup_modern_style(root)

# 将root保存到update_window_title函数中，以便函数可以访问
update_window_title.root = root

# 选择交叉口类型或读取文件
try:
    choice = select_intersection_type()
except Exception as e:
    print(f"选择对话框出错：{e}")
    root.destroy()
    exit()

if choice is None:
    root.destroy()
    exit()

num_entries = None
initial_file = None

if choice == 'load_file':
    # 如果选择读取文件，调用文件选择对话框
    initial_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if initial_file:
        # 读取文件第一行，解析路数
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']
            first_line = None
            for encoding in encodings:
                try:
                    with open(initial_file, 'r', encoding=encoding) as f:
                        first_line = f.readline().strip()
                        break
                except:
                    continue
            
            if first_line:
                match = re.search(r'本交叉口为(\d+)路交叉口', first_line)
                if match:
                    num_entries = int(match.group(1))
                    if num_entries < 3 or num_entries > 6:
                        messagebox.showerror("错误", "交叉口路数错误，请核对数据后再读取")
                        root.destroy()
                        exit()
                else:
                    # 如果未声明路数，允许继续，让load_data_from_file函数从数据推断
                    num_entries = None  # 设置为None，让load_data_from_file函数处理
            else:
                messagebox.showerror("错误", "无法读取文件。")
                root.destroy()
                exit()
        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错：{str(e)}")
            root.destroy()
            exit()
    else:
        root.destroy()
        exit()
else:
    num_entries = choice

# 创建表格（默认4路，如果从文件读取则使用文件中的路数，如果未声明则使用4路作为初始值）
# 注意：如果num_entries为None，说明文件未声明路数，将在load_data_from_file中从数据推断
if num_entries is None:
    num_entries = 4  # 使用默认值，load_data_from_file会重新创建表格
table = Table(root, num_entries=num_entries)
table.pack()
root.update()  # 确保表格显示

# 如果从文件读取，加载数据
if choice == 'load_file' and initial_file:
    success, new_table = load_data_from_file(initial_file, table, root)
    if success:
        table = new_table

# 创建按钮框架
button_frame = tk.Frame(root, bg='#f5f5f5')
button_frame.pack(pady=10)

new_file_button = ttk.Button(button_frame, text="新建文件", command=on_new_file_click)
new_file_button.pack(side=tk.LEFT, padx=5)

load_button = ttk.Button(button_frame, text="读取数据", command=on_load_data_click)
load_button.pack(side=tk.LEFT, padx=5)

clear_data_button = ttk.Button(button_frame, text="清空数据", command=on_clear_data_click)
clear_data_button.pack(side=tk.LEFT, padx=5)

save_button = ttk.Button(button_frame, text="保存数据", command=on_save_data_click)
save_button.pack(side=tk.LEFT, padx=5)

save_as_button = ttk.Button(button_frame, text="数据另存为", command=on_save_data_as_click)
save_as_button.pack(side=tk.LEFT, padx=5)

plot_button = ttk.Button(button_frame, text="绘制流量图", command=lambda: plot_traffic_flow(table))
plot_button.pack(side=tk.LEFT, padx=5)

help_button = ttk.Button(button_frame, text="帮助", command=show_help)
help_button.pack(side=tk.LEFT, padx=5)

about_button = ttk.Button(button_frame, text="关于", command=show_about)
about_button.pack(side=tk.LEFT, padx=5)

# 显示主窗口并居中（在所有组件添加完成后）
root.deiconify()
root.update_idletasks()  # 确保所有组件都布局完成
root.update()  # 再次更新以确保尺寸计算准确

# 调整窗口大小以适应内容并居中
adjust_window_size(root)

# 添加主窗口关闭事件处理，确保程序完全退出
def on_main_window_close():
    """主窗口关闭时的清理函数"""
    try:
        # 关闭所有matplotlib图形
        plt.close('all')
        # 停止事件循环
        root.quit()
        # 销毁主窗口
        root.destroy()
    except:
        pass
    finally:
        # 确保进程完全退出
        # 使用os._exit强制退出，避免等待其他线程
        os._exit(0)

root.protocol("WM_DELETE_WINDOW", on_main_window_close)

root.mainloop()
