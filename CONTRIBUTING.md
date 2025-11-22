# Contributing Guidelines

Thank you for your interest in contributing to 交叉口交通流量流向可视化工具 (Intersection Traffic Flow Visualize)! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear title and description
- Steps to reproduce the bug
- Expected behavior vs actual behavior
- Environment information (OS, Python version)
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please open an issue with:
- A clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Follow the code style guidelines
5. Test your changes
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/chrisKLP-sys/intersection-traffic-flow.git
cd intersection-traffic-flow
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guidelines
- Use meaningful variable names (prefer English for code, Chinese for user-facing strings)
- Add comments for complex logic
- Keep functions focused and small
- Write docstrings for functions and classes

### Code Formatting

- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use descriptive variable and function names

### Example

```python
def calculate_traffic_volume(entry_flows, exit_flows):
    """
    Calculate total traffic volume for an intersection.
    
    Args:
        entry_flows: List of entry flow volumes
        exit_flows: List of exit flow volumes
        
    Returns:
        Total traffic volume
    """
    return sum(entry_flows) + sum(exit_flows)
```

## Testing

Before submitting a pull request:
- Test your changes on your platform
- Test with different intersection types (3-way to 6-way)
- Verify export functionality works
- Check that the application runs without errors

## Commit Messages

Write clear commit messages:
- Use the imperative mood ("Add feature" not "Added feature")
- First line should be a brief summary (50 characters or less)
- Add more detailed explanation if needed

Examples:
- `Add support for 7-way intersections`
- `Fix window centering on multi-monitor systems`
- `Update dependencies in requirements.txt`

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Add comments to explain complex code
4. Update CHANGELOG.md if applicable
5. Request review from maintainers

## Questions?

If you have questions, please open an issue with the `question` label.

Thank you for contributing! 🎉

