# -*- coding: utf-8 -*-
"""
主绘图功能模块
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import re

# 抑制 matplotlib 字体警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')

# 延迟导入其他模块
def t(key, **kwargs):
    """翻译函数（延迟导入i18n）"""
    try:
        import i18n
        return i18n.t(key, **kwargs)
    except:
        return key

def convert_to_float_list(string_list):
    """将字符串列表转换为浮点数列表"""
    try:
        return [float(x) if x.strip() else 0.0 for x in string_list]
    except:
        return [0.0] * len(string_list)

def get_ui_utils():
    """获取ui_utils模块的函数和变量"""
    try:
        import ui_utils
        return {
            'create_toplevel': ui_utils.create_toplevel,
            'set_window_icon': ui_utils.set_window_icon,
            'center_window': ui_utils.center_window,
        }
    except:
        return None

def get_drawing_utils():
    """获取drawing_utils模块的函数和常量"""
    try:
        import drawing_utils
        return {
            'normalize_index': drawing_utils.normalize_index,
            'draw_line_with_width': drawing_utils.draw_line_with_width,
            'draw_arrow': drawing_utils.draw_arrow,
            'draw_arc_with_width': drawing_utils.draw_arc_with_width,
            'draw_turn_path_generic': drawing_utils.draw_turn_path_generic,
            'draw_traffic_volume_labels': drawing_utils.draw_traffic_volume_labels,
            'draw_text': drawing_utils.draw_text,
            'CENTER_OFFSET': drawing_utils.CENTER_OFFSET,
            'INNER_RADIUS_COEFF': drawing_utils.INNER_RADIUS_COEFF,
            'OUTER_RADIUS_COEFF': drawing_utils.OUTER_RADIUS_COEFF,
            'MIDDLE_RADIUS_COEFF': drawing_utils.MIDDLE_RADIUS_COEFF,
            'NAME_LABEL_OFFSET': drawing_utils.NAME_LABEL_OFFSET,
            'MAX_LINE_WIDTH': drawing_utils.MAX_LINE_WIDTH,
            'PLOT_XLIM': drawing_utils.PLOT_XLIM,
            'PLOT_YLIM': drawing_utils.PLOT_YLIM,
            'FIGURE_SIZE': drawing_utils.FIGURE_SIZE,
            'FIGURE_DPI': drawing_utils.FIGURE_DPI,
            'ENTRY_COLORS': drawing_utils.ENTRY_COLORS,
            'DEFAULT_ROAD_LABEL_FONT_SIZE': drawing_utils.DEFAULT_ROAD_LABEL_FONT_SIZE,
            'DEFAULT_FLOW_LABEL_FONT_SIZE': drawing_utils.DEFAULT_FLOW_LABEL_FONT_SIZE,
        }
    except:
        return None

def get_root():
    """获取主窗口root对象"""
    try:
        import i18n
        if hasattr(i18n, '_ui_components') and i18n._ui_components.get('root'):
            return i18n._ui_components['root']
    except:
        pass
    return None


def plot_traffic_flow(table_instance):
    """绘制交通流量图"""
    # 检查 table_instance 是否有效
    if table_instance is None:
        messagebox.showerror(t('file_load_error'), '表格对象未找到')
        return
    
    # 配置 matplotlib 使用项目字体文件（抑制字体警告）
    try:
        import ui_utils
        # 优先使用项目字体文件
        font_file = ui_utils.get_font_file()
        if font_file:
            # 使用字体文件路径
            plt.rcParams['font.family'] = 'sans-serif'
            # 注册字体文件到 matplotlib
            fm.fontManager.addfont(font_file)
            # 获取字体名称
            try:
                from fontTools.ttLib import TTFont
                font = TTFont(font_file)
                name_table = font.get('name')
                font_name = None
                for record in name_table.names:
                    if record.nameID == 6:  # PostScript name
                        font_name = record.toUnicode()
                        break
                    elif record.nameID == 1 and font_name is None:  # Font Family name
                        font_name = record.toUnicode()
                font.close()
                if font_name:
                    plt.rcParams['font.sans-serif'] = [font_name, 'Arial', 'DejaVu Sans']
                else:
                    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
            except:
                # 如果无法读取字体名称，使用默认设置
                plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        else:
            # 如果没有字体文件，使用安全字体
            safe_font = ui_utils.get_safe_font_family()
            plt.rcParams['font.family'] = safe_font
            plt.rcParams['font.sans-serif'] = [safe_font, 'Arial', 'DejaVu Sans']
    except:
        pass
    
    # 获取绘图工具函数和常量
    drawing = get_drawing_utils()
    if drawing is None:
        messagebox.showerror(t('file_load_error'), '绘图工具模块加载失败')
        return
    
    ui_utils = get_ui_utils()
    if ui_utils is None:
        messagebox.showerror(t('file_load_error'), 'UI工具模块加载失败')
        return
    
    root = get_root()
    if root is None:
        messagebox.showerror(t('file_load_error'), '主窗口未找到')
        return
    
    # 解包绘图工具
    normalize_index = drawing['normalize_index']
    draw_line_with_width = drawing['draw_line_with_width']
    draw_arrow = drawing['draw_arrow']
    draw_arc_with_width = drawing['draw_arc_with_width']
    draw_turn_path_generic = drawing['draw_turn_path_generic']
    draw_traffic_volume_labels = drawing['draw_traffic_volume_labels']
    draw_text = drawing['draw_text']
    CENTER_OFFSET = drawing['CENTER_OFFSET']
    INNER_RADIUS_COEFF = drawing['INNER_RADIUS_COEFF']
    OUTER_RADIUS_COEFF = drawing['OUTER_RADIUS_COEFF']
    MIDDLE_RADIUS_COEFF = drawing['MIDDLE_RADIUS_COEFF']
    NAME_LABEL_OFFSET = drawing['NAME_LABEL_OFFSET']
    MAX_LINE_WIDTH = drawing['MAX_LINE_WIDTH']
    PLOT_XLIM = drawing['PLOT_XLIM']
    PLOT_YLIM = drawing['PLOT_YLIM']
    FIGURE_SIZE = drawing['FIGURE_SIZE']
    FIGURE_DPI = drawing['FIGURE_DPI']
    ENTRY_COLORS = drawing['ENTRY_COLORS']
    DEFAULT_ROAD_LABEL_FONT_SIZE = drawing['DEFAULT_ROAD_LABEL_FONT_SIZE']
    DEFAULT_FLOW_LABEL_FONT_SIZE = drawing['DEFAULT_FLOW_LABEL_FONT_SIZE']
    
    # 解包UI工具
    create_toplevel = ui_utils['create_toplevel']
    set_window_icon = ui_utils['set_window_icon']
    center_window = ui_utils['center_window']
    
    # 获取表格数据
    try:
        table_instance.get()
        data = table_instance.data
        num_entries = table_instance.num_entries
    except (AttributeError, tk.TclError) as e:
        messagebox.showerror(t('file_load_error'), f'无法获取表格数据: {str(e)}')
        return
    
    # 验证数据完整性
    required_keys = ['names', 'angles'] + [f'flow_{i}' for i in range(num_entries)]
    if not data or not all(key in data for key in required_keys):
        messagebox.showerror(t('file_load_error'), t('data_incomplete'))
        return
    
    # 验证数据是否为空
    if not any(data.get(key) for key in required_keys):
        messagebox.showerror(t('file_load_error'), t('data_empty'))
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
            messagebox.showerror(t('file_load_error'), t('data_insufficient', num=num_entries, current=min_length))
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

        # 从配置加载默认字号
        try:
            import config
            cfg = config.load_config()
            road_font_size = int(cfg.get('road_label_font_size', DEFAULT_ROAD_LABEL_FONT_SIZE))
            flow_font_size = int(cfg.get('flow_label_font_size', DEFAULT_FLOW_LABEL_FONT_SIZE))
        except:
            road_font_size = DEFAULT_ROAD_LABEL_FONT_SIZE
            flow_font_size = DEFAULT_FLOW_LABEL_FONT_SIZE

        # 限制字号范围
        def clamp_font_size(size, default):
            try:
                size = int(size)
            except:
                return default
            if size < 6:
                return 6
            if size > 30:
                return 30
            return size

        road_font_size = clamp_font_size(road_font_size, DEFAULT_ROAD_LABEL_FONT_SIZE)
        flow_font_size = clamp_font_size(flow_font_size, DEFAULT_FLOW_LABEL_FONT_SIZE)

        # 创建画布
        fig = plt.figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_aspect('equal')

        def draw_diagram(current_road_font_size, current_flow_font_size):
            """按指定字号绘制完整图形"""
            ax.clear()
            ax.set_aspect('equal')

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
                    draw_line_with_width(
                        ax,
                        start=(entry_inner_x, entry_inner_y),
                        end=(entry_outer_extended_x, entry_outer_extended_y),
                        width=entry_line_width,
                        color=ENTRY_COLORS[i],
                    )
                    
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
                    draw_line_with_width(
                        ax,
                        start=(entry_inner_x, entry_inner_y),
                        end=(entry_outer_extended_x, entry_outer_extended_y),
                        width=entry_line_width,
                        color=ENTRY_COLORS[i],
                    )
                    
                    # 计算出口流量线坐标
                    exit_inner_x = CENTER_OFFSET * np.sin(angle_rad) + INNER_RADIUS_COEFF * np.cos(angle_rad)
                    exit_inner_y = INNER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
                    exit_outer_x = CENTER_OFFSET * np.sin(angle_rad) + OUTER_RADIUS_COEFF * np.cos(angle_rad)
                    exit_outer_y = OUTER_RADIUS_COEFF * np.sin(angle_rad) - CENTER_OFFSET * np.cos(angle_rad)
                
                exit_line_width = exit_total_volumes[i] * line_width_multiplier / max_volume
                draw_line_with_width(
                    ax,
                    start=(exit_inner_x, exit_inner_y),
                    end=(exit_outer_x, exit_outer_y),
                    width=exit_line_width,
                    color=ENTRY_COLORS[i],
                )
                
                # 在出口宽度条末端添加箭头
                # 计算箭头方向向量（从exit_inner指向exit_outer）
                exit_direction = np.array([exit_outer_x - exit_inner_x, exit_outer_y - exit_inner_y])
                exit_direction_norm = np.linalg.norm(exit_direction)
                if exit_direction_norm > 1e-10:
                    exit_direction_unit = exit_direction / exit_direction_norm
                    # 箭头起点：exit_outer
                    # 箭头终点：exit_outer + 方向向量 * 45
                    arrow_start = (exit_outer_x, exit_outer_y)
                    arrow_end = (
                        exit_outer_x + exit_direction_unit[0] * 45,
                        exit_outer_y + exit_direction_unit[1] * 45,
                    )
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
                    draw_text(ax, names[i], current_road_font_size, (name_x, name_y), name_angle, "black")
                
                # 进口总量标注：只有当进口总量不为0时才显示
                if entry_total_volumes[i] != 0:
                    entry_label_x = (entry_inner_x + entry_outer_x) / 2
                    entry_label_y = (entry_inner_y + entry_outer_y) / 2
                    entry_label_angle = (angles[i] + 90) % 180 - 90
                    draw_text(
                        ax,
                        str(int(entry_total_volumes[i])),
                        current_flow_font_size,
                        (entry_label_x, entry_label_y),
                        entry_label_angle,
                        "black",
                    )
                
                # 出口总量标注：只有当出口总量不为0时才显示
                if exit_total_volumes[i] != 0:
                    exit_label_x = (exit_inner_x + exit_outer_x) / 2
                    exit_label_y = (exit_inner_y + exit_outer_y) / 2
                    exit_label_angle = (angles[i] + 90) % 180 - 90
                    draw_text(
                        ax,
                        str(int(exit_total_volumes[i])),
                        current_flow_font_size,
                        (exit_label_x, exit_label_y),
                        exit_label_angle,
                        "black",
                    )
            
            # 绘制掉头路径（流线X_X，即flows[entry_idx][entry_idx]）
            for entry_idx in range(num_entries):
                exit_idx = entry_idx  # 掉头：出口编号等于进口编号
                if flows[entry_idx][exit_idx] != 0:
                    entry_angle_rad = angles[entry_idx] * np.pi / 180
                    volume_ratio = line_width_multiplier / max_volume
                    # 获取交通规则
                    traffic_rule_local = getattr(table_instance, 'traffic_rule', 'right')
                    
                    # 计算已绘制的前面流线的累积影响（在进口处，掉头是最左边的）
                    previous_flows_sum_entry = 0.0  # 掉头是最左边的，前面没有流线
                    # 计算已绘制的前面流线的累积影响（在出口处）
                    exit_num = exit_idx + 1  # 出口编号（1-based）
                    previous_flows_sum_exit = 0.0
                    if traffic_rule_local == 'left':
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
                    if traffic_rule_local == 'left':
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
                        draw_arc_with_width(
                            ax,
                            center=(center_x, center_y),
                            radius=arc_radius,
                            start_angle=angles[entry_idx] + 90,
                            end_angle=angles[entry_idx] + 270,
                            width=u_turn_width,
                            color=ENTRY_COLORS[entry_idx % len(ENTRY_COLORS)],
                        )
            
            # 绘制其他流向路径（流线X_Y，其中X != Y）
            # 根据交通规则确定流线顺序
            traffic_rule_local = getattr(table_instance, 'traffic_rule', 'right')
            for entry_idx in range(num_entries):  # entry_idx是0-based，对应进口编号entry_idx+1
                entry_num = entry_idx + 1  # 进口编号（1-based）
                # 计算该进口的所有流向顺序
                for flow_order in range(num_entries):  # flow_order表示在进口处的顺序（0是最左边）
                    # 根据交通规则计算出口编号
                    if traffic_rule_local == 'left':
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
                        draw_turn_path_generic(
                            ax,
                            entry_idx,
                            exit_idx,
                            angles,
                            angles,
                            entry_total_volumes,
                            exit_total_volumes,
                            flows[entry_idx][exit_idx],
                            line_width_multiplier,
                            max_volume,
                            ENTRY_COLORS[entry_idx % len(ENTRY_COLORS)],
                            flows,
                            num_entries,
                            traffic_rule_local,
                        )
            
            # 标注各流向交通量
            # 根据交通规则确定流线顺序
            traffic_rule_local = getattr(table_instance, 'traffic_rule', 'right')
            for entry_idx in range(num_entries):
                entry_num = entry_idx + 1  # 进口编号（1-based）
                flow_volumes = []
                for order in range(num_entries):
                    # 根据交通规则计算出口编号
                    if traffic_rule_local == 'left':
                        # 左行规则：从X开始顺时针递增：X, X+1, X+2, ..., 1
                        exit_num = normalize_index(entry_num + order, num_entries)
                    else:
                        # 右行规则：从X开始逆时针递减：X, X-1, X-2, ..., 1
                        exit_num = normalize_index(entry_num - order, num_entries)
                    exit_idx = exit_num - 1
                    flow_volumes.append(flows[entry_idx][exit_idx])
                draw_traffic_volume_labels(
                    ax,
                    entry_idx,
                    angles[entry_idx],
                    flow_volumes,
                    num_entries,
                    traffic_rule_local,
                    flow_font_size=current_flow_font_size,
                )
            
            plt.xlim(PLOT_XLIM[0], PLOT_XLIM[1])
            plt.ylim(PLOT_YLIM[0], PLOT_YLIM[1])
            plt.gca().set_axis_off()
            plt.tight_layout()
        
        # 先按配置字号绘制一次
        draw_diagram(road_font_size, flow_font_size)
        
        # 创建新的tkinter窗口来显示图形
        plot_window = create_toplevel(root)
        
        # 立即隐藏窗口，避免闪现
        plot_window.withdraw()
        # 先设置一个临时位置（屏幕外），避免在左上角闪现
        plot_window.geometry("1x1+-10000+-10000")
        
        # 设置窗口图标
        set_window_icon(plot_window)
        
        if table_instance.file_name:
            # 去掉文件扩展名显示
            file_name = os.path.basename(table_instance.file_name)
            plot_title = os.path.splitext(file_name)[0]
        else:
            plot_title = t('plot_title')
        plot_window.title(plot_title)
        
        # 先创建并pack工具栏框架（确保它占据底部空间）
        toolbar_frame = tk.Frame(plot_window, bg='#f5f5f5', relief='flat', padx=10, pady=5)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 将matplotlib图形嵌入到tkinter窗口
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # ===== 导出与字号控制工具栏 =====
        size_state = {
            'road': road_font_size,
            'flow': flow_font_size,
        }

        # 导出按钮
        def export_figure():
            # 定义文件类型（使用翻译）
            filetypes = [
                (t('export_filetype_svg'), "*.svg"),  # SVG作为默认格式
                (t('export_filetype_pdf'), "*.pdf"),
                (t('export_filetype_png'), "*.png"),
                (t('export_filetype_jpg'), "*.jpg"),
                (t('export_filetype_tif'), "*.tif"),
            ]
            
            # 获取默认文件名（使用翻译）
            if table_instance.file_name:
                default_name = os.path.splitext(os.path.basename(table_instance.file_name))[0]
            else:
                default_name = t('export_default_filename')
            
            # 打开保存对话框
            filename = filedialog.asksaveasfilename(
                defaultextension='.svg',  # SVG作为默认格式
                filetypes=filetypes,
                initialfile=default_name,
                title=t('btn_export')
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
                        messagebox.showerror(t('file_load_error'), t('export_format_error', ext=ext))
                        return
                    
                    # 保存图形
                    fig.savefig(filename, format=format, dpi=FIGURE_DPI, bbox_inches='tight', pad_inches=0.1)
                    messagebox.showinfo(t('file_saved_success'), t('export_success', file=filename))
                except Exception as e:
                    messagebox.showerror(t('file_load_error'), t('export_error', error=str(e)))
        
        export_button = ttk.Button(toolbar_frame, text=t('btn_export'), command=export_figure)
        export_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 数字输入校验：只允许整数或空字符串
        def validate_int(P):
            if P == "":
                return True
            return P.isdigit()

        vcmd = (toolbar_frame.register(validate_int), '%P')

        # 路名字号
        road_label = ttk.Label(toolbar_frame, text=t('road_label_font_size'))
        road_label.pack(side=tk.LEFT, padx=(15, 5), pady=5)
        road_var = tk.StringVar(value=str(road_font_size))
        road_entry = ttk.Entry(
            toolbar_frame,
            width=4,
            textvariable=road_var,
            validate='key',
            validatecommand=vcmd,
        )
        road_entry.pack(side=tk.LEFT, padx=(0, 10), pady=5)

        # 流量字号
        flow_label = ttk.Label(toolbar_frame, text=t('flow_label_font_size'))
        flow_label.pack(side=tk.LEFT, padx=(5, 5), pady=5)
        flow_var = tk.StringVar(value=str(flow_font_size))
        flow_entry = ttk.Entry(
            toolbar_frame,
            width=4,
            textvariable=flow_var,
            validate='key',
            validatecommand=vcmd,
        )
        flow_entry.pack(side=tk.LEFT, padx=(0, 10), pady=5)

        def get_valid_size(text_value, key):
            """从输入框获取合法字号，否则恢复为上一次正确数值"""
            last = size_state[key]
            text_value = text_value.strip()
            if not text_value:
                # 空值直接恢复
                return last
            try:
                value = int(text_value)
            except:
                return last
            if value < 6 or value > 30:
                return last
            return value

        def on_reset_font_size():
            """重置路名和流量字号为内置默认值"""
            new_road = DEFAULT_ROAD_LABEL_FONT_SIZE
            new_flow = DEFAULT_FLOW_LABEL_FONT_SIZE

            size_state['road'] = new_road
            size_state['flow'] = new_flow

            road_var.set(str(new_road))
            flow_var.set(str(new_flow))

            # 重绘
            draw_diagram(new_road, new_flow)
            canvas.draw_idle()

            # 将重置后的字号写回配置
            try:
                import config as _cfg_mod
                _cfg_mod.save_config(
                    table=table_instance,
                    road_label_font_size=new_road,
                    flow_label_font_size=new_flow,
                )
            except:
                pass

        def on_redraw(event=None):
            # 解析并校验新字号
            new_road = get_valid_size(road_var.get(), 'road')
            new_flow = get_valid_size(flow_var.get(), 'flow')

            # 如果输入非法，恢复文本为上一次合法值
            if str(new_road) != road_var.get().strip():
                road_var.set(str(new_road))
            if str(new_flow) != flow_var.get().strip():
                flow_var.set(str(new_flow))

            size_state['road'] = new_road
            size_state['flow'] = new_flow

            # 重绘
            draw_diagram(new_road, new_flow)
            canvas.draw_idle()

            # 成功重绘后将配置写回文件
            try:
                import config as _cfg_mod
                _cfg_mod.save_config(table=table_instance,
                                     road_label_font_size=new_road,
                                     flow_label_font_size=new_flow)
            except:
                pass

        # 重置字号按钮（排在重绘按钮前面）
        reset_button = ttk.Button(toolbar_frame, text=t('btn_reset_font_size'), command=on_reset_font_size)
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 重绘按钮（与按回车效果相同）
        redraw_button = ttk.Button(toolbar_frame, text=t('btn_redraw'), command=on_redraw)
        redraw_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 回车键触发重绘
        road_entry.bind('<Return>', on_redraw)
        flow_entry.bind('<Return>', on_redraw)
        
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
        messagebox.showerror(t('file_load_error'), t('draw_error', error=str(e)))

