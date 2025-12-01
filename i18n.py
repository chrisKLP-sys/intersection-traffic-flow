# -*- coding: utf-8 -*-
"""多语言支持模块"""
import os
import sys

# ==================== 多语言支持 ====================
# 语言字典
LANGUAGES = {
    'zh_CN': {
        # 窗口标题
        'app_title': '交叉口交通流量流向可视化工具',
        'app_title_unsaved': '交叉口交通流量流向可视化工具 - 未保存',
        'plot_title': '交叉口交通流量流向可视化图',
        
        # 选择对话框
        'select_intersection_type': '请选择交叉口类型或读取文件：',
        'btn_3way': '3路交叉口',
        'btn_4way': '4路交叉口',
        'btn_5way': '5路交叉口',
        'btn_6way': '6路交叉口',
        'btn_load_file': '读取数据文件',
        
        # 表格相关
        'entry_number': '进口编号',
        'entry_name': '进口名称',
        'angle': '方位角',
        'important_notice': '重要提醒',
        'notice_content': "1. '方位角'以正东方向为0度，逆时针增加。例如：0度 = 正东，90度 = 正北，180度 = 正西，270度 = 正南。\n2. 请注意转向流量的输入顺序，以道路中心线为基准，靠近中心线的流线优先输入，例如，右行规则下，4路交叉口的输入顺序分别为：掉头、左转、直行、右转，左行规则下则为：掉头、右转、直行、左转。",
        'entry': '进口',
        'u_turn': '掉头',
        'left_turn': '左转',
        'straight': '直行',
        'right_turn': '右转',
        'flow_line': '流线X_X',
        'flow_line_n': '流线X_X-{n}',
        
        # 交通规则
        'traffic_rule': '交通规则：',
        'right_hand_rule': '右行规则',
        'left_hand_rule': '左行规则',
        
        # 按钮
        'btn_draw': '绘制流量图',
        'btn_save': '保存数据',
        'btn_save_as': '数据另存为',
        'btn_load': '读取数据',
        'btn_help': '帮助',
        'btn_export': '导出图片',
        'road_label_font_size': '路名字号',
        'flow_label_font_size': '流量字号',
        'btn_reset_font_size': '重置字号',
        'btn_redraw': '重绘',
        
        # 文件操作
        'file_saved': '数据已保存到 {file}',
        'file_saved_success': '成功',
        'file_no_save_target': '没有可保存的文件。请先加载文件。',
        'file_load_success': '数据加载成功！已识别为{num}路交叉口。',
        'file_load_error': '错误',
        'file_save_error': '保存文件时出错：{error}',
        'file_load_error_msg': '读取文件时出错：{error}',
        'file_empty': '文件为空。',
        'file_encoding_error': '无法读取文件 {file}，请检查文件编码。',
        'file_format_error_infer': '文件格式不正确，无法推断交叉口路数。',
        'file_num_entries_error': '交叉口路数错误，请核对数据后再读取',
        'file_num_entries_infer_error': '无法从数据推断路数，推断结果为{num}路，不在有效范围内（3-6路）',
        'file_read_error': '无法读取文件。',
        'file_cannot_parse': '文件无法解析，请重新选择数据文件。',
        
        # 数据验证
        'data_empty': '数据为空，请先输入或加载数据',
        'data_insufficient': '数据不足，至少需要{num}个进口的数据，当前只有 {current} 个',
        
        # 导出
        'export_success': '图片已保存到：\n{file}',
        'export_error': '保存图片时出错：{error}',
        'export_format_error': '不支持的格式：{ext}\n仅支持：svg, pdf, png, jpg, tif',
        'export_filetype_svg': 'SVG 矢量图',
        'export_filetype_pdf': 'PDF 文档',
        'export_filetype_png': 'PNG 图片',
        'export_filetype_jpg': 'JPG 图片',
        'export_filetype_tif': 'TIF 图片',
        'export_default_filename': '交叉口交通流量流向可视化图',
        
        # 文件格式
        'file_declaration': '本交叉口为{num}路交叉口，实行{rule}行通行规则。',
        'right_hand': '右',
        'left_hand': '左',
        
        # 其他按钮
        'btn_new_file': '新建文件',
        'btn_clear_data': '清空数据',
        'btn_about': '关于',
        
        # 其他消息
        'parse_error': '解析数据时出错：{error}',
        'draw_error': '绘制图形时出错：{error}',
        'data_cleared': '数据已清空',
        'new_table_created': '已创建新的{num}路交叉口数据表格',
        'help_file_not_found': '未找到帮助文档文件。\n\n预期位置：{file}\n\n请确保帮助文档.html文件与程序在同一目录。',
        'help_file_error': '无法打开帮助文档：{error}\n\n备用方法也失败：{error2}\n\n帮助文档位置：{file}',
        'data_incomplete': '数据不完整，请先输入或加载数据',
        'confirm': '确认',
        'confirm_clear': '确定要清空所有数据吗？',
        'confirm_new_file': '当前数据已修改，确定要新建文件吗？未保存的修改将丢失。',
        'about': '关于',
        
        # 打赏相关
        'btn_donate': '打赏',
        'donate_title': '打赏支持',
        'donate_message': '一分也是爱 ❤️\n\n您的支持，是我持续维护和升级此软件的最大动力。\n\n不打赏也没关系，所有功能永久免费开放。\n\n感谢每一位同行的信任与鼓励！\n\n如果提示"验证姓氏"，请输入"何"',
        
        # 更新相关
        'btn_check_update': '检查更新',
        'update_checking': '正在检查更新...',
        'update_downloading_title': '正在下载更新',
        'update_checking_github': '正在从GitHub检查更新...',
        'update_checking_gitee': '正在从Gitee检查更新...',
        'update_available': '发现新版本',
        'update_available_msg': '发现新版本 {version}！\n当前版本：{current}\n\n是否立即下载并更新？',
        'update_latest': '已是最新版本',
        'update_latest_msg': '您当前使用的是最新版本 {version}。',
        'update_downloading': '正在下载更新...',
        'update_download_progress': '下载进度：{percent}% ({downloaded}/{total})',
        'update_download_success': '下载完成！',
        'update_download_failed': '下载失败',
        'update_download_failed_msg': '下载更新失败：{error}',
        'update_install_failed': '安装失败',
        'update_install_failed_msg': '安装更新时出错：{error}',
        'update_error': '更新检查失败',
        'update_error_msg': '检查更新时出错：{error}',
        'update_network_error': '网络连接失败',
        'update_network_error_msg': '请检查网络连接或VPN设置，或者稍后再试',
        'update_prepared': '更新已准备',
        'update_prepared_msg': '下载已完成，重启软件后生效',
        'update_restart_now': '立即重启软件',
        'update_install_restart_failed': '安装失败',
        'update_install_restart_failed_msg': '安装更新时出错：{error}',
        'update_no_download': '未找到下载链接',
        'update_no_download_msg': '未找到可用的下载链接。',
        'update_source_select': '选择更新源',
        'update_source_gitee': 'Gitee',
        'update_source_github': 'GitHub',
        'update_source_gitee_note': 'Gitee（推荐中国大陆用户使用）',
        'update_source_github_note': 'GitHub（推荐中国大陆以外用户使用）',
        'update_source_gitee_button': '从Gitee更新',
        'update_source_github_button': '从GitHub更新',
        'update_cancel': '取消',
        'update_download_and_install': '直接更新',
        'update_save_as': '新版本另存为',
        'update_skip': '跳过',
        'update_close': '关闭',
        'update_release_notes': '更新说明：',
        'update_save_success': '保存成功',
        'update_save_success_msg': '新版本已保存到：{path}',
        'update_auto_available': '发现新版本',
        'update_auto_available_msg': '发现新版本 {version}！\n当前版本：{current}\n更新源：{source}\n\n是否立即更新？',
        'update_now': '立即更新',
        'update_later': '稍后提醒',
    },
    'en_US': {
        # Window titles
        'app_title': 'Intersection Traffic Flow Visualization Tool',
        'app_title_unsaved': 'Intersection Traffic Flow Visualization Tool - Unsaved',
        'plot_title': 'Intersection Traffic Flow Visualization',
        
        # Selection dialog
        'select_intersection_type': 'Please select intersection type or load file:',
        'btn_3way': '3-Way Intersection',
        'btn_4way': '4-Way Intersection',
        'btn_5way': '5-Way Intersection',
        'btn_6way': '6-Way Intersection',
        'btn_load_file': 'Load Data File',
        
        # Table related
        'entry_number': 'Entry No.',
        'entry_name': 'Entry Name',
        'angle': 'Angle',
        'important_notice': 'Important Notice',
        'notice_content': "1. 'Angle' is measured from due east (0°), increasing counterclockwise. Example: 0° = East, 90° = North, 180° = West, 270° = South.\n2. Please note the input order of turning flows. Based on the road centerline, flows closer to the centerline should be entered first. For example, under right-hand traffic rule, the input order for a 4-way intersection is: U-turn, Left turn, Straight, Right turn. Under left-hand traffic rule, it is: U-turn, Right turn, Straight, Left turn.",
        'entry': 'Entry',
        'u_turn': 'U-Turn',
        'left_turn': 'Left Turn',
        'straight': 'Straight',
        'right_turn': 'Right Turn',
        'flow_line': 'Flow X_X',
        'flow_line_n': 'Flow X_X-{n}',
        
        # Traffic rules
        'traffic_rule': 'Traffic Rule:',
        'right_hand_rule': 'Right-Hand Traffic',
        'left_hand_rule': 'Left-Hand Traffic',
        
        # Buttons
        'btn_draw': 'Draw Flow Diagram',
        'btn_save': 'Save Data',
        'btn_save_as': 'Save As',
        'btn_load': 'Load Data',
        'btn_help': 'Help',
        'btn_export': 'Export Image',
        'road_label_font_size': 'Road label size',
        'flow_label_font_size': 'Flow label size',
        'btn_reset_font_size': 'Reset font size',
        'btn_redraw': 'Redraw',
        
        # File operations
        'file_saved': 'Data saved to {file}',
        'file_saved_success': 'Success',
        'file_no_save_target': 'No file to save to. Please load a file first.',
        'file_load_success': 'Data loaded successfully! Identified as {num}-way intersection.',
        'file_load_error': 'Error',
        'file_save_error': 'Error saving file: {error}',
        'file_load_error_msg': 'Error reading file: {error}',
        'file_empty': 'File is empty.',
        'file_encoding_error': 'Cannot read file {file}, please check file encoding.',
        'file_format_error_infer': 'Invalid file format. Cannot infer intersection type.',
        'file_num_entries_error': 'Intersection type error. Please check data before reading.',
        'file_num_entries_infer_error': 'Cannot infer intersection type from data. Inferred result is {num}-way, not in valid range (3-6 ways)',
        'file_read_error': 'Cannot read file.',
        'file_cannot_parse': 'The file cannot be parsed. Please select another data file.',
        
        # Data validation
        'data_empty': 'Data is empty. Please enter or load data first.',
        'data_insufficient': 'Insufficient data. At least {num} entry data required, currently only {current} entries.',
        
        # Export
        'export_success': 'Image saved to:\n{file}',
        'export_error': 'Error saving image: {error}',
        'export_format_error': 'Unsupported format: {ext}\nSupported formats: svg, pdf, png, jpg, tif',
        'export_filetype_svg': 'SVG Vector Image',
        'export_filetype_pdf': 'PDF Document',
        'export_filetype_png': 'PNG Image',
        'export_filetype_jpg': 'JPG Image',
        'export_filetype_tif': 'TIF Image',
        'export_default_filename': 'Intersection Traffic Flow Visualization',
        
        # File format
        'file_declaration': 'This intersection is a {num}-way intersection, implementing {rule}-hand traffic rule.',
        'right_hand': 'right',
        'left_hand': 'left',
        
        # Other buttons
        'btn_new_file': 'New File',
        'btn_clear_data': 'Clear Data',
        'btn_about': 'About',
        
        # Donation related
        'btn_donate': 'Tip',
        'donate_title': 'Tip Support',
        'donate_message': 'Every penny counts! ❤️\n\nYour support is the greatest motivation for me to continue maintaining and upgrading this software.\n\nNo tip is fine, all features are permanently free.\n\nThank you for every colleague\'s trust and encouragement!\n\nIf prompted for "verification surname", please enter "何"',
        # Other messages
        'parse_error': 'Error parsing data: {error}',
        'draw_error': 'Error drawing diagram: {error}',
        'data_cleared': 'Data cleared',
        'new_table_created': 'Created new {num}-way intersection data table',
        'help_file_not_found': 'Help file not found.\n\nExpected location: {file}\n\nPlease ensure help.html is in the same directory as the program.',
        'help_file_error': 'Cannot open help file: {error}\n\nFallback method also failed: {error2}\n\nHelp file location: {file}',
        'data_incomplete': 'Data incomplete. Please enter or load data first.',
        'confirm': 'Confirm',
        'confirm_clear': 'Are you sure you want to clear all data?',
        'confirm_new_file': 'Current data has been modified. Are you sure you want to create a new file? Unsaved changes will be lost.',
        'about': 'About',
        
        # Update related
        'btn_check_update': 'Check for Updates',
        'update_checking': 'Checking for updates...',
        'update_downloading_title': 'Downloading Update',
        'update_checking_github': 'Checking for updates from GitHub...',
        'update_checking_gitee': 'Checking for updates from Gitee...',
        'update_available': 'Update Available',
        'update_available_msg': 'New version {version} is available!\nCurrent version: {current}\n\nWould you like to download and update now?',
        'update_latest': 'Up to Date',
        'update_latest_msg': 'You are using the latest version {version}.',
        'update_downloading': 'Downloading update...',
        'update_download_progress': 'Download progress: {percent}% ({downloaded}/{total})',
        'update_download_success': 'Download complete!',
        'update_download_failed': 'Download failed',
        'update_download_failed_msg': 'Failed to download update: {error}',
        'update_install_failed': 'Installation failed',
        'update_install_failed_msg': 'Error installing update: {error}',
        'update_error': 'Update check failed',
        'update_error_msg': 'Error checking for updates: {error}',
        'update_network_error': 'Network connection failed',
        'update_network_error_msg': 'Please check your network connection or VPN settings, or try again later',
        'update_prepared': 'Update prepared',
        'update_prepared_msg': 'Download completed, will take effect after restarting the software',
        'update_restart_now': 'Restart software now',
        'update_install_restart_failed': 'Installation failed',
        'update_install_restart_failed_msg': 'Error installing update: {error}',
        'update_no_download': 'No download link found',
        'update_no_download_msg': 'No available download link found.',
        'update_source_select': 'Select Update Source',
        'update_source_gitee': 'Gitee',
        'update_source_github': 'GitHub',
        'update_source_gitee_note': 'Gitee (Recommended for users in Mainland China)',
        'update_source_github_note': 'GitHub (Recommended for users outside Mainland China)',
        'update_source_gitee_button': 'Update from Gitee',
        'update_source_github_button': 'Update from GitHub',
        'update_cancel': 'Cancel',
        'update_download_and_install': 'Update Now',
        'update_save_as': 'Save As',
        'update_skip': 'Skip',
        'update_close': 'Close',
        'update_release_notes': 'Release Notes:',
        'update_save_success': 'Save Success',
        'update_save_success_msg': 'New version saved to: {path}',
        'update_auto_available': 'Update Available',
        'update_auto_available_msg': 'New version {version} is available!\nCurrent version: {current}\nUpdate source: {source}\n\nWould you like to update now?',
        'update_now': 'Update Now',
        'update_later': 'Remind Me Later',
    }
}

# 全局变量：存储需要更新的界面组件引用
_ui_components = {
    'buttons': {},
    'labels': {},
    'menu_items': {},
    'table': None,
    'root': None,
}

# 当前语言（默认简体中文）
CURRENT_LANGUAGE = 'zh_CN'

def t(key, **kwargs):
    """翻译函数，获取当前语言的文本"""
    if CURRENT_LANGUAGE in LANGUAGES and key in LANGUAGES[CURRENT_LANGUAGE]:
        text = LANGUAGES[CURRENT_LANGUAGE][key]
        # 支持格式化字符串
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text
    # 如果找不到翻译，返回key本身
    return key

def set_language(lang_code):
    """设置当前语言"""
    global CURRENT_LANGUAGE
    if lang_code in LANGUAGES:
        CURRENT_LANGUAGE = lang_code
        # 保存配置（延迟保存，避免频繁写入）
        # 延迟导入config模块，避免循环依赖
        # 尝试从_ui_components获取table对象
        try:
            import config
            table = _ui_components.get('table')
            config.save_config(table=table)
        except:
            pass
        return True
    return False

def update_ui_language():
    """更新所有界面文本为当前语言"""
    global _ui_components
    
    try:
        # 更新窗口标题
        if _ui_components.get('root'):
            try:
                table = _ui_components.get('table')
                if table and hasattr(table, 'file_name') and table.file_name:
                    file_name = os.path.basename(table.file_name)
                    file_name_without_ext = os.path.splitext(file_name)[0]
                    if table and hasattr(table, 'is_modified') and table.is_modified:
                        _ui_components['root'].title(f"{file_name_without_ext} - {t('app_title_unsaved').split(' - ')[-1]}")
                    else:
                        _ui_components['root'].title(file_name_without_ext)
                else:
                    if table and hasattr(table, 'is_modified') and table.is_modified:
                        _ui_components['root'].title(t('app_title_unsaved'))
                    else:
                        _ui_components['root'].title(t('app_title'))
            except Exception as e:
                # 如果更新标题失败，至少设置基本标题
                try:
                    _ui_components['root'].title(t('app_title'))
                except:
                    pass
        
        # 更新按钮文本
        buttons = _ui_components.get('buttons', {})
        try:
            if 'new_file' in buttons and buttons['new_file']:
                buttons['new_file'].config(text=t('btn_new_file'))
        except:
            pass
        try:
            if 'load' in buttons and buttons['load']:
                buttons['load'].config(text=t('btn_load'))
        except:
            pass
        try:
            if 'clear_data' in buttons and buttons['clear_data']:
                buttons['clear_data'].config(text=t('btn_clear_data'))
        except:
            pass
        try:
            if 'save' in buttons and buttons['save']:
                buttons['save'].config(text=t('btn_save'))
        except:
            pass
        try:
            if 'save_as' in buttons and buttons['save_as']:
                buttons['save_as'].config(text=t('btn_save_as'))
        except:
            pass
        try:
            if 'plot' in buttons and buttons['plot']:
                buttons['plot'].config(text=t('btn_draw'))
        except:
            pass
        try:
            if 'help' in buttons and buttons['help']:
                buttons['help'].config(text=t('btn_help'))
        except:
            pass
        try:
            if 'about' in buttons and buttons['about']:
                buttons['about'].config(text=t('btn_about'))
        except:
            pass
        
        # 更新表格（如果存在且有效）
        table = _ui_components.get('table')
        if table:
            try:
                # 检查table对象是否仍然有效（没有被销毁）
                # Table继承自tk.Frame，应该有winfo_exists方法
                if hasattr(table, 'winfo_exists'):
                    try:
                        exists = table.winfo_exists()
                        if exists and hasattr(table, 'update_language'):
                            table.update_language()
                    except:
                        # 如果检查失败，尝试直接调用update_language
                        if hasattr(table, 'update_language'):
                            table.update_language()
                elif hasattr(table, 'update_language'):
                    # 如果没有winfo_exists方法，直接尝试调用
                    table.update_language()
            except Exception as e:
                # 如果更新表格失败，打印错误但不影响其他组件更新
                print(f"更新表格语言失败: {e}")
    except Exception as e:
        print(f"更新界面语言时出错: {e}")

def change_language(lang_code):
    """切换语言（全局生效）"""
    if set_language(lang_code):
        # 更新主界面（如果已创建）
        if _ui_components.get('root'):
            update_ui_language()
            # 重新调整窗口大小以适应新的文本长度（保持位置）
            root = _ui_components.get('root')
            if root:
                # 延迟导入ui_utils模块，避免循环依赖
                try:
                    import ui_utils
                    ui_utils.adjust_window_size(root)
                except:
                    pass
        return True
    return False

