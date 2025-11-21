# 上传到GitHub指南

本指南介绍如何将项目上传到GitHub，提供多种方法供您选择。

## 前置准备

您需要：
- ✅ GitHub账号（已有）
- ✅ 安装Git（如果没有的话）

### 检查是否已安装Git

在命令行（CMD或PowerShell）中运行：
```bash
git --version
```

如果显示版本号（如 `git version 2.x.x`），说明已安装。如果没有，请先安装Git：
- 下载地址：https://git-scm.com/download/win
- 或使用GitHub Desktop（包含Git）

---

## 方法一：使用Git命令行（推荐）

### 步骤1：初始化Git仓库

在项目目录（`d:\python\交叉口流量绘制`）中打开命令行，运行：

```bash
git init
```

### 步骤2：添加所有文件

```bash
git add .
```

### 步骤3：创建第一次提交

```bash
git commit -m "Initial commit: Open source release v1.0.0"
```

### 步骤4：在GitHub上创建新仓库

1. 登录GitHub（https://github.com）
2. 点击右上角的 **+** 号，选择 **New repository**
3. 填写仓库信息：
   - **Repository name**: `intersection-traffic-flow`（或您喜欢的名字）
   - **Description**: 交叉口流量绘制工具 / Intersection Traffic Flow Visualization Tool
   - **Visibility**: 选择 **Public**（公开）或 **Private**（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 **Create repository**

### 步骤5：连接本地仓库到GitHub

创建仓库后，GitHub会显示仓库地址，类似：
```
https://github.com/您的用户名/intersection-traffic-flow.git
```

在命令行中运行（**替换为您实际的仓库地址**）：

```bash
git remote add origin https://github.com/您的用户名/intersection-traffic-flow.git
```

### 步骤6：推送代码到GitHub

```bash
git branch -M main
git push -u origin main
```

**注意**：首次推送会要求输入GitHub用户名和密码（或Personal Access Token）。

---

## 方法二：使用GitHub Desktop（最简单，推荐新手）

GitHub Desktop是一个图形化工具，非常适合不熟悉命令行的用户。

### 步骤1：下载安装GitHub Desktop

- 下载地址：https://desktop.github.com/
- 安装后登录您的GitHub账号

### 步骤2：初始化仓库

1. 打开GitHub Desktop
2. 点击 **File** → **Add local repository**
3. 点击 **Create a New Repository on your Hard Drive**
4. 填写信息：
   - **Name**: `intersection-traffic-flow`
   - **Local path**: `d:\python\交叉口流量绘制`
   - **Git ignore**: 选择 **None**（我们已经有了.gitignore）
5. 点击 **Create repository**

### 步骤3：提交代码

1. 在GitHub Desktop中，您会看到所有文件的变化
2. 在左下角填写提交信息：`Initial commit: Open source release v1.0.0`
3. 点击 **Commit to main**

### 步骤4：发布到GitHub

1. 点击右上角的 **Publish repository**
2. 取消勾选 "Keep this code private"（如果要公开的话）
3. 点击 **Publish repository**

完成！代码已上传到GitHub。

---

## 方法三：使用IDE内置Git功能

如果您使用的是VSCode、PyCharm等IDE，可以直接在IDE中使用Git。

### VSCode

1. 点击左侧的源代码管理图标（或按 `Ctrl+Shift+G`）
2. 点击 **Initialize Repository**（如果还没初始化）
3. 输入提交信息并提交
4. 点击 **...** → **Remote** → **Add Remote**
5. 输入GitHub仓库地址
6. 点击 **Publish Branch**

### PyCharm

1. **VCS** → **Enable Version Control Integration** → 选择 **Git**
2. **VCS** → **Git** → **Add**
3. 右键项目 → **Git** → **Commit**
4. **VCS** → **Git** → **Push** → 配置远程仓库

---

## 方法四：直接在GitHub网页上上传（临时方案）

如果命令行和工具都不想用，可以：

1. 在GitHub上创建新仓库（步骤同上）
2. 点击 **uploading an existing file**
3. 将所有文件拖拽到网页中
4. 填写提交信息并提交

**注意**：这种方法不适合后续更新，建议使用前三种方法之一。

---

## 重要提示

### 1. 更新README.md中的仓库地址

上传成功后，记得更新 `README.md` 文件中的仓库地址：
- 将 `yourusername` 替换为您的GitHub用户名
- 将 `intersection-traffic-flow` 替换为您的实际仓库名

### 2. Personal Access Token（如果使用HTTPS）

如果使用命令行推送时要求输入密码，可能需要使用Personal Access Token：

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 **Generate new token (classic)**
3. 勾选 `repo` 权限
4. 生成后复制token（只显示一次，请保存好）
5. 推送时，用户名输入您的GitHub用户名，密码输入token

### 3. 使用SSH（推荐，避免每次输入密码）

如果您想使用SSH方式（不需要每次输入密码），可以：

1. 生成SSH密钥：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. 将公钥添加到GitHub：
   - 复制 `C:\Users\您的用户名\.ssh\id_ed25519.pub` 的内容
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - 粘贴并保存

3. 使用SSH地址连接：
```bash
git remote set-url origin git@github.com:您的用户名/intersection-traffic-flow.git
```

---

## 验证上传是否成功

上传后，访问您的GitHub仓库地址：
```
https://github.com/您的用户名/intersection-traffic-flow
```

应该能看到：
- ✅ README.md 显示在仓库首页
- ✅ 所有源代码文件
- ✅ LICENSE 文件
- ✅ 其他文档文件

---

## 后续更新代码

### 使用命令行

```bash
# 查看更改
git status

# 添加更改
git add .

# 提交更改
git commit -m "描述更改内容"

# 推送到GitHub
git push
```

### 使用GitHub Desktop

1. 在GitHub Desktop中查看更改
2. 填写提交信息
3. 点击 **Commit to main**
4. 点击 **Push origin**

---

## 常见问题

### Q: 提示"repository not found"
A: 检查仓库地址是否正确，确保GitHub上已创建仓库。

### Q: 提示"authentication failed"
A: 使用Personal Access Token代替密码，或设置SSH密钥。

### Q: 上传时哪些文件会被忽略？
A: `.gitignore` 文件中列出的文件会被忽略（如 `venv/`, `build/`, `dist/` 等）。

### Q: 如何删除已上传的文件？
A: 在GitHub网页上直接删除，或在本地删除后提交推送。

---

## 推荐工作流程

**新手推荐**：使用 **GitHub Desktop**（方法二）
- ✅ 图形化界面，操作简单
- ✅ 自动管理Git
- ✅ 可视化查看更改

**熟悉命令行的用户**：使用 **Git命令行**（方法一）
- ✅ 更灵活
- ✅ 功能更强大
- ✅ 适合高级操作

祝您上传顺利！如有问题，请查看GitHub官方文档或提交Issue。

