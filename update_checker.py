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


def get_current_version():
    """
    获取当前程序版本号
    返回格式: "2.2.0" 或 None（如果无法获取）
    """
    try:
        # 方法1: 从exe文件属性读取（Windows）
        if platform.system() == 'Windows' and getattr(sys, 'frozen', False):
            try:
                import win32api
                import win32file
                exe_path = sys.executable
                if os.path.exists(exe_path):
                    # 获取文件版本信息
                    info = win32api.GetFileVersionInfo(exe_path, '\\')
                    version = info['FileVersionMS'] >> 16, info['FileVersionMS'] & 0xFFFF, \
                             info['FileVersionLS'] >> 16, info['FileVersionLS'] & 0xFFFF
                    return f"{version[0]}.{version[1]}.{version[2]}"
            except ImportError:
                # win32api不可用，尝试其他方法
                pass
            except Exception:
                pass
        
        # 方法2: 从version_info.txt读取
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
                # 提取版本号: filevers=(2, 2, 0, 0) 或 prodvers=(2, 2, 0, 0)
                match = re.search(r'(?:filevers|prodvers)=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', content)
                if match:
                    return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
        
        # 方法3: 从文件名推断（最后手段）
        if getattr(sys, 'frozen', False):
            exe_name = os.path.basename(sys.executable)
            # 匹配 "交叉口交通流量流向可视化工具2.2.exe" 中的 "2.2"
            match = re.search(r'(\d+)\.(\d+)', exe_name)
            if match:
                return f"{match.group(1)}.{match.group(2)}.0"
        
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
    返回: (success, version, download_url, release_notes) 或 (False, None, None, None)
    """
    try:
        req = urllib.request.Request(GITHUB_API_LATEST)
        # 使用更常见的浏览器 User-Agent，避免被拒绝
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # 检查是否有错误信息
            if 'message' in data and 'tag_name' not in data:
                print(f"GitHub API错误: {data.get('message', 'Unknown error')}")
                return False, None, None, None
            
            # 提取版本号（tag_name可能包含'v'前缀）
            version = data.get('tag_name', '').lstrip('vV')
            if not version:
                print("GitHub API响应中未找到tag_name")
                return False, None, None, None
            
            # 查找Windows exe文件
            download_url = None
            assets = data.get('assets', [])
            for asset in assets:
                name = asset.get('name', '').lower()
                if name.endswith('.exe') and 'windows' in name.lower():
                    download_url = asset.get('browser_download_url')
                    if download_url:
                        break
            
            # 如果没找到特定Windows版本，查找任何exe文件
            if not download_url:
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if name.endswith('.exe'):
                        download_url = asset.get('browser_download_url')
                        if download_url:
                            break
            
            # 获取发布说明
            release_notes = data.get('body', '')
            
            return True, version, download_url, release_notes
            
    except urllib.error.HTTPError as e:
        error_msg = f"GitHub API HTTP错误 {e.code}: {e.reason}"
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            if 'message' in error_data:
                error_msg += f" - {error_data['message']}"
        except:
            pass
        print(error_msg)
        return False, None, None, None
    except urllib.error.URLError as e:
        print(f"GitHub API网络连接失败: {e.reason if hasattr(e, 'reason') else str(e)}")
        return False, None, None, None
    except json.JSONDecodeError as e:
        print(f"GitHub API响应解析失败: {e}")
        return False, None, None, None
    except Exception as e:
        print(f"检查GitHub更新时出错: {type(e).__name__}: {str(e)}")
        return False, None, None, None


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


def install_update(downloaded_file_path, current_exe_path):
    """
    安装更新：替换旧版本并启动新版本
    返回: (success, error_message)
    """
    try:
        if not os.path.exists(downloaded_file_path):
            return False, "下载的文件不存在"
        
        if not os.path.exists(current_exe_path):
            return False, "当前程序文件不存在"
        
        # 创建备份（可选）
        backup_path = current_exe_path + ".backup"
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(current_exe_path, backup_path)
        except Exception:
            pass  # 备份失败不影响更新
        
        # 在Windows上，可能需要先关闭程序才能替换文件
        # 这里我们尝试直接替换，如果失败则提示用户手动操作
        try:
            # 尝试删除旧文件
            if os.path.exists(current_exe_path):
                os.remove(current_exe_path)
            
            # 复制新文件
            shutil.copy2(downloaded_file_path, current_exe_path)
            
            # 启动新版本
            try:
                subprocess.Popen([current_exe_path], shell=False)
            except Exception:
                pass  # 启动失败不影响文件替换
            
            return True, None
            
        except PermissionError:
            # 文件被占用，需要用户手动操作
            return False, "无法替换文件，程序可能正在运行。请关闭程序后手动替换文件。"
        except Exception as e:
            return False, f"安装更新时出错: {str(e)}"
            
    except Exception as e:
        return False, f"安装更新失败: {str(e)}"


def check_update(source='github', callback=None):
    """
    检查更新（统一接口）
    source: 'github' 或 'gitee'
    callback: 可选的回调函数，参数为 (success, version, download_url, release_notes, error)
    返回: (success, version, download_url, release_notes, error_message)
    """
    error_msg = None
    # 规范化source参数
    if source:
        source_lower = str(source).lower().strip()
    else:
        source_lower = 'github'
    
    try:
        if source_lower == 'github':
            success, version, download_url, release_notes = check_github_update()
            if not success:
                error_msg = f"无法连接到GitHub或解析响应失败。请检查网络连接或稍后重试。"
        elif source_lower == 'gitee':
            success, version, download_url, release_notes = check_gitee_update()
            if not success:
                # 检查是否是频率限制错误（从check_gitee_update的返回值无法直接判断，但可以通过错误信息推断）
                # 这里使用通用错误信息，具体的频率限制错误已在check_gitee_update中处理
                error_msg = f"无法连接到Gitee或解析响应失败。可能是网络问题或API访问频率限制，请稍后重试。"
        else:
            error_msg = f"不支持的更新源: {source}"
            if callback:
                callback(False, None, None, None, error_msg)
            return False, None, None, None, error_msg
        
        if not success:
            if callback:
                callback(False, None, None, None, error_msg)
            return False, None, None, None, error_msg
        
        if not download_url:
            error_msg = "未找到可用的下载链接。该版本可能尚未发布Windows版本。"
            if callback:
                callback(False, version, None, None, error_msg)
            return False, version, None, None, error_msg
        
        if callback:
            callback(True, version, download_url, release_notes, None)
        
        return True, version, download_url, release_notes, None
        
    except Exception as e:
        error_msg = f"检查更新时发生未知错误: {str(e)}"
        if callback:
            callback(False, None, None, None, error_msg)
        return False, None, None, None, error_msg

