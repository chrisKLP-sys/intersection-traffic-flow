# 交叉口交通流量流向可视化工具 / Intersection Traffic Flow Visualize

[English](#english) | [中文](#中文)

---

**Latest Release / 最新版本: [v2.4.0](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases/tag/v2.4.0)** 🎉

<a name="english"></a>
## English

A professional Python application for visualizing traffic flow at intersections. This tool helps traffic engineers and planners visualize and analyze traffic patterns at 3-way, 4-way, 5-way, and 6-way intersections.

### Features

- 🚦 Support for 3-way, 4-way, 5-way, and 6-way intersections
- 📊 Automatic calculation of entry and exit traffic volumes
- 🎨 Visual representation with color-coded traffic flows
- 📈 Traffic flow lines with width proportional to volume
- 💾 Save and load traffic data files
- 🖼️ Export flow diagrams in multiple formats (SVG, PDF, PNG, JPG, TIF)
- 🪟 Centered window display for better user experience
- 📱 Cross-platform support (Windows, macOS, Linux)
- 🚗 Left-hand and right-hand traffic rule support
- 🌐 Multi-language interface: Simplified Chinese and English
- ⚙️ Configuration persistence: Saves language and traffic rule settings
- 🔄 Online update: Check for updates from GitHub or Gitee
- 🎯 Application icon: Beautiful Sparrow icon for all windows
- 📝 Flow input guidance: Detailed instructions for turning flow input order

### Screenshots

*(Add screenshots here if available)*

### Requirements

- Python 3.7 or higher
- Required packages:
  - matplotlib >= 3.5.0
  - numpy >= 1.21.0
  - Pillow >= 8.0.0
  - PyInstaller >= 5.0.0 (for building executable)

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/chrisKLP-sys/intersection-traffic-flow.git
cd intersection-traffic-flow
```

#### 2. Create a virtual environment (recommended)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Or use the provided setup script:
```bash
python setup_venv.py
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### Usage

#### Running the application

**Windows:**
```cmd
python main.py
```

**macOS/Linux:**
```bash
python3 main.py
```

Or if using virtual environment:
```bash
venv\Scripts\python.exe main.py  # Windows
venv/bin/python3 main.py           # macOS/Linux
```

#### Basic workflow

1. **Launch the application** - Select intersection type (3-way to 6-way) or load from file
2. **Enter traffic data** - Input entry names, angles, and flow volumes for each direction
3. **View the diagram** - Click "绘制流量图" (Draw Flow Diagram) to generate visualization
4. **Export results** - Save the diagram in SVG, PDF, PNG, JPG, or TIF format
5. **Save data** - Save your traffic data for future use

### Building executable

To build a standalone executable:

```bash
python build_all.py
```

This will create an executable in the `dist/` directory for your platform.

For more details, see the build configuration files:
- `build_all.py` - Automated build script
- `build_config.spec` - PyInstaller spec file
- `build_config.spec` - Alternative build configuration

### Project Structure

```
intersection-traffic-flow/
├── main.py                  # Main application entry
├── dialogs.py               # Dialog windows and startup UI
├── table_widget.py          # Main data table widget
├── file_operations.py       # Data file load/save logic
├── plotting.py              # Plot window and drawing orchestration
├── drawing_utils.py         # Low-level matplotlib drawing helpers
├── ui_utils.py              # Common UI utilities and styles
├── update_checker.py        # Online update check (GitHub / Gitee)
├── update_manager.py        # Update workflow and dialogs
├── update_gitee_release.py  # Sync release info to Gitee
├── config.py                # Config load/save helpers
├── config.txt               # User configuration file
├── i18n.py                  # Internationalization strings
├── build_all.py             # Build script (PyInstaller)
├── build_config.spec        # PyInstaller spec file
├── version_info.txt         # Version source for build/update
├── version_info.rc          # Windows version resource
├── requirements.txt         # Python dependencies
├── setup_venv.py            # Virtual environment helper
├── README.md                # This file
├── README_虚拟环境使用说明.md # Virtual environment usage guide (Chinese)
├── CHANGELOG.md             # Changelog
├── 帮助文档_中文.html        # Help documentation (Chinese)
├── 帮助文档_English.html    # Help documentation (English)
├── fonts/                   # Font files (HarmonyOS Sans etc.)
│   ├── HarmonyOS_Sans_SC_*.ttf
│   └── SourceHanSansCN-Regular.otf
├── Sparrow.ico              # Application icon (ICO)
├── Sparrow.png              # Application icon (PNG)
├── 测试数据_3路.txt          # Sample data (3-leg intersection)
├── 测试数据_4路.txt          # Sample data (4-leg intersection)
├── 测试数据_5路.txt          # Sample data (5-leg intersection)
└── 测试数据_6路.txt          # Sample data (6-leg intersection)
```

### Export Formats

The application supports exporting flow diagrams in the following formats:
- **SVG** (default) - Scalable vector graphics
- **PDF** - Portable document format
- **PNG** - Raster image
- **JPG** - Compressed image
- **TIF** - Tagged image format

### Development

#### Virtual Environment

See `README_虚拟环境使用说明.md` for detailed virtual environment setup instructions.

#### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable names
- Add comments for complex logic

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project also depends on several third‑party libraries and free fonts. Their licenses are provided by their own projects; please refer to their official pages for details and comply with the corresponding terms, for example:

- matplotlib, numpy, Pillow, PyInstaller, ttkbootstrap, CairoSVG, ReportLab, svglib and other Python libraries used in this project.
- HarmonyOS Sans SC (Huawei), used as the main UI font.
- Source Han Sans (Adobe / Google), used as a fallback / alternative CJK font.

### Author

交叉口交通流量流向可视化工具 Team

### Acknowledgments

- Built with [matplotlib](https://matplotlib.org/)
- Powered by [numpy](https://numpy.org/)
- Packaged with [PyInstaller](https://www.pyinstaller.org/)

---

<a name="中文"></a>
## 中文

**最新版本: [v2.4.0](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases/tag/v2.4.0)** 🎉

一款专业的交通流量可视化工具，用于绘制和分析交叉口的交通流量图。本工具帮助交通工程师和规划人员可视化和分析3路、4路、5路和6路交叉口的交通模式。

### 功能特性

- 🚦 支持3路、4路、5路、6路交叉口
- 📊 自动计算进口和出口交通量
- 🎨 彩色编码的交通流量可视化
- 📈 线宽与流量成正比的流量线
- 💾 保存和加载交通数据文件
- 🖼️ 多种格式导出流量图（SVG、PDF、PNG、JPG、TIF）
- 🪟 居中窗口显示，提升用户体验
- 📱 跨平台支持（Windows、macOS、Linux）
- 🚗 支持左行和右行通行规则
- 🌐 多语言界面：简体中文和英文
- ⚙️ 配置保存功能：自动保存语言和通行规则设置
- 🔄 在线更新：支持从 GitHub 或 Gitee 检查更新
- 🎯 应用图标：精美的 Sparrow 图标，所有窗口统一显示
- 📝 输入指引：详细的转向流量输入顺序说明

### 截图

*(如有截图，请在此处添加)*

### 系统要求

- Python 3.7 或更高版本
- 必需的包：
  - matplotlib >= 3.5.0
  - numpy >= 1.21.0
  - Pillow >= 8.0.0
  - PyInstaller >= 5.0.0（用于构建可执行文件）

### 安装

#### 1. 克隆仓库

```bash
git clone https://github.com/chrisKLP-sys/intersection-traffic-flow.git
cd intersection-traffic-flow
```

#### 2. 创建虚拟环境（推荐）

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

或使用提供的设置脚本：
```bash
python setup_venv.py
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

#### 运行程序

**Windows:**
```cmd
python main.py
```

**macOS/Linux:**
```bash
python3 main.py
```

如果使用虚拟环境：
```bash
venv\Scripts\python.exe main.py  # Windows
venv/bin/python3 main.py           # macOS/Linux
```

#### 基本工作流程

1. **启动程序** - 选择交叉口类型（3路到6路）或从文件加载
2. **输入交通数据** - 输入各方向的进口名称、方位角和流量数据
3. **查看图表** - 点击"绘制流量图"生成可视化图表
4. **导出结果** - 将图表保存为SVG、PDF、PNG、JPG或TIF格式
5. **保存数据** - 保存交通数据以便以后使用

### 构建可执行文件

要构建独立的可执行文件：

```bash
python build_all.py
```

这将在 `dist/` 目录中为您的平台创建可执行文件。

更多详细信息，请参阅构建配置文件：
- `build_all.py` - 自动化构建脚本
- `build_config.spec` - PyInstaller 配置文件
- `build_config.spec` - 替代构建配置

### 项目结构

```
intersection-traffic-flow/
├── main.py                  # 主程序入口
├── dialogs.py               # 各类对话框与启动界面 UI
├── table_widget.py          # 主界面数据表格
├── file_operations.py       # 数据文件读写与解析
├── plotting.py              # 绘图窗口与整体绘制逻辑
├── drawing_utils.py         # 底层 matplotlib 绘图工具
├── ui_utils.py              # 通用 UI 工具与样式
├── update_checker.py        # 联机检查更新（GitHub / Gitee）
├── update_manager.py        # 更新流程与更新对话框
├── update_gitee_release.py  # 发布信息同步到 Gitee
├── config.py                # 配置加载与保存辅助
├── config.txt               # 用户配置文件
├── i18n.py                  # 多语言文案定义
├── build_all.py             # 一键打包脚本（PyInstaller）
├── build_config.spec        # PyInstaller 配置文件
├── version_info.txt         # 版本号真源，用于构建与更新
├── version_info.rc          # Windows 版本资源
├── requirements.txt         # Python 依赖列表
├── setup_venv.py            # 虚拟环境辅助脚本
├── README.md                # 本说明文件
├── README_虚拟环境使用说明.md # 虚拟环境使用说明
├── CHANGELOG.md             # 版本更新记录
├── 帮助文档_中文.html        # 中文帮助文档
├── 帮助文档_English.html    # 英文帮助文档
├── fonts/                   # 字体文件（HarmonyOS Sans 等）
│   ├── HarmonyOS_Sans_SC_*.ttf
│   └── SourceHanSansCN-Regular.otf
├── Sparrow.ico              # 程序图标（ICO）
├── Sparrow.png              # 程序图标（PNG）
├── 测试数据_3路.txt          # 示例数据（3 路交叉口）
├── 测试数据_4路.txt          # 示例数据（4 路交叉口）
├── 测试数据_5路.txt          # 示例数据（5 路交叉口）
└── 测试数据_6路.txt          # 示例数据（6 路交叉口）
```

### 导出格式

程序支持以下格式导出流量图：
- **SVG**（默认）- 可缩放矢量图形
- **PDF** - 便携式文档格式
- **PNG** - 光栅图像
- **JPG** - 压缩图像
- **TIF** - 标记图像格式

### 开发

#### 虚拟环境

详细的虚拟环境设置说明，请参阅 `README_虚拟环境使用说明.md`。

#### 代码风格

- 遵循 PEP 8 Python 代码风格指南
- 使用有意义的变量名
- 为复杂逻辑添加注释

### 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

### 作者

交叉口交通流量流向可视化工具团队

### 致谢

- 基于 [matplotlib](https://matplotlib.org/) 构建
- 由 [numpy](https://numpy.org/) 提供支持
- 使用 [PyInstaller](https://www.pyinstaller.org/) 打包
- 使用 [Pillow](https://python-pillow.org/)、[ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) 等第三方库优化界面与图形
- 使用 [CairoSVG](https://cairosvg.org/)、[ReportLab](https://www.reportlab.com/)、[svglib](https://pypi.org/project/svglib/) 等库支持多格式导出
- 使用 [HarmonyOS Sans](https://developer.huawei.com/consumer/cn/design/resource/) / HarmonyOS Sans SC 作为主要界面字体
- 使用 [思源黑体 / Source Han Sans](https://github.com/adobe-fonts/source-han-sans) 作为中文备用字体

上述第三方库与字体均遵循其各自的开源或免费使用许可协议（如 MIT / BSD / GPL with exception / SIL OFL 等），本项目仅在其许可范围内使用，相关权利归原作者及其项目所有。

---

## 常见问题 / FAQ

### Windows PowerShell 执行策略错误

如果遇到 PowerShell 执行策略错误，可以使用以下方法：

1. 使用批处理文件：直接运行 `激活虚拟环境.bat`
2. 使用 CMD：运行 `venv\Scripts\activate.bat`
3. 直接使用 Python：`venv\Scripts\python.exe main.py`

更多详情请参考 `README_虚拟环境使用说明.md`。

### 打包后无法导出PDF/SVG

确保在打包时包含了所需的后端模块。相关配置已在 `build_all.py` 和 `.spec` 文件中设置。

### 窗口不居中

程序已实现自动居中功能。如果窗口仍然不在中心，请检查是否有多个显示器。

---

如有问题或建议，请提交 Issue 或联系维护者。

