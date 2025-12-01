# -*- coding: utf-8 -*-
"""配置管理模块"""
import os
import sys

# ==================== 配置文件管理 ====================
CONFIG_FILE = 'config.txt'

def get_config_path():
    """获取配置文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件，配置文件保存在可执行文件目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境，配置文件保存在脚本目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, CONFIG_FILE)

def load_config():
    """加载配置文件"""
    config_path = get_config_path()
    default_config = {
        'language': 'zh_CN',
        'traffic_rule': 'right',
        # 绘图文字默认字号（与 drawing_utils 中的默认值保持一致）
        'road_label_font_size': 15,
        'flow_label_font_size': 12,
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释行（以#开头的行）
                    if not line or line.startswith('#'):
                        continue
                    # 解析键值对：key=value 或 key: value
                    if '=' in line:
                        key, value = line.split('=', 1)
                    elif ':' in line:
                        key, value = line.split(':', 1)
                    else:
                        continue
                    key = key.strip()
                    value = value.strip()
                    # 验证并设置配置值
                    # 延迟导入i18n模块，避免循环依赖
                    if key == 'language':
                        try:
                            import i18n
                            if value in i18n.LANGUAGES:
                                default_config['language'] = value
                        except:
                            if value in ['zh_CN', 'en_US']:
                                default_config['language'] = value
                    elif key == 'traffic_rule' and value in ['left', 'right']:
                        default_config['traffic_rule'] = value
                    elif key == 'road_label_font_size':
                        try:
                            size = int(value)
                            if 6 <= size <= 30:
                                default_config['road_label_font_size'] = size
                        except:
                            pass
                    elif key == 'flow_label_font_size':
                        try:
                            size = int(value)
                            if 6 <= size <= 30:
                                default_config['flow_label_font_size'] = size
                        except:
                            pass
        except Exception as e:
            # 如果读取失败，使用默认值
            print(f"加载配置文件失败: {e}")
    
    return default_config

def save_config(table=None, road_label_font_size=None, flow_label_font_size=None):
    """保存配置文件
    
    参数:
        table: Table对象，用于获取traffic_rule。如果为None，使用默认值'right'
    """
    config_path = get_config_path()
    # 先加载现有配置，保证未指定的字段保持不变
    current = load_config()
    # 延迟导入i18n模块，避免循环依赖
    try:
        import i18n
        language = i18n.CURRENT_LANGUAGE
    except:
        language = 'zh_CN'
    
    # 获取traffic_rule
    if table and hasattr(table, 'traffic_rule'):
        traffic_rule = table.traffic_rule
    else:
        traffic_rule = current.get('traffic_rule', 'right')  # 默认值或现有配置

    # 处理字号配置
    if road_label_font_size is None:
        road_label_font_size = current.get('road_label_font_size', 15)
    if flow_label_font_size is None:
        flow_label_font_size = current.get('flow_label_font_size', 12)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("# 交叉口交通流量流向可视化工具配置文件 / Intersection Traffic Flow Visualization Tool Config File\n")
            f.write("# 此文件由程序自动生成，可以手动编辑 / This file is auto-generated and can be manually edited\n")
            f.write("#\n")
            f.write("# 语言设置 / Language Setting:\n")
            f.write("#   zh_CN - 简体中文 (Simplified Chinese)\n")
            f.write("#   en_US - English (英语)\n")
            f.write("#\n")
            f.write("# 通行规则 / Traffic Rule:\n")
            f.write("#   left  - 左行 (Left-hand traffic)\n")
            f.write("#   right - 右行 (Right-hand traffic)\n")
            f.write("#\n")
            f.write("# 绘图文字字号 / Plot Text Sizes:\n")
            f.write("#   road_label_font_size  - 路名标注字号 / Road name label size\n")
            f.write("#   flow_label_font_size  - 流量标注字号 / Flow value label size\n")
            f.write("#\n")
            f.write(f"language={language}\n")
            f.write(f"traffic_rule={traffic_rule}\n")
            f.write(f"road_label_font_size={road_label_font_size}\n")
            f.write(f"flow_label_font_size={flow_label_font_size}\n")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


# 获取当前table对象的traffic_rule（供外部调用）
def get_traffic_rule():
    """获取当前交通规则"""
    # 这个函数需要从外部传入table对象，或者使用全局变量
    # 暂时返回默认值
    return 'right'
