# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of 交叉口流量绘制 (Intersection Traffic Flow Visualization)
- Support for 3-way, 4-way, 5-way, and 6-way intersections
- Interactive data input interface
- Traffic flow visualization with color-coded flows
- Export functionality for multiple formats (SVG, PDF, PNG, JPG, TIF)
- Data save and load functionality
- Help documentation (HTML format)
- Window centering on display
- Support for custom font paths for Chinese characters
- Automatic calculation of entry and exit traffic volumes
- Visual representation with flow lines proportional to volume

### Features
- **Cross-platform support**: Windows, macOS, Linux
- **Multiple export formats**: SVG (default), PDF, PNG, JPG, TIF
- **Data persistence**: Save and load traffic data files
- **User-friendly interface**: Centered windows, clear layout
- **Comprehensive help**: Built-in help documentation

### Technical Details
- Built with Python 3.7+
- Uses matplotlib for visualization
- Uses tkinter for GUI
- Packaged with PyInstaller for standalone executables
- Supports virtual environment setup

### Documentation
- Main README.md (English and Chinese)
- Help documentation (HTML)
- Virtual environment setup guide
- Build and packaging instructions

## [1.1.0] - 2024-11-XX

### Added
- Modern UI design with flat style buttons and improved color scheme
- Font optimization: Support for Source Han Sans and Microsoft YaHei fonts
- Window auto-sizing: Automatically adjusts window size based on intersection type
- New buttons: "新建文件" (New File) and "清空数据" (Clear Data)
- Enhanced azimuth angle warning with error troubleshooting tips

### Changed
- Improved font rendering for better screen display (Source Han Sans / Microsoft YaHei)
- Updated UI styling with modern flat design
- Enhanced dialog boxes with better spacing and backgrounds
- Improved window centering and sizing logic

### Fixed
- Font loading issues on Windows systems
- Window size adaptation for different intersection types
- UI component font consistency

### Technical Details
- Added `setup_modern_style()` function for unified UI styling
- Improved font loading with fallback to system fonts
- Enhanced window management with `adjust_window_size()` function
- Updated help documentation (v1.1)

## Future Plans

### Potential Features
- Support for more intersection types (7-way, 8-way)
- Batch processing of multiple intersections
- Statistical analysis of traffic data
- Integration with traffic data sources
- Export to CAD formats
- Custom color schemes
- Keyboard shortcuts
- Dark mode theme

### Improvements
- Performance optimization
- Additional export formats
- Enhanced error handling
- Unit tests
- CI/CD pipeline

---

## Version History

- **v1.1.0** - UI improvements, font optimization, window auto-sizing
- **v1.0.0** - Initial release

---

For more details, see the [releases](https://github.com/chrisKLP-sys/intersection-traffic-flow/releases) page.

