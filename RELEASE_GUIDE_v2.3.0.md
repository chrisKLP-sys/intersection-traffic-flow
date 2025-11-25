# 版本 2.3.0 发布指南

## ✅ 打包完成

- 可执行文件：`dist\交叉口交通流量流向可视化工具2.3.0.exe`
- 文件大小：84.01 MB
- 打包时间：已完成

## 📋 发布步骤

### 1. 删除旧的 v2.3 版本

#### GitHub
1. 访问：https://github.com/chrisKLP-sys/intersection-traffic-flow/releases
2. 找到 `v2.3` 标签的 Release
3. 点击 "Delete release" 删除发行版
4. 在 Tags 页面删除 `v2.3` 标签

#### Gitee
1. 访问：https://gitee.com/Chris_KLP/intersection-traffic-flow/releases
2. 找到 `v2.3` 标签的 Release
3. 点击删除发行版
4. 在 Tags 页面删除 `v2.3` 标签

或者运行脚本（需要配置token）：
```bash
python delete_release_v2.3.py
```

### 2. 创建新的 v2.3.0 Release

#### GitHub
1. 访问：https://github.com/chrisKLP-sys/intersection-traffic-flow/releases/new
2. **Tag**: `v2.3.0`
3. **Title**: `v2.3.0 - 在线更新功能`
4. **Description**: 从 CHANGELOG.md 复制 2.3.0 版本的内容
5. **上传文件**: 
   - `dist\交叉口交通流量流向可视化工具2.3.0.exe`
6. 勾选 "Set as the latest release"
7. 点击 "Publish release"

#### Gitee
1. 访问：https://gitee.com/Chris_KLP/intersection-traffic-flow/releases/new
2. **标签**: `v2.3.0`
3. **标题**: `v2.3.0 - 在线更新功能`
4. **描述**: 从 CHANGELOG.md 复制 2.3.0 版本的内容
5. **上传文件**: 
   - `dist\交叉口交通流量流向可视化工具2.3.0.exe`
6. 点击 "发布"

### 3. 验证发布

- [ ] GitHub Release 已创建
- [ ] Gitee Release 已创建
- [ ] 可执行文件已上传
- [ ] 版本号正确（v2.3.0）
- [ ] 描述信息完整

## 📝 Release 描述模板

```
## v2.3.0 (2025-11-25)

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
```

## ⚠️ 注意事项

1. **文件位置**：可执行文件在 `dist\交叉口交通流量流向可视化工具2.3.0.exe`
2. **文件大小**：约 84 MB
3. **版本号**：确保使用 `v2.3.0`（不是 `v2.3`）
4. **标签格式**：GitHub 和 Gitee 都使用 `v2.3.0`

