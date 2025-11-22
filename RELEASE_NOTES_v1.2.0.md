# Release Notes / 发布说明 - v1.2.0

## 🎉 Stable Release / 稳定版本发布

**Release Date / 发布日期:** 2025-11-22

This is a stable release of the Intersection Traffic Flow Visualize tool. This version includes comprehensive bug fixes, improvements, and new features that make it production-ready.

这是交叉口交通流量流向可视化工具的稳定版本。此版本包含全面的错误修复、改进和新功能，使其可用于生产环境。

---

## What's New / 新功能

### ✨ New Features / 新特性

- **Project Renaming / 项目重命名**
  - Renamed to "交叉口交通流量流向可视化工具" (Intersection Traffic Flow Visualize)
  - 重命名为"交叉口交通流量流向可视化工具"
  - Updated all references across codebase and documentation
  - 更新了代码库和文档中的所有引用

- **Enhanced Version Information / 增强的版本信息**
  - Added detailed version information to Windows executable
  - 为Windows可执行文件添加了详细的版本信息
  - Includes product name, version, author, and GitHub repository URL
  - 包含产品名称、版本、作者和GitHub仓库地址

- **Improved Data Input / 改进的数据输入**
  - Default azimuth angles automatically distributed from 0-360 degrees
  - 默认方位角自动从0-360度平均分布
  - Automatic entry naming when name field is empty
  - 当名称字段为空时自动命名进口

- **UI Enhancements / UI改进**
  - Modern, screen-friendly fonts (Source Han Sans / Microsoft YaHei)
  - 现代化、适合屏幕显示的字体（思源黑体/微软雅黑）
  - Adaptive window sizing for data input
  - 数据输入窗口自适应大小
  - Clear Data and New File buttons
  - 清空数据和新建文件按钮

### 🐛 Bug Fixes / 错误修复

- **Geometric Calculation Fixes / 几何计算修复**
  - Fixed division by zero errors in geometric calculations
  - 修复了几何计算中的除零错误
  - Improved infinite slope handling in line intersection calculations
  - 改进了直线交点计算中的无限斜率处理
  - Fixed infinite radius handling in arc drawing functions
  - 修复了圆弧绘制函数中的无限半径处理
  - Resolved zero-length vector normalization issues
  - 解决了零长度向量归一化问题
  - Enhanced parallel line intersection edge case handling
  - 增强了平行线交点的边界情况处理
  - Fixed negative radius handling in arc width calculations
  - 修复了圆弧宽度计算中的负半径处理

- **Text Rendering Fixes / 文本渲染修复**
  - Fixed `'list' object has no attribute 'flags'` error
  - 修复了 `'list' object has no attribute 'flags'` 错误
  - Improved text coordinate handling
  - 改进了文本坐标处理

### 🔧 Technical Improvements / 技术改进

- Enhanced floating-point comparison using epsilon values
  - 使用epsilon值改进了浮点数比较
- Improved error handling with fallback mechanisms
  - 改进了错误处理，使用备用机制
- Better font loading and embedding for cross-platform compatibility
  - 改进了字体加载和嵌入，提高跨平台兼容性
- Optimized build configuration for Windows executables
  - 优化了Windows可执行文件的构建配置

---

## Installation / 安装

### From Source / 从源码安装

```bash
git clone https://github.com/chrisKLP-sys/intersection-traffic-flow.git
cd intersection-traffic-flow
git checkout v1.2.0  # 切换到稳定版本标签
python setup_venv.py
pip install -r requirements.txt
python 交叉口交通流量流向可视化工具1.2.py
```

### Pre-built Executable / 预编译可执行文件

Download the Windows executable from the [Releases](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases/tag/v1.2.0) page.

从 [Releases](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases/tag/v1.2.0) 页面下载Windows可执行文件。

---

## Upgrade Notes / 升级说明

If you're upgrading from v1.1.0 or earlier:

如果您从v1.1.0或更早版本升级：

1. **Backup your data files** - Save any custom data files before upgrading
   - **备份数据文件** - 在升级前保存任何自定义数据文件

2. **Check file compatibility** - Data files from previous versions should work, but it's recommended to test
   - **检查文件兼容性** - 以前版本的数据文件应该可以工作，但建议进行测试

3. **Review new features** - Check the new default azimuth angle settings
   - **查看新功能** - 检查新的默认方位角设置

---

## Known Issues / 已知问题

None at this time. If you encounter any issues, please report them on the [Issues](https://github.com/chrisKLP-sys/intersection-traffic-flow/issues) page.

目前没有已知问题。如果您遇到任何问题，请在 [Issues](https://github.com/chrisKLP-sys/intersection-traffic-flow/issues) 页面上报告。

---

## Credits / 致谢

- **Developer / 开发者:** chrisKLP-sys
- **License / 许可证:** MIT
- **Repository / 仓库:** https://github.com/chrisKLP-sys/intersection-traffic-flow

---

## Support / 支持

For questions, bug reports, or feature requests, please visit:
如有问题、错误报告或功能请求，请访问：

- **GitHub Issues:** https://github.com/chrisKLP-sys/intersection-traffic-flow/issues
- **Documentation / 文档:** See `帮助文档.html` or `README.md`

---

**Thank you for using Intersection Traffic Flow Visualize! / 感谢使用交叉口交通流量流向可视化工具！** 🚦

