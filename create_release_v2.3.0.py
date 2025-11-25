# -*- coding: utf-8 -*-
"""
创建GitHub和Gitee上的v2.3.0 Release
"""
import os
import sys
import io
import json
import urllib.request
import urllib.error
import urllib.parse
import base64

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 仓库信息
GITHUB_OWNER = "chrisKLP-sys"
GITHUB_REPO = "intersection-traffic-flow"
GITEE_OWNER = "Chris_KLP"
GITEE_REPO = "intersection-traffic-flow"

# 版本信息
VERSION = "2.3.0"
TAG = f"v{VERSION}"
TITLE = f"{TAG} - 在线更新功能"

# 读取token
def read_token(platform):
    token_file = f'{platform}_token.txt'
    if os.path.exists(token_file):
        with open(token_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 查找token（GitHub: ghp_开头，Gitee: 可能是其他格式）
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                # 提取token（可能是 token=xxx 格式或直接是token）
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        token = parts[1].strip()
                        if token:
                            return token
                # 直接是token（GitHub: ghp_开头，Gitee: 可能是其他格式）
                elif line.startswith('ghp_') or len(line) > 20:
                    return line
    return None

# Release描述（从CHANGELOG提取）
RELEASE_DESCRIPTION = """## v2.3.0 (2025-11-25)

### 新增功能

- 在线更新功能：支持从 GitHub 或 Gitee 检查更新
- 更新检查界面：在"关于"对话框中可以手动检查更新
- 更新源选择：支持选择从 GitHub 或 Gitee 检查更新
- 版本信息显示：在"关于"对话框中显示当前程序版本号
- 更新下载和安装：发现新版本后可以直接下载并安装更新
- 应用图标：为所有窗口添加精美的 Sparrow 图标
- 转向流量输入顺序提示：添加了详细的转向流量输入顺序说明

### 性能优化

- 图标加载优化：实现缓存机制，避免重复加载大图标文件
- 图标自动缩放：大图标自动缩放到64x64，提升性能
- 语言切换优化：增强错误处理和UI更新可靠性
- 表头对齐修复：修复表头与数据框的对齐问题

### 使用说明

- 点击菜单栏"帮助" → "关于"，打开关于对话框
- 在关于对话框中点击"检查更新"按钮
- 选择更新源（GitHub 或 Gitee）
- 如果有新版本，可以点击"下载"按钮下载并安装
- 程序会自动检查版本并提示是否需要更新
- 在数据输入窗口中，注意查看转向流量输入顺序的提示说明
"""

def create_github_release():
    """在GitHub上创建Release"""
    token = read_token('github')
    if not token:
        print("⚠ 未找到GitHub token，跳过GitHub操作")
        return False
    
    exe_file = f'dist\\交叉口交通流量流向可视化工具{VERSION}.exe'
    if not os.path.exists(exe_file):
        print(f"❌ 未找到可执行文件: {exe_file}")
        return False
    
    # 创建Release
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
    data = {
        "tag_name": TAG,
        "name": TITLE,
        "body": RELEASE_DESCRIPTION,
        "draft": False,
        "prerelease": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    # 使用token格式，避免编码问题
    req.add_header('Authorization', f'token {token}')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            release_data = json.loads(response.read())
            release_id = release_data['id']
            print(f"  ✓ 已创建GitHub Release: {TAG}")
            
            # 上传文件
            upload_url = release_data['upload_url'].split('{')[0]
            file_name = os.path.basename(exe_file)
            # URL编码文件名
            encoded_file_name = urllib.parse.quote(file_name)
            
            with open(exe_file, 'rb') as f:
                file_data = f.read()
            
            upload_req = urllib.request.Request(
                f"{upload_url}?name={encoded_file_name}",
                data=file_data,
                method='POST'
            )
            upload_req.add_header('Authorization', f'token {token}')
            upload_req.add_header('Accept', 'application/vnd.github.v3+json')
            upload_req.add_header('Content-Type', 'application/octet-stream')
            
            with urllib.request.urlopen(upload_req) as upload_response:
                upload_result = json.loads(upload_response.read())
                print(f"  ✓ 已上传文件到GitHub: {file_name}")
                print(f"    文件大小: {upload_result.get('size', 0) / 1024 / 1024:.2f} MB")
                return True
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"  ❌ 创建GitHub Release失败: {e.code}")
        print(f"    错误信息: {error_data[:200]}")
        return False
    except Exception as e:
        print(f"  ❌ 创建GitHub Release时出错: {e}")
        return False

def get_gitee_default_branch():
    """获取Gitee仓库的默认分支"""
    token = read_token('gitee')
    if not token:
        return "master"  # 默认值
    
    url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'token {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            repo_data = json.loads(response.read())
            return repo_data.get('default_branch', 'master')
    except:
        return "master"  # 默认值

def create_gitee_release():
    """在Gitee上创建Release"""
    token = read_token('gitee')
    if not token:
        print("⚠ 未找到Gitee token，跳过Gitee操作")
        return False
    
    exe_file = f'dist\\交叉口交通流量流向可视化工具{VERSION}.exe'
    if not os.path.exists(exe_file):
        print(f"❌ 未找到可执行文件: {exe_file}")
        return False
    
    # 获取默认分支
    default_branch = get_gitee_default_branch()
    
    # 创建Release
    url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/releases"
    data = {
        "tag_name": TAG,
        "name": TITLE,
        "body": RELEASE_DESCRIPTION,
        "target_commitish": default_branch,
        "draft": False,
        "prerelease": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    req.add_header('Authorization', f'token {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            release_data = json.loads(response.read())
            release_id = release_data['id']
            print(f"  ✓ 已创建Gitee Release: {TAG}")
            
            # Gitee上传文件需要先创建附件
            file_name = os.path.basename(exe_file)
            file_size = os.path.getsize(exe_file)
            
            # 读取文件并转换为base64
            with open(exe_file, 'rb') as f:
                file_data = f.read()
                file_base64 = base64.b64encode(file_data).decode('utf-8')
            
            # 上传附件
            upload_url = f"https://gitee.com/api/v5/repos/{GITEE_OWNER}/{GITEE_REPO}/releases/{release_id}/attach_files"
            upload_data = {
                "file_name": file_name,
                "file_content": file_base64
            }
            
            upload_req = urllib.request.Request(
                upload_url,
                data=json.dumps(upload_data).encode('utf-8'),
                method='POST'
            )
            upload_req.add_header('Authorization', f'token {token}')
            upload_req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(upload_req) as upload_response:
                upload_result = json.loads(upload_response.read())
                print(f"  ✓ 已上传文件到Gitee: {file_name}")
                print(f"    文件大小: {file_size / 1024 / 1024:.2f} MB")
                return True
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"  ❌ 创建Gitee Release失败: {e.code}")
        print(f"    错误信息: {error_data[:200]}")
        return False
    except Exception as e:
        print(f"  ❌ 创建Gitee Release时出错: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print(f"创建 {TAG} Release")
    print("=" * 60)
    
    print(f"\n检查可执行文件...")
    exe_file = f'dist\\交叉口交通流量流向可视化工具{VERSION}.exe'
    if os.path.exists(exe_file):
        file_size = os.path.getsize(exe_file) / 1024 / 1024
        print(f"  ✓ 找到可执行文件: {exe_file}")
        print(f"    文件大小: {file_size:.2f} MB")
    else:
        print(f"  ❌ 未找到可执行文件: {exe_file}")
        sys.exit(1)
    
    print(f"\n创建 GitHub Release...")
    github_success = create_github_release()
    
    print(f"\n创建 Gitee Release...")
    gitee_success = create_gitee_release()
    
    print("\n" + "=" * 60)
    if github_success and gitee_success:
        print("✓ 发布成功！")
    elif github_success or gitee_success:
        print("⚠ 部分发布成功，请检查失败的平台")
    else:
        print("❌ 发布失败，请检查token和网络连接")
    print("=" * 60)

