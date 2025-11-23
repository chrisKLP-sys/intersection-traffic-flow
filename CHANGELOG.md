# Changelog / 更新日志

All notable changes to this project will be documented in this file.

本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

---

## [2.1.0] - 2025-11-22

**🎉 Stable Release / 稳定版本发布**

This is a stable release with new features and improvements. Recommended for production use.
这是一个稳定版本，包含新功能和改进。推荐用于生产环境。

### Added / 新增

- Left-hand traffic rule support: Supports both left-hand and right-hand traffic rules
  - 左行规则支持：支持左行规则和右行规则两种交通规则
- Traffic rule selection: Can select traffic rule above data table
  - 交通规则选择：可在数据表格上方选择交通规则
- Dynamic headers: 4-way intersection headers automatically adjust based on traffic rule
  - 动态表头：4路交叉口表头根据交通规则自动调整
- File format update: Data files include traffic rule information
  - 文件格式更新：数据文件包含交通规则信息
- Enhanced file parsing: Automatically infers intersection type from data if not declared
  - 增强的文件解析：如果未声明，自动从数据推断交叉口类型
- Default traffic rule: Defaults to right-hand traffic if not specified
  - 默认交通规则：如果未指定，默认为右行规则
- Multi-language support: Simplified Chinese and English interfaces
  - 多语言支持：简体中文和英文界面
- Language selection menu: Switch interface language from menu bar
  - 语言选择菜单：可在菜单栏中切换界面语言
- Global language switching: Language changes apply to all windows (startup dialog, main window, dialogs)
  - 全局语言切换：语言切换对所有窗口生效（启动对话框、主窗口、对话框）
- Separated help documents: Chinese and English help documents provided separately
  - 帮助文档分离：中英文帮助文档分别提供
- Dynamic UI updates: All interface text updates automatically when language changes
  - 动态界面更新：语言切换时所有界面文本自动更新
- Adaptive button widths: Button widths adjust based on language (wider for English)
  - 自适应按钮宽度：按钮宽度根据语言调整（英文更宽）
- Window size auto-adjustment: Windows resize automatically after language change
  - 窗口大小自动调整：语言切换后窗口自动调整大小
- Configuration persistence: Automatically saves language and traffic rule settings to config.txt
  - 配置保存功能：自动保存语言和通行规则设置到config.txt文件
- Config file format: User-friendly TXT format with bilingual instructions (Chinese and English)
  - 配置文件格式：用户友好的TXT格式，包含中英文双语说明
- Startup dialog enhancements: Added Help and About buttons at the bottom
  - 启动界面增强：在底部添加帮助和关于按钮

### Changed / 变更

- Data file format: First line now includes traffic rule declaration
  - 数据文件格式：第一行现在包含交通规则声明
- File format: "本交叉口为X路交叉口，实行左/右行通行规则。"
  - 文件格式："本交叉口为X路交叉口，实行左/右行通行规则。"
- Table header order: Changes based on traffic rule for 4-way intersections
  - 表头顺序：4路交叉口的表头顺序根据交通规则变化
- All interface text now uses translation functions
  - 所有界面文本现在使用翻译函数
- File export dialog: File type descriptions and default filenames are now translated
  - 文件导出对话框：文件类型描述和默认文件名现在已翻译
- Help document loading: Automatically selects help document based on current language
  - 帮助文档加载：根据当前语言自动选择帮助文档
- Configuration file: Changed from JSON to TXT format for better user-friendliness
  - 配置文件：从JSON格式改为TXT格式，更便于用户编辑

### Technical Details / 技术细节

- Modified `draw_turn_path_generic()` to support left-hand traffic
  - 修改了 `draw_turn_path_generic()` 以支持左行规则
- Updated `plot_traffic_flow()` with traffic rule parameter
  - 更新了 `plot_traffic_flow()`，添加了交通规则参数
- Enhanced `load_data_from_file()` to parse traffic rule from file
  - 增强了 `load_data_from_file()` 以从文件解析交通规则
- Added `on_rule_change()` callback in `Table` class
  - 在 `Table` 类中添加了 `on_rule_change()` 回调函数
- Added `LANGUAGES` dictionary with Chinese and English translations
  - 添加了包含中英文翻译的 `LANGUAGES` 字典
- Implemented `t()` translation function with string formatting support
  - 实现了支持字符串格式化的 `t()` 翻译函数
- Added `update_ui_language()` function for dynamic UI updates
  - 添加了 `update_ui_language()` 函数用于动态界面更新
- Enhanced `Table` class with `update_language()` method
  - 增强了 `Table` 类，添加了 `update_language()` 方法
- Language menu added to startup dialog, new file dialog, and main window
  - 在启动对话框、新建文件对话框和主窗口添加了语言菜单
- Added configuration management functions: `load_config()`, `save_config()`, `get_config_path()`
  - 添加了配置管理函数：`load_config()`, `save_config()`, `get_config_path()`
- Configuration auto-saves on language change and traffic rule change
  - 配置在语言切换和通行规则切换时自动保存
- Configuration loads on startup and applies to language and traffic rule settings
  - 配置在启动时加载并应用到语言和通行规则设置

---

## [1.3.0] - 2025-11-22

**🎉 Stable Release / 稳定版本发布**

This is a stable release with new features and improvements. Recommended for production use.
这是一个稳定版本，包含新功能和改进。推荐用于生产环境。

### Added / 新增

- Exit width bar arrows: Added solid arrows at the end of exit width bars
  - 出口宽度条箭头：在出口宽度条末端添加实心箭头
- Extended entry width bars: Entry width bars now extend 45 units outward
  - 延长进口宽度条：进口宽度条现在向外延长45单位
- Expanded plot window: Plot window range expanded from (-330, 330) to (-375, 375)
  - 扩大绘图窗口：绘图窗口范围从(-330, 330)扩大到(-375, 375)
- Adjusted entry name labels: Entry name labels moved 45 units outward along azimuth angle direction
  - 调整进口名称标签：进口名称标签沿方位角方向向外移动45单位

### Fixed / 修复

- Startup dialog close handling: Fixed error when closing startup dialog, now properly terminates all processes
  - 启动界面关闭处理：修复了关闭启动界面时的错误，现在能正确终止所有进程

### Changed / 变更

- Arrow specifications:
  - Length: 45 units
  - Width: 1.8 times the exit width bar width
  - Color: Same as exit width bar color
  - 箭头规格：
    - 长度：45单位
    - 宽度：出口宽度条宽度的1.8倍
    - 颜色：与出口宽度条颜色一致

---
## [1.2.0] - 2025-11-22

### Fixed / 修复

- Division by zero errors in geometric calculations
  - 修复了几何计算中的除零错误
- Infinite slope handling in line intersection calculations
  - 改进了直线交点计算中的无限斜率处理
- Infinite radius handling in arc drawing functions
  - 优化了圆弧绘制函数中的无限半径处理
- Zero-length vector normalization issues
  - 修复了零长度向量归一化问题
- Parallel line intersection edge cases
  - 改进了平行线交点的边界情况处理
- Negative radius handling in arc width calculations
  - 修复了圆弧宽度计算中的负半径处理
- Improved floating-point comparison using epsilon values
  - 使用epsilon值改进了浮点数比较

### Technical Details / 技术细节

- Enhanced `find_intersection()` function with epsilon-based comparison
  - 增强了 `find_intersection()` 函数，使用基于epsilon的比较
- Added safety checks in `create_wide_line_with_arc()` for parallel lines
  - 在 `create_wide_line_with_arc()` 中添加了平行线的安全检查
- Improved `create_parallel_arcs_with_width()` with None checks for circle centers
  - 改进了 `create_parallel_arcs_with_width()`，添加了圆心为None的检查
- Added radius validation in `draw_arc_with_width()` function
  - 在 `draw_arc_with_width()` 函数中添加了半径验证
- Enhanced vector normalization with zero-length checks
  - 增强了向量归一化，添加了零长度检查
- Improved error handling with fallback to straight line connections
  - 改进了错误处理，使用直线连接作为备用方案

---

## [1.1.0] - 2025-11-22

### Added / 新增

- Modern UI design with flat style buttons and improved color scheme
  - 现代化的UI设计，采用扁平风格按钮和改进的配色方案
- Font optimization: Support for Source Han Sans and Microsoft YaHei fonts
  - 字体优化：支持思源黑体和微软雅黑字体
- Window auto-sizing: Automatically adjusts window size based on intersection type
  - 窗口自适应：根据交叉口类型自动调整窗口大小
- New buttons: "新建文件" (New File) and "清空数据" (Clear Data)
  - 新增按钮："新建文件"和"清空数据"
- Enhanced azimuth angle warning with error troubleshooting tips
  - 增强了方位角警告，包含错误排查提示

### Changed / 变更

- Improved font rendering for better screen display (Source Han Sans / Microsoft YaHei)
  - 改进了字体渲染，更适合屏幕显示（思源黑体/微软雅黑）
- Updated UI styling with modern flat design
  - 更新了UI样式，采用现代化扁平设计
- Enhanced dialog boxes with better spacing and backgrounds
  - 增强了对话框，改进了间距和背景
- Improved window centering and sizing logic
  - 改进了窗口居中和大小调整逻辑

### Fixed / 修复

- Font loading issues on Windows systems
  - 修复了Windows系统上的字体加载问题
- Window size adaptation for different intersection types
  - 修复了不同交叉口类型的窗口大小适配问题
- UI component font consistency
  - 修复了UI组件字体一致性问题

### Technical Details / 技术细节

- Added `setup_modern_style()` function for unified UI styling
  - 添加了 `setup_modern_style()` 函数，用于统一UI样式
- Improved font loading with fallback to system fonts
  - 改进了字体加载，支持回退到系统字体
- Enhanced window management with `adjust_window_size()` function
  - 增强了窗口管理，添加了 `adjust_window_size()` 函数
- Updated help documentation (v1.1)
  - 更新了帮助文档（v1.1）

---

## [1.0.0] - 2025-11-22

### Added / 新增

- Initial release of 交叉口交通流量流向可视化工具 (Intersection Traffic Flow Visualize)
  - 交叉口交通流量流向可视化工具的初始版本发布
- Support for 3-way, 4-way, 5-way, and 6-way intersections
  - 支持3路、4路、5路和6路交叉口
- Interactive data input interface
  - 交互式数据输入界面
- Traffic flow visualization with color-coded flows
  - 彩色编码的交通流量可视化
- Export functionality for multiple formats (SVG, PDF, PNG, JPG, TIF)
  - 支持多种格式导出（SVG、PDF、PNG、JPG、TIF）
- Data save and load functionality
  - 数据保存和加载功能
- Help documentation (HTML format)
  - 帮助文档（HTML格式）
- Window centering on display
  - 窗口在显示器上居中显示
- Support for custom font paths for Chinese characters
  - 支持自定义中文字体路径
- Automatic calculation of entry and exit traffic volumes
  - 自动计算进口和出口交通量
- Visual representation with flow lines proportional to volume
  - 流量线宽度与流量成正比的视觉表示

### Features / 功能特性

- **Cross-platform support**: Windows, macOS, Linux
  - **跨平台支持**：Windows、macOS、Linux
- **Multiple export formats**: SVG (default), PDF, PNG, JPG, TIF
  - **多种导出格式**：SVG（默认）、PDF、PNG、JPG、TIF
- **Data persistence**: Save and load traffic data files
  - **数据持久化**：保存和加载交通数据文件
- **User-friendly interface**: Centered windows, clear layout
  - **用户友好界面**：居中窗口，清晰布局
- **Comprehensive help**: Built-in help documentation
  - **全面帮助**：内置帮助文档

### Technical Details / 技术细节

- Built with Python 3.7+
  - 使用 Python 3.7+ 构建
- Uses matplotlib for visualization
  - 使用 matplotlib 进行可视化
- Uses tkinter for GUI
  - 使用 tkinter 构建GUI
- Packaged with PyInstaller for standalone executables
  - 使用 PyInstaller 打包为独立可执行文件
- Supports virtual environment setup
  - 支持虚拟环境设置

### Documentation / 文档

- Main README.md (English and Chinese)
  - 主 README.md（中英文）
- Help documentation (HTML)
  - 帮助文档（HTML）
- Virtual environment setup guide
  - 虚拟环境设置指南
- Build and packaging instructions
  - 构建和打包说明

---

## Future Plans / 未来计划

### Potential Features / 潜在功能

- Support for more intersection types (7-way, 8-way)
  - 支持更多交叉口类型（7路、8路）
- Batch processing of multiple intersections
  - 批量处理多个交叉口
- Statistical analysis of traffic data
  - 交通数据统计分析
- Integration with traffic data sources
  - 与交通数据源集成
- Export to CAD formats
  - 导出为CAD格式
- Custom color schemes
  - 自定义配色方案
- Keyboard shortcuts
  - 键盘快捷键
- Dark mode theme
  - 深色模式主题

### Improvements / 改进计划

- Performance optimization
  - 性能优化
- Additional export formats
  - 额外的导出格式
- Enhanced error handling
  - 增强的错误处理
- Unit tests
  - 单元测试
- CI/CD pipeline
  - CI/CD 流水线

---

## Version History / 版本历史

- **v2.1.0** (Stable) - Complete feature set: Left-hand traffic rules, multi-language support, configuration persistence
  - **v2.1.0** (稳定版) - 完整功能集：左行规则、多语言支持、配置保存
- **v1.3.0** - New features: exit arrows, extended entry bars, expanded plot window
  - **v1.3.0** - 新功能：出口箭头、延长进口条、扩大绘图窗口
- **v1.2.0** - Bug fixes: division by zero, infinite slope/radius handling, improved geometric calculations
  - **v1.2.0** - 错误修复：除零错误、无限斜率/半径处理、改进的几何计算
- **v1.1.0** - UI improvements, font optimization, window auto-sizing
  - **v1.1.0** - UI改进、字体优化、窗口自适应
- **v1.0.0** - Initial release
  - **v1.0.0** - 初始版本

---

For more details, see the [releases](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases) page.

更多详情，请参阅[发布页面](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases)。
