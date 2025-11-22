# Changelog / 更新日志

All notable changes to this project will be documented in this file.

本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

---

## [1.2.0] - 2025-11-22

**🎉 Stable Release / 稳定版本发布**

This is a stable release with comprehensive bug fixes and improvements. Recommended for production use.
这是一个稳定版本，包含全面的错误修复和改进。推荐用于生产环境。

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

- **v1.2.0** - Bug fixes: division by zero, infinite slope/radius handling, improved geometric calculations
  - **v1.2.0** - 错误修复：除零错误、无限斜率/半径处理、改进的几何计算
- **v1.1.0** - UI improvements, font optimization, window auto-sizing
  - **v1.1.0** - UI改进、字体优化、窗口自适应
- **v1.0.0** - Initial release
  - **v1.0.0** - 初始版本

---

For more details, see the [releases](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases) page.

更多详情，请参阅[发布页面](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases)。
