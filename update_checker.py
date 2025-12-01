# -*- coding: utf-8 -*-
"""
更新检查模块
支持从GitHub和Gitee检查并下载更新
"""

import urllib.request
import urllib.error
import json
import os
import sys
import re
import threading
import tempfile
import shutil
import subprocess
import platform

# GitHub和Gitee仓库信息
GITHUB_OWNER = "chrisKLP-sys"
GITHUB_REPO = "intersection-traffic-flow"
GITEE_OWNER = "Chris_KLP"
GITEE_REPO = "intersection-traffic-flow"

# API端点
GITHUB_API_LATEST = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
GITEE_API_LATEST = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/releases/latest"

# 超时设置（秒）
REQUEST_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 300

# 配置文件名称
CONFIG_FILE = 'config.txt'
# GitHub token 配置文件（独立文件，不会被主程序重置）
GITHUB_TOKEN_FILE = 'github_token.txt'


def get_config_path():
    """
    获取配置文件路径
    支持打包后的可执行文件和开发环境
    """
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件，配置文件保存在可执行文件目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境，配置文件保存在脚本目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, CONFIG_FILE)


def get_github_token_file_path():
    """
    获取 GitHub token 配置文件路径
    支持打包后的可执行文件和开发环境
    """
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件，配置文件保存在可执行文件目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境，配置文件保存在脚本目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, GITHUB_TOKEN_FILE)


def get_github_token():
    """
    从独立的 GitHub token 配置文件读取 API token
    返回: token字符串或None（如果未配置）
    """
    token_file_path = get_github_token_file_path()
    if not os.path.exists(token_file_path):
        return None
    
    try:
        with open(token_file_path, 'r', encoding='utf-8') as f:
            # 读取第一行非空、非注释的内容作为 token
            for line in f:
                line = line.strip()
                # 跳过空行和注释行（以#开头的行）
                if not line or line.startswith('#'):
                    continue
                # 如果行中包含 = 或 :，尝试解析
                if '=' in line:
                    _, value = line.split('=', 1)
                    value = value.strip()
                elif ':' in line:
                    _, value = line.split(':', 1)
                    value = value.strip()
                else:
                    # 如果整行就是 token（没有 key=value 格式）
                    value = line
                
                if value:
                    return value
    except Exception:
        # 如果读取失败，静默返回None（不影响程序运行）
        pass
    
    return None


def get_file_version(file_path):
    """
    从文件版本信息中获取版本号
    返回: 版本号字符串，如 "2.4.0"，如果获取失败返回 None
    """
    try:
        if platform.system() == 'Windows' and os.path.exists(file_path):
            try:
                import win32api
                info = win32api.GetFileVersionInfo(file_path, '\\')
                version = info['FileVersionMS'] >> 16, info['FileVersionMS'] & 0xFFFF, \
                         info['FileVersionLS'] >> 16, info['FileVersionLS'] & 0xFFFF
                return f"{version[0]}.{version[1]}.{version[2]}"
            except ImportError:
                # win32api不可用，尝试使用其他方法
                try:
                    # 使用ctypes作为备选方案
                    import ctypes
                    from ctypes import wintypes
                    
                    # 获取文件版本信息大小
                    size = ctypes.windll.version.GetFileVersionInfoSizeW(file_path, None)
                    if size == 0:
                        return None
                    
                    # 分配缓冲区
                    buffer = ctypes.create_string_buffer(size)
                    if ctypes.windll.version.GetFileVersionInfoW(file_path, None, size, buffer) == 0:
                        return None
                    
                    # 解析版本信息
                    # 这里简化处理，直接读取VS_FIXEDFILEINFO
                    class VS_FIXEDFILEINFO(ctypes.Structure):
                        _fields_ = [
                            ("dwSignature", wintypes.DWORD),
                            ("dwStrucVersion", wintypes.DWORD),
                            ("dwFileVersionMS", wintypes.DWORD),
                            ("dwFileVersionLS", wintypes.DWORD),
                            ("dwProductVersionMS", wintypes.DWORD),
                            ("dwProductVersionLS", wintypes.DWORD),
                            ("dwFileFlagsMask", wintypes.DWORD),
                            ("dwFileFlags", wintypes.DWORD),
                            ("dwFileOS", wintypes.DWORD),
                            ("dwFileType", wintypes.DWORD),
                            ("dwFileSubtype", wintypes.DWORD),
                            ("dwFileDateMS", wintypes.DWORD),
                            ("dwFileDateLS", wintypes.DWORD),
                        ]
                    
                    # 查找VS_FIXEDFILEINFO
                    u = ctypes.c_void_p()
                    l = ctypes.c_uint()
                    if ctypes.windll.version.VerQueryValueW(buffer, "\\", ctypes.byref(u), ctypes.byref(l)) == 0:
                        return None
                    
                    fixed_info = ctypes.cast(u, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
                    version_ms = fixed_info.dwFileVersionMS
                    version_ls = fixed_info.dwFileVersionLS
                    
                    version = (version_ms >> 16, version_ms & 0xFFFF, version_ls >> 16)
                    return f"{version[0]}.{version[1]}.{version[2]}"
                except:
                    return None
            except Exception as e:
                # 打印错误信息以便调试
                print(f"获取文件版本信息失败: {e}")
                return None
    except Exception as e:
        print(f"get_file_version异常: {e}")
    return None


def get_current_version():
    """
    获取当前程序版本号
    返回格式: "2.4.0" 或 None（如果无法获取）
    优先从文件版本信息中获取，不从文件名推断
    """
    try:
        # 方法1: 从exe文件的版本信息读取（最准确，优先使用）
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            if os.path.exists(exe_path):
                version = get_file_version(exe_path)
                if version:
                    return version
        
        # 方法2: 从version_info.txt读取（开发环境或打包后找不到版本信息时）
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_path = sys._MEIPASS
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, 'version_info.txt')
        if not os.path.exists(version_file):
            # 尝试在程序目录查找
            if getattr(sys, 'frozen', False):
                exe_dir = os.path.dirname(sys.executable)
                version_file = os.path.join(exe_dir, 'version_info.txt')
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取版本号: filevers=(2, 3, 0, 0) 或 prodvers=(2, 3, 0, 0)
                match = re.search(r'(?:filevers|prodvers)=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
                if match:
                    return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        
        # 方法3: 从Git标签读取（开发环境备用方法）
        if not getattr(sys, 'frozen', False):
            try:
                import subprocess
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # 尝试获取最新的Git标签
                result = subprocess.run(
                    ['git', 'describe', '--tags', '--abbrev=0'],
                    cwd=script_dir,
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    tag = result.stdout.strip()
                    # 移除'v'前缀，如 "v2.3.0" -> "2.3.0"
                    version = tag.lstrip('vV')
                    # 验证版本号格式
                    if re.match(r'^\d+\.\d+\.\d+', version):
                        return version
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, Exception):
                # Git不可用或出错，忽略
                pass
        
    except Exception as e:
        print(f"获取版本号失败: {e}")
    
    return None


def compare_versions(current_version, latest_version):
    """
    比较两个版本号
    返回: -1 (current < latest), 0 (current == latest), 1 (current > latest)
    """
    try:
        def version_tuple(version_str):
            # 移除可能的'v'前缀，如 "v2.3.0" -> "2.3.0"
            version_str = version_str.lstrip('vV')
            parts = version_str.split('.')
            # 确保至少有3部分，不足的补0
            while len(parts) < 3:
                parts.append('0')
            return tuple(int(x) for x in parts[:3])
        
        current = version_tuple(current_version)
        latest = version_tuple(latest_version)
        
        if current < latest:
            return -1
        elif current > latest:
            return 1
        else:
            return 0
    except Exception as e:
        print(f"版本比较失败: {e}")
        return 0


def check_github_update():
    """
    从GitHub检查更新
    返回: (success, version, download_url, release_notes, tag_name, filename)
    """
    try:
        req = urllib.request.Request(GITHUB_API_LATEST)
        # 使用更常见的浏览器 User-Agent，避免被拒绝
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        # 如果配置了 GitHub token，添加认证头以提升 rate limit
        github_token = get_github_token()
        if github_token:
            # 使用 Bearer 格式（GitHub API 推荐的标准格式）
            req.add_header('Authorization', f'Bearer {github_token}')
        
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            response_data = response.read().decode('utf-8')
            data = json.loads(response_data)
            
            # 检查是否有错误信息
            if 'message' in data and 'tag_name' not in data:
                error_msg = data.get('message', 'Unknown error')
                print(f"GitHub API错误: {error_msg}")
                # 检查是否是认证问题
                if 'Bad credentials' in error_msg or 'Invalid token' in error_msg:
                    print("提示: GitHub token 可能无效或已过期，请检查 github_token.txt 中的 token")
                return False, None, None, None, None, None
            
            # 提取版本号（tag_name可能包含'v'前缀）
            version = data.get('tag_name', '').lstrip('vV')
            # 获取原始tag_name
            tag_name = data.get('tag_name', '')
            if not version:
                print("GitHub API响应中未找到tag_name")
                return False, None, None, None, None, None
            
            # 查找Windows exe文件
            download_url = None
            exe_filename = None
            assets = data.get('assets', [])
            for asset in assets:
                name = asset.get('name', '').lower()
                if name.endswith('.exe') and 'windows' in name.lower():
                    download_url = asset.get('browser_download_url')
                    exe_filename = asset.get('name', '')  # 保存原始文件名（包含中文）
                    if download_url:
                        break
            
            # 如果没找到特定Windows版本，查找任何exe文件
            if not download_url:
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if name.endswith('.exe'):
                        download_url = asset.get('browser_download_url')
                        exe_filename = asset.get('name', '')  # 保存原始文件名
                        if download_url:
                            break
            
            # 获取发布说明
            release_notes = data.get('body', '')
            
            # 返回：success, version, download_url, release_notes, tag_name, filename
            return True, version, download_url, release_notes, tag_name, exe_filename
            
    except urllib.error.HTTPError as e:
        error_msg = f"GitHub API HTTP错误 {e.code}: {e.reason}"
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            if 'message' in error_data:
                error_msg += f" - {error_data['message']}"
                # 检查是否是认证问题
                if e.code == 401:
                    print("提示: GitHub token 认证失败，请检查 github_token.txt 中的 token 是否正确")
                elif e.code == 403:
                    if 'rate limit' in error_data.get('message', '').lower():
                        print("提示: 即使使用了 token，仍然遇到 rate limit，可能是 token 权限不足或 IP 被限制")
                    else:
                        print(f"提示: GitHub API 访问被拒绝 (403)，错误详情: {error_data.get('message', 'Unknown')}")
        except:
            pass
        print(error_msg)
        return False, None, None, None, None, None
    except urllib.error.URLError as e:
        print(f"GitHub API网络连接失败: {e.reason if hasattr(e, 'reason') else str(e)}")
        return False, None, None, None, None, None
    except json.JSONDecodeError as e:
        print(f"GitHub API响应解析失败: {e}")
        return False, None, None, None, None, None
    except Exception as e:
        print(f"检查GitHub更新时出错: {type(e).__name__}: {str(e)}")
        return False, None, None, None, None, None


def check_gitee_update():
    """
    从Gitee检查更新
    返回: (success, version, download_url, release_notes) 或 (False, None, None, None)
    """
    try:
        # Gitee API v5 获取最新release的端点
        # 先尝试 /latest 端点，如果失败则使用列表端点取第一个
        api_url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/releases/latest"
        
        req = urllib.request.Request(api_url)
        # 使用更常见的浏览器 User-Agent，避免被拒绝
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Accept', 'application/json')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        req.add_header('Referer', 'https://gitee.com/')
        
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
        except urllib.error.HTTPError as e:
            # 如果 /latest 端点不存在（404）或被拒绝（403），尝试使用列表端点
            if e.code in [404, 403]:
                api_url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/releases"
                req = urllib.request.Request(api_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                req.add_header('Accept', 'application/json')
                req.add_header('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
                req.add_header('Referer', 'https://gitee.com/')
                try:
                    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                        response_data = response.read().decode('utf-8')
                        releases = json.loads(response_data)
                        if isinstance(releases, list) and len(releases) > 0:
                            data = releases[0]  # 取第一个（最新的）
                        else:
                            print("Gitee API返回空列表")
                            return False, None, None, None
                except urllib.error.HTTPError as e2:
                    # 如果列表端点也返回HTTP错误，抛出原始错误（让外层处理）
                    raise e
                except urllib.error.URLError as e2:
                    # 如果列表端点网络连接失败，直接返回失败（不抛出，避免混淆错误信息）
                    print(f"Gitee API列表端点网络连接失败: {e2.reason if hasattr(e2, 'reason') else str(e2)}")
                    return False, None, None, None
            else:
                raise  # 重新抛出其他HTTP错误
        
        # Gitee API可能返回列表或单个对象
        if isinstance(data, list):
            if len(data) == 0:
                print("Gitee API返回空列表")
                return False, None, None, None
            data = data[0]
        
        # 检查是否有错误信息
        if 'message' in data and 'tag_name' not in data:
            print(f"Gitee API错误: {data.get('message', 'Unknown error')}")
            return False, None, None, None
        
        # 提取版本号（tag_name可能包含'v'前缀）
        version = data.get('tag_name', '').lstrip('vV')
        if not version:
            print("Gitee API响应中未找到tag_name")
            return False, None, None, None
        
        # 查找Windows exe文件
        download_url = None
        # Gitee API中assets字段可能不同，尝试多种可能的字段名
        assets = data.get('assets', [])
        if not assets:
            # 尝试其他可能的字段名
            assets = data.get('release_assets', [])
        
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe') and 'windows' in name.lower():
                # Gitee可能使用不同的字段名
                download_url = asset.get('browser_download_url') or asset.get('download_url') or asset.get('url')
                if download_url:
                    break
        
        # 如果没找到特定Windows版本，查找任何exe文件
        if not download_url:
            for asset in assets:
                name = asset.get('name', '').lower()
                if name.endswith('.exe'):
                    download_url = asset.get('browser_download_url') or asset.get('download_url') or asset.get('url')
                    if download_url:
                        break
        
        # 获取发布说明
        release_notes = data.get('body', '') or data.get('description', '')
        
        return True, version, download_url, release_notes
            
    except urllib.error.HTTPError as e:
        error_msg = f"Gitee API HTTP错误 {e.code}: {e.reason}"
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            if 'message' in error_data:
                error_msg += f" - {error_data['message']}"
                # 检查是否是频率限制错误
                if 'rate limit' in error_data.get('message', '').lower() or e.code == 403:
                    error_msg = "Gitee API访问频率限制：请求过于频繁，请稍后再试。"
        except:
            pass
        print(error_msg)
        return False, None, None, None
    except urllib.error.URLError as e:
        print(f"Gitee API网络连接失败: {e.reason if hasattr(e, 'reason') else str(e)}")
        return False, None, None, None
    except json.JSONDecodeError as e:
        print(f"Gitee API响应解析失败: {e}")
        return False, None, None, None
    except Exception as e:
        print(f"检查Gitee更新时出错: {type(e).__name__}: {str(e)}")
        return False, None, None, None


def download_file(url, save_path, progress_callback=None):
    """
    下载文件
    progress_callback: 可选的回调函数，参数为 (downloaded_bytes, total_bytes)
    返回: (success, error_message)
    """
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Intersection-Traffic-Flow-Updater/1.0')
        
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
            
            return True, None
            
    except urllib.error.URLError as e:
        return False, f"下载失败: {str(e)}"
    except Exception as e:
        return False, f"下载时出错: {str(e)}"


def get_program_dir():
    """
    获取程序目录路径
    支持打包后的可执行文件和开发环境
    """
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))


def prepare_update_for_restart(downloaded_file_path, current_exe_path, version, language='zh_CN'):
    """
    准备更新：将下载的文件移动到程序目录，创建标记文件
    参数:
        downloaded_file_path: 下载的文件路径
        current_exe_path: 当前可执行文件路径
        version: 新版本号
        language: 当前语言设置 ('zh_CN' 或 'en_US')
    返回: (success, error_message)
    """
    try:
        if not os.path.exists(downloaded_file_path):
            return False, "下载的文件不存在"
        
        if not os.path.exists(current_exe_path):
            return False, "当前程序文件不存在"
        
        # 如果版本号未提供或为unknown，从下载文件的版本信息中获取
        if not version or version == "unknown":
            version = get_file_version(downloaded_file_path)
            if not version:
                # 如果无法从版本信息获取，尝试从文件名推断（最后手段）
                import re
                downloaded_file_name = os.path.basename(downloaded_file_path)
                version_match = re.search(r'(\d+\.\d+\.\d+)', downloaded_file_name)
                if version_match:
                    version = version_match.group(1)
                else:
                    version = "unknown"
        
        program_dir = get_program_dir()
        update_temp_dir = os.path.join(program_dir, 'update_temp')
        
        # 如果临时目录已存在，先清空它
        if os.path.exists(update_temp_dir):
            try:
                # 删除临时目录中的所有文件和子目录
                for item in os.listdir(update_temp_dir):
                    item_path = os.path.join(update_temp_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            except Exception as e:
                # 如果清空失败，尝试删除整个目录后重新创建
                try:
                    shutil.rmtree(update_temp_dir)
                    os.makedirs(update_temp_dir)
                except:
                    return False, f"无法清空临时目录: {str(e)}"
        else:
            # 创建临时目录
            os.makedirs(update_temp_dir)
        
        # 根据语言和版本号生成标准文件名（完全按照标准名命名，不替换版本号）
        if version and version != "unknown":
            if language == 'zh_CN':
                # 中文标准名称
                new_file_name = f"交叉口交通流量流向可视化工具{version}.exe"
            else:
                # 英文标准名称
                new_file_name = f"IntersectionTrafficFlowVisualize{version}.exe"
        else:
            # 版本号未知，使用下载文件的原始文件名
            downloaded_file_name = os.path.basename(downloaded_file_path)
            new_file_name = downloaded_file_name
        
        new_file_path = os.path.join(update_temp_dir, new_file_name)
        
        # 如果目标文件已存在，先删除
        if os.path.exists(new_file_path):
            try:
                os.remove(new_file_path)
            except:
                pass
        
        # 复制文件
        shutil.copy2(downloaded_file_path, new_file_path)
        
        # 创建标记文件（包含语言信息）
        marker_file = os.path.join(program_dir, 'update_pending.txt')
        with open(marker_file, 'w', encoding='utf-8') as f:
            f.write(f"new_file_path={new_file_path}\n")
            f.write(f"current_exe_path={current_exe_path}\n")
            f.write(f"version={version}\n")
            f.write(f"language={language}\n")
        
        return True, None
        
    except Exception as e:
        return False, f"准备更新失败: {str(e)}"


def check_pending_update():
    """
    检查是否有待安装的更新
    返回: (has_pending, new_file_path, current_exe_path, version, language) 或 (False, None, None, None, None)
    """
    try:
        program_dir = get_program_dir()
        marker_file = os.path.join(program_dir, 'update_pending.txt')
        
        if not os.path.exists(marker_file):
            return False, None, None, None, None
        
        # 读取标记文件
        new_file_path = None
        current_exe_path = None
        version = None
        language = 'zh_CN'  # 默认值
        
        with open(marker_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('new_file_path='):
                    new_file_path = line.split('=', 1)[1]
                elif line.startswith('current_exe_path='):
                    current_exe_path = line.split('=', 1)[1]
                elif line.startswith('version='):
                    version = line.split('=', 1)[1]
                elif line.startswith('language='):
                    language = line.split('=', 1)[1]
        
        # 检查新文件是否存在
        if new_file_path and os.path.exists(new_file_path):
            return True, new_file_path, current_exe_path, version, language
        else:
            # 文件不存在，删除标记文件
            try:
                os.remove(marker_file)
            except:
                pass
            return False, None, None, None, None
            
    except Exception as e:
        return False, None, None, None


def execute_pending_update():
    """
    执行待安装的更新：替换文件并启动新版本
    返回: (success, error_message)
    """
    try:
        has_pending, new_file_path, current_exe_path, version, language = check_pending_update()
        
        if not has_pending:
            return False, "没有待安装的更新"
        
        if not os.path.exists(new_file_path):
            return False, "更新文件不存在"
        
        if not os.path.exists(current_exe_path):
            return False, "当前程序文件不存在"
        
        # 确定新版本的目标文件名（完全按照标准名命名，基于语言和版本号）
        current_dir = os.path.dirname(current_exe_path)
        
        # 根据语言和版本号生成标准文件名
        if version and version != "unknown":
            if language == 'zh_CN':
                # 中文标准名称
                new_file_name = f"交叉口交通流量流向可视化工具{version}.exe"
            else:
                # 英文标准名称
                new_file_name = f"IntersectionTrafficFlowVisualize{version}.exe"
        else:
            # 版本号未知，使用新文件的文件名
            new_file_name = os.path.basename(new_file_path)
        
        # 新版本的目标完整路径
        new_exe_path = os.path.join(current_dir, new_file_name)
        
        # 创建备份
        backup_path = current_exe_path + ".backup"
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(current_exe_path, backup_path)
        except Exception:
            pass  # 备份失败不影响更新
        
        # 替换文件（如果新文件名与旧文件名不同，先删除旧文件）
        try:
            if new_exe_path != current_exe_path and os.path.exists(current_exe_path):
                os.remove(current_exe_path)
            if os.path.exists(new_exe_path):
                os.remove(new_exe_path)
            shutil.copy2(new_file_path, new_exe_path)
        except Exception as e:
            return False, f"替换文件失败: {str(e)}"
        
        # 启动新版本
        try:
            subprocess.Popen([current_exe_path], shell=False)
        except Exception as e:
            return False, f"启动新版本失败: {str(e)}"
        
        # 清理临时文件和标记文件
        try:
            program_dir = get_program_dir()
            marker_file = os.path.join(program_dir, 'update_pending.txt')
            if os.path.exists(marker_file):
                os.remove(marker_file)
            
            update_temp_dir = os.path.join(program_dir, 'update_temp')
            if os.path.exists(update_temp_dir):
                shutil.rmtree(update_temp_dir)
        except:
            pass  # 清理失败不影响更新
        
        return True, None
        
    except Exception as e:
        return False, f"执行更新失败: {str(e)}"


def restart_with_update():
    """
    重启程序并安装更新：创建批处理脚本，在程序退出后替换文件并启动新版本
    """
    try:
        has_pending, new_file_path, current_exe_path, version, language = check_pending_update()
        
        if not has_pending:
            return False, "没有待安装的更新"
        
        if not os.path.exists(new_file_path):
            return False, "更新文件不存在"
        
        if not os.path.exists(current_exe_path):
            return False, "当前程序文件不存在"
        
        program_dir = get_program_dir()
        bat_file = os.path.join(program_dir, 'update_install.bat')
        
        # 确定新版本的目标文件名（完全按照标准名命名，基于语言和版本号）
        current_dir = os.path.dirname(current_exe_path)
        
        # 根据语言和版本号生成标准文件名
        if version and version != "unknown":
            if language == 'zh_CN':
                # 中文标准名称
                new_file_name = f"交叉口交通流量流向可视化工具{version}.exe"
            else:
                # 英文标准名称
                new_file_name = f"IntersectionTrafficFlowVisualize{version}.exe"
        else:
            # 版本号未知，使用新文件的文件名
            new_file_name = os.path.basename(new_file_path)
        
        # 新版本的目标完整路径
        new_exe_path = os.path.join(current_dir, new_file_name)
        
        # 获取进程名（从exe路径提取文件名，不含扩展名）
        # 使用短路径名获取文件名，避免中文乱码
        try:
            import win32api
            current_exe_short_full = win32api.GetShortPathName(current_exe_path)
            exe_name = os.path.basename(current_exe_short_full)
        except:
            # 如果无法获取短路径名，使用原文件名
            exe_name = os.path.basename(current_exe_path)
        process_name = os.path.splitext(exe_name)[0]
        
        # 获取短路径名（8.3格式）以避免中文路径编码问题
        # 必须使用短路径名，否则批处理脚本中的中文路径会乱码
        def get_short_path(long_path):
            """获取Windows短路径名（8.3格式）"""
            try:
                import win32api
                short_path = win32api.GetShortPathName(long_path)
                # 确保返回的路径使用反斜杠
                return short_path.replace('/', '\\')
            except ImportError:
                # win32api不可用，尝试使用ctypes
                try:
                    import ctypes
                    from ctypes import wintypes
                    kernel32 = ctypes.windll.kernel32
                    buffer = ctypes.create_unicode_buffer(260)  # MAX_PATH
                    if kernel32.GetShortPathNameW(long_path, buffer, 260):
                        return buffer.value.replace('/', '\\')
                    else:
                        raise Exception("GetShortPathName failed")
                except:
                    # 如果都失败，返回错误
                    raise Exception(f"无法获取短路径名，需要win32api或ctypes支持: {long_path}")
            except Exception as e:
                raise Exception(f"获取短路径名失败: {e}")
        
        # 获取短路径名（必须成功，否则无法处理中文路径）
        # 注意：备份文件和新文件路径可能还不存在，需要先获取目录的短路径名，然后拼接文件名
        try:
            current_exe_short = get_short_path(current_exe_path)
            new_file_short = get_short_path(new_file_path)
            marker_short = get_short_path(os.path.join(program_dir, 'update_pending.txt'))
            temp_dir_short = get_short_path(os.path.join(program_dir, 'update_temp'))
            
            # 备份文件路径可能还不存在，需要获取目录的短路径名，然后拼接文件名
            backup_path = current_exe_path + ".backup"
            backup_dir = os.path.dirname(backup_path)
            backup_dir_short = get_short_path(backup_dir) if os.path.exists(backup_dir) else backup_dir.replace('/', '\\')
            backup_name = os.path.basename(backup_path)
            backup_short = os.path.join(backup_dir_short, backup_name)
            
            # 新文件路径可能还不存在，需要获取目录的短路径名，然后拼接文件名
            new_exe_dir = os.path.dirname(new_exe_path)
            new_exe_dir_short = get_short_path(new_exe_dir) if os.path.exists(new_exe_dir) else new_exe_dir.replace('/', '\\')
            new_exe_name = os.path.basename(new_exe_path)
            new_exe_short = os.path.join(new_exe_dir_short, new_exe_name)
        except Exception as e:
            # 如果获取短路径失败，返回错误
            return False, f"无法获取短路径名: {str(e)}。请确保已安装pywin32或系统支持短路径名。"
        
        # 转义批处理脚本中的特殊字符
        # 短路径名通常不包含特殊字符，但为了安全还是转义
        def escape_bat_path(path):
            """转义批处理脚本中的路径，处理特殊字符"""
            # 短路径名通常不包含空格和特殊字符，但为了安全还是用引号包裹
            escaped = path.replace('"', '""').replace('&', '^&').replace('|', '^|')
            return f'"{escaped}"'
        
        # 转义所有路径（短路径名）
        current_exe_escaped = escape_bat_path(current_exe_short)
        new_file_escaped = escape_bat_path(new_file_short)
        new_exe_escaped = escape_bat_path(new_exe_short)  # 新版本的目标路径
        backup_escaped = escape_bat_path(backup_short)
        marker_escaped = escape_bat_path(marker_short)
        temp_dir_escaped = escape_bat_path(temp_dir_short)
        
        # 创建批处理脚本（使用短路径名避免中文乱码）
        # 注意：批处理脚本中不使用chcp 65001，使用默认编码（GBK）
        # 所有路径都使用短路径名（8.3格式），避免中文乱码
        bat_content = f"""@echo off
echo Waiting for program to exit...
set max_wait=60
set waited=0
:wait_loop
tasklist /FI "IMAGENAME eq {exe_name}" 2>NUL | find /I /N "{exe_name}">NUL
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >nul
    set /a waited+=1
    if %waited% geq %max_wait% (
        echo Timeout, continuing installation...
        goto install
    )
    goto wait_loop
)
echo Program has exited, waiting 2 seconds...
timeout /t 2 /nobreak >nul
:install
echo Installing update...
if exist {backup_escaped} del /F /Q {backup_escaped}
copy /Y {current_exe_escaped} {backup_escaped} >nul 2>&1
if errorlevel 1 (
    echo Backup failed, aborting
    goto end
)
del /F /Q {current_exe_escaped} >nul 2>&1
if errorlevel 1 (
    echo Delete old file failed, aborting
    goto end
)
copy /Y {new_file_escaped} {new_exe_escaped} >nul 2>&1
if errorlevel 1 (
    echo Copy new file failed, aborting
    goto end
)
echo Starting new version...
start "" {new_exe_escaped}
timeout /t 3 /nobreak >nul
echo Cleaning temporary files...
if exist {marker_escaped} del /F /Q {marker_escaped}
if exist {temp_dir_escaped} rmdir /S /Q {temp_dir_escaped}
:end
timeout /t 1 /nobreak >nul
if exist "%~f0" (
    call :delete_self
    exit /b
)
exit /b
:delete_self
timeout /t 1 /nobreak >nul
del /F /Q "%~f0" >nul 2>&1
exit /b
"""
        
        # 写入批处理文件（使用GBK编码，Windows批处理脚本标准编码）
        # 注意：不使用UTF-8 BOM，因为可能导致批处理脚本执行错误
        try:
            with open(bat_file, 'w', encoding='gbk', errors='replace') as f:
                f.write(bat_content)
        except Exception as e:
            # 如果GBK失败，尝试使用系统默认编码
            try:
                import locale
                default_encoding = locale.getpreferredencoding()
                with open(bat_file, 'w', encoding=default_encoding, errors='replace') as f:
                    f.write(bat_content)
            except:
                # 最后尝试使用UTF-8（不带BOM）
                with open(bat_file, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(bat_content)
        
        # 启动批处理脚本（隐藏窗口，使用cmd.exe来执行，确保批处理脚本正确运行）
        # 批处理文件已创建，现在可以获取短路径名（如果路径包含中文）
        try:
            # 尝试获取批处理文件的短路径名（文件已创建）
            bat_file_short = get_short_path(bat_file)
        except:
            # 如果获取失败，使用原路径（批处理文件名通常不包含中文）
            bat_file_short = bat_file.replace('/', '\\')
        
        try:
            # 使用cmd.exe来执行批处理脚本，使用短路径名避免中文路径问题
            subprocess.Popen(
                ['cmd.exe', '/c', 'start', '/min', '', bat_file_short],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            # 如果 CREATE_NO_WINDOW 不支持，使用普通方式
            try:
                subprocess.Popen(['cmd.exe', '/c', bat_file_short], shell=False)
            except:
                # 最后尝试直接执行（使用原路径）
                subprocess.Popen([bat_file], shell=False)
        
        return True, None
        
    except Exception as e:
        return False, f"创建重启脚本失败: {str(e)}"


def install_update(downloaded_file_path, current_exe_path):
    """
    安装更新：准备更新文件，等待重启后安装
    返回: (success, error_message)
    """
    # 使用新的重启方案
    # 这里需要版本号，但函数签名中没有，所以先尝试从文件名提取
    # 或者返回一个特殊值，让调用者知道需要使用 prepare_update_for_restart
    try:
        # 尝试从文件名提取版本号（如果文件名包含版本信息）
        version = "unknown"
        filename = os.path.basename(downloaded_file_path)
        # 简单的版本提取逻辑，可以根据实际情况调整
        version_match = re.search(r'(\d+\.\d+\.\d+)', filename)
        if version_match:
            version = version_match.group(1)
        
        return prepare_update_for_restart(downloaded_file_path, current_exe_path, version)
    except Exception as e:
        return False, f"准备更新失败: {str(e)}"


def check_update(source='github', callback=None):
    """
    检查更新（统一接口）
    source: 'github' 或 'gitee'
    callback: 可选的回调函数，参数为 (success, version, download_url, release_notes, error, tag_name, filename)
    返回: (success, version, download_url, release_notes, error_message, tag_name, filename)
    """
    error_msg = None
    tag_name = None
    filename = None
    # 规范化source参数
    if source:
        source_lower = str(source).lower().strip()
    else:
        source_lower = 'github'
    
    try:
        if source_lower == 'github':
            result = check_github_update()
            # check_github_update现在返回6个值：success, version, download_url, release_notes, tag_name, filename
            if len(result) == 6:
                success, version, download_url, release_notes, tag_name, filename = result
            else:
                # 向后兼容：如果返回4个值，则tag_name和filename为None
                success, version, download_url, release_notes = result[:4]
                tag_name = None
                filename = None
            if not success:
                error_msg = f"无法连接到GitHub或解析响应失败。\n建议：请尝试使用Gitee更新源，或检查网络连接后重试。"
        elif source_lower == 'gitee':
            success, version, download_url, release_notes = check_gitee_update()
            if not success:
                # 检查是否是频率限制错误（从check_gitee_update的返回值无法直接判断，但可以通过错误信息推断）
                # 这里使用通用错误信息，具体的频率限制错误已在check_gitee_update中处理
                error_msg = f"无法连接到Gitee或解析响应失败。可能是网络问题或API访问频率限制，请稍后重试。"
        else:
            error_msg = f"不支持的更新源: {source}"
            if callback:
                callback(False, None, None, None, error_msg, None, None)
            return False, None, None, None, error_msg, None, None
        
        if not success:
            if callback:
                callback(False, None, None, None, error_msg, None, None)
            return False, None, None, None, error_msg, None, None
        
        if not download_url:
            error_msg = "未找到可用的下载链接。该版本可能尚未发布Windows版本。"
            if callback:
                callback(False, version, None, None, error_msg, None, None)
            return False, version, None, None, error_msg, None, None
        
        if callback:
            callback(True, version, download_url, release_notes, None, tag_name, filename)
        
        return True, version, download_url, release_notes, None, tag_name, filename
        
    except Exception as e:
        error_msg = f"检查更新时发生未知错误: {str(e)}"
        if callback:
            callback(False, None, None, None, error_msg, None, None)
        return False, None, None, None, error_msg, None, None

