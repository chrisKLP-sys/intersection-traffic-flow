# -*- coding: utf-8 -*-
"""
绘图工具函数模块
包含所有绘图相关的辅助函数和常量
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.text import TextPath
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import matplotlib.font_manager as fm
import os

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

# 文本默认字号（用于与外部配置联动）
# 路名标注默认字号
DEFAULT_ROAD_LABEL_FONT_SIZE = 15
# 流量标注（包括进口/出口总量与各转向流量数字）默认字号
DEFAULT_FLOW_LABEL_FONT_SIZE = 12

# 绘图参数
MAX_LINE_WIDTH = 10  # 最大线宽倍数
PLOT_XLIM = (-375, 375)  # 绘图X轴范围
PLOT_YLIM = (-375, 375)  # 绘图Y轴范围
FIGURE_SIZE = (10, 10)  # 图形尺寸
FIGURE_DPI = 100  # 图形分辨率

# 颜色配置（扩展到6种颜色以支持3-6路交叉口）
ENTRY_COLORS = ['red', '#27a5d6', '#d161a3', 'orange', 'green', 'purple']


# ==================== 绘图工具函数 ====================

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


def draw_line_with_width(ax, start, end, width, color):
    """画直线宽度条"""
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


def create_line(p1, p2):
    """创建直线方程"""
    a = p2[1] - p1[1]
    b = p1[0] - p2[0]
    c = p2[0] * p1[1] - p1[0] * p2[1]
    return {'a': a, 'b': b, 'c': c}


def create_perpendicular_line(line, point):
    """创建垂直于给定直线并经过指定点的直线"""
    a, b = line['b'], -line['a']
    c = -(a * point[0] + b * point[1])
    return {'a': a, 'b': b, 'c': c}


def find_intersection(line1, line2):
    """计算两条直线的交点"""
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
    """生成圆弧上的点"""
    start_angle = start_angle % 360
    end_angle = end_angle % 360

    if end_angle <= start_angle:
        end_angle += 360

    angles = np.linspace(np.radians(start_angle), np.radians(end_angle), num_points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return np.column_stack((x, y))


def transfor_arc_to_width_bar(arc, width, color='blue', ax=None, num_points=100):
    """将圆弧转换为宽度条"""
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
    """判断三点是否共线"""
    AB = np.array([p2[0] - p1[0], p2[1] - p1[1]])
    AC = np.array([p3[0] - p1[0], p3[1] - p1[1]])
    
    cross_product = AB[0] * AC[1] - AB[1] * AC[0]
    
    return abs(cross_product) < epsilon


def create_parallel_arcs_with_width(ax, p1, p2, p3, p4, width=0.1, color='red'):
    """创建平行弧线并添加宽度"""
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


def create_wide_line_with_arc(ax, p1, p2, p3, p4, start_angle, end_angle, line_width=0.1, color='red'):
    """执行圆角操作，在两条直线间创建圆弧，并对直线修饰"""
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

        start_x = p3[0]
        end_x = p5[0]
        start_y = p3[1]
        end_y = p5[1]

    elif dist_Op2 == dist_Op3:
        p5 = p3
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

        start_x = p2[0]
        end_x = p5[0]
        start_y = p2[1]
        end_y = p5[1]

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


def draw_arc_with_width(ax, center, radius, start_angle, end_angle, width, color):
    """画圆弧宽度条"""
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


def draw_traffic_volume_labels(
    ax,
    entry_index,
    entry_angle,
    flow_volumes,
    num_entries,
    traffic_rule='right',
    flow_font_size=DEFAULT_FLOW_LABEL_FONT_SIZE,
):
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
    # 行间距随字号同比例缩放
    base_spacing = 12.0
    # 避免除零
    size_scale = flow_font_size / DEFAULT_FLOW_LABEL_FONT_SIZE if DEFAULT_FLOW_LABEL_FONT_SIZE > 0 else 1.0
    spacing = base_spacing * size_scale

    if len(non_zero_labels) == 1:
        # 只有一个非0标注，将其放在中心位置（偏移为0）
        adjusted_labels = [(flow_idx, volume, 0) for flow_idx, volume, _ in non_zero_labels]
    else:
        # 按原始偏移量从大到小排序（保持原始顺序）
        sorted_labels = sorted(non_zero_labels, key=lambda x: x[2], reverse=True)
        
        # 计算需要重新排列的位置
        # 保持间距spacing，以0为中心对称分布
        num_labels = len(sorted_labels)
        
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
        draw_text(ax, str(int(volume)), flow_font_size, (label_x, label_y), label_angle, "black")


def draw_text(ax, text, fontsize, center, angle, color, fontname=None):
    """创建矢量图文字"""
    # 延迟导入i18n模块以获取字体
    try:
        import i18n
        # 尝试从i18n获取全局字体
        if hasattr(i18n, 'font'):
            font_prop = i18n.font
        else:
            # 如果没有全局字体，使用默认字体
            font_prop = None
    except:
        font_prop = None
    
    # 如果没有指定字体，使用全局字体设置
    if fontname is None:
        if font_prop is None:
            # 尝试从ui_utils获取字体（优先使用项目字体文件）
            try:
                import ui_utils
                # 优先使用项目字体文件（如果存在）
                font_file = ui_utils.get_font_file()
                if font_file:
                    font_prop = fm.FontProperties(fname=font_file, size=fontsize)
                else:
                    # 使用安全的字体获取函数，避免使用不存在的字体
                    safe_font_family = ui_utils.get_font_family()
                    font_prop = fm.FontProperties(family=safe_font_family, size=fontsize)
            except:
                # 如果获取字体失败，使用默认字体（不指定family，让matplotlib自动选择）
                font_prop = fm.FontProperties(size=fontsize)
        else:
            # 使用全局字体，但调整大小
            font_prop = fm.FontProperties(fname=font_prop.get_file() if hasattr(font_prop, 'get_file') else None,
                                         family=font_prop.get_name() if hasattr(font_prop, 'get_name') else None,
                                         size=fontsize)
    elif os.path.exists(fontname):
        font_prop = fm.FontProperties(fname=fontname, size=fontsize)
    else:
        # 如果路径不存在，尝试使用字体名称（使用安全的字体获取方法）
        try:
            import ui_utils
            # 验证字体是否存在，如果不存在则使用安全字体
            safe_font_family = ui_utils.get_safe_font_family(default=fontname)
            font_prop = fm.FontProperties(family=safe_font_family, size=fontsize)
        except:
            # 如果获取字体失败，使用默认字体
            font_prop = fm.FontProperties(size=fontsize)
    
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

