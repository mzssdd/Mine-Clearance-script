# 扫雷辅助工具项目 / Minesweeper Helper

一个智能的扫雷游戏辅助系统，能够识别屏幕上的扫雷游戏并提供游戏提示。

## 📋 项目文件

- **minesweeper_solver.py** - 主程序，用于识别真实扫雷游戏
- **minesweeper_demo.py** - 演示程序，使用模拟棋盘展示功能
- **requirements.txt** - Python 依赖包列表
- **QUICKSTART.md** - 快速开始指南 ⭐ 推荐先看这个
- **MINESWEEPER_README.md** - 详细使用文档

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示（推荐）

```bash
python minesweeper_demo.py
```

这会创建一个模拟的扫雷游戏并自动给出提示，帮助你理解工具的工作原理。

### 3. 使用真实游戏

```bash
python minesweeper_solver.py
```

然后按照提示操作：

- 打开扫雷游戏
- 输入 `s` 开始扫描
- 输入棋盘大小（如 `9x9`）
- 查看生成的提示图片

## ✨ 功能特性

- 🎯 **自动识别** - 扫描屏幕上的扫雷游戏界面
- 🧠 **智能分析** - 分析当前棋盘状态
- 💡 **游戏提示** - 标注安全格子和地雷位置
- 🖼️ **可视化** - 生成带标注的提示图像
- 📊 **演示模式** - 模拟棋盘用于学习和测试

## 📖 使用说明

详细的使用说明请查看：

- [快速开始指南](QUICKSTART.md) - 5 分钟上手
- [完整文档](MINESWEEPER_README.md) - 深入了解所有功能

## 🎮 支持的游戏

- Windows 自带扫雷游戏
- 在线扫雷游戏（如 minesweeper.online）
- 其他标准扫雷游戏

## 🔧 技术栈

- **OpenCV** - 图像处理和识别
- **NumPy** - 数值计算
- **PyAutoGUI** - 屏幕截图
- **Pillow** - 图像绘制和处理

## 📝 提示说明

- 🟢 **绿色边框 + ✓** = 安全格子，可以点击
- 🔴 **红色边框 + 💣** = 地雷格子，需要标记

## ⚠️ 注意事项

- 需要正确输入棋盘大小才能准确分析
- 游戏需要已经翻开一些格子（至少 3-5 个）
- 确保游戏窗口清晰可见，不被遮挡

## 📸 演示截图

运行 `minesweeper_demo.py` 会生成两张图片：

- `demo_initial.png` - 初始游戏状态
- `demo_hints.png` - 带提示的游戏状态（绿色=安全，红色=地雷）

## 📄 许可证

MIT License

## 🤝 免责声明

本工具仅供学习和研究使用，请勿用于作弊或违反游戏规则的行为。

---

## English Version

An intelligent Minesweeper game assistant that can recognize Minesweeper games on your screen and provide game hints.

### Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run demo: `python minesweeper_demo.py`
3. Use with real game: `python minesweeper_solver.py`

### Features

- 🎯 Auto-detect game board
- 🧠 Smart analysis
- 💡 Hint generation
- 🖼️ Visual overlay

See [QUICKSTART.md](QUICKSTART.md) and [MINESWEEPER_README.md](MINESWEEPER_README.md) for detailed instructions.
