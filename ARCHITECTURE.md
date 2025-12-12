# 🏗️ 项目架构文档

## 概述

本项目采用模块化架构设计，将功能划分为核心逻辑、图形界面和工具模块三个主要部分。

## 架构图

```
┌─────────────────────────────────────────┐
│           GUI Layer (界面层)             │
│  ┌────────────┐  ┌──────────────────┐  │
│  │ MainWindow │  │  Custom Widgets  │  │
│  └────────────┘  └──────────────────┘  │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│         Core Layer (核心层)              │
│  ┌─────────────┐  ┌──────────────────┐ │
│  │ImageProcessor│  │ Board Analyzer   │ │
│  └─────────────┘  └──────────────────┘ │
│  ┌─────────────────────────────────┐   │
│  │   Minesweeper Solver             │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│        Utils Layer (工具层)              │
│  ┌──────────┐  ┌─────────────────────┐ │
│  │Constants │  │   Image Utils       │ │
│  └──────────┘  └─────────────────────┘ │
└─────────────────────────────────────────┘
```

## 模块详解

### 1. GUI Layer (界面层)

#### 1.1 MainWindow (主窗口)

**职责:**
- 界面布局管理
- 用户交互处理
- 状态更新显示
- 核心模块调度

**主要方法:**
```python
setup_ui()              # 设置界面
on_size_changed()       # 处理大小改变
start_capture()         # 开始捕获
analyze_board()         # 分析棋盘
save_image()            # 保存图片
update_status()         # 更新状态
```

**依赖:**
- ImageProcessor
- BoardAnalyzer
- MinesweeperSolver
- Widgets

#### 1.2 Widgets (自定义组件)

**包含组件:**

1. **ControlPanel** - 控制面板
   - 棋盘大小选择
   - 操作按钮
   - 自定义输入

2. **ImageCanvas** - 图像画布
   - 图像显示
   - 自动缩放

3. **InfoText** - 信息文本
   - 提示信息显示
   - 滚动支持

### 2. Core Layer (核心层)

#### 2.1 ImageProcessor (图像处理器)

**职责:**
- 屏幕截图
- 棋盘区域检测
- 格子状态识别
- 提示图层绘制

**主要方法:**
```python
capture_screenshot()    # 捕获屏幕
detect_board()          # 检测棋盘
recognize_cell()        # 识别格子
create_hint_overlay()   # 创建提示层
```

**技术:**
- OpenCV (图像处理)
- PyAutoGUI (截图)
- Pillow (绘图)

#### 2.2 BoardAnalyzer (棋盘分析器)

**职责:**
- 棋盘状态分析
- 格子数据管理
- 棋盘信息提供

**主要方法:**
```python
set_board_size()        # 设置大小
analyze()               # 分析棋盘
get_board_state()       # 获取状态
get_cell_size()         # 获取格子大小
```

**数据结构:**
```python
board: np.ndarray       # 棋盘矩阵
rows: int               # 行数
cols: int               # 列数
cell_size: int          # 格子大小
```

#### 2.3 MinesweeperSolver (求解器)

**职责:**
- 逻辑推理
- 安全/地雷判断
- 统计信息

**主要方法:**
```python
solve()                 # 求解
get_results()           # 获取结果
get_statistics()        # 获取统计
```

**算法:**
1. 遍历所有数字格子
2. 分析周围未知格子
3. 应用扫雷规则：
   - 未知数 = 剩余雷数 → 全是雷
   - 标记数 = 数字 → 全安全

### 3. Utils Layer (工具层)

#### 3.1 Constants (常量)

**包含:**
- 棋盘大小预设
- 颜色定义
- GUI配置
- 图像配置
- 消息模板
- 文件配置

**类别:**
```python
BOARD_SIZES             # 棋盘大小
Colors                  # 颜色常量
GUIConfig               # GUI配置
ImageConfig             # 图像配置
Messages                # 消息模板
CellState               # 格子状态
FileConfig              # 文件配置
```

#### 3.2 ImageUtils (图像工具)

**功能:**
- 图像格式转换
- 尺寸调整
- 区域提取
- 棋盘检测

**主要函数:**
```python
numpy_to_pil()          # numpy转PIL
resize_to_fit()         # 调整大小
detect_board_region()   # 检测棋盘
extract_board_region()  # 提取区域
get_cell_image()        # 获取格子
```

## 数据流

### 1. 启动流程

```
run.py
  └─> main.py
      └─> MainWindow.__init__()
          ├─> 创建 ImageProcessor
          ├─> 创建 BoardAnalyzer
          ├─> 创建 MinesweeperSolver
          └─> setup_ui()
```

### 2. 捕获流程

```
用户点击"捕获"
  └─> MainWindow.start_capture()
      └─> 新线程 capture_screen_delayed()
          └─> ImageProcessor.capture_screenshot()
              └─> ImageProcessor.detect_board()
                  └─> 显示图像
```

### 3. 分析流程

```
用户点击"分析"
  └─> MainWindow.analyze_board()
      ├─> BoardAnalyzer.set_board_size()
      ├─> BoardAnalyzer.analyze()
      │   └─> 遍历每个格子
      │       └─> ImageProcessor.recognize_cell()
      ├─> MinesweeperSolver.solve()
      │   └─> 遍历数字格子
      │       └─> 应用推理规则
      ├─> ImageProcessor.create_hint_overlay()
      └─> 显示结果
```

## 设计模式

### 1. 单一职责原则 (SRP)

每个类只负责一个功能：
- ImageProcessor: 图像处理
- BoardAnalyzer: 棋盘分析
- MinesweeperSolver: 逻辑求解

### 2. 依赖注入 (DI)

```python
# BoardAnalyzer 依赖 ImageProcessor
analyzer = BoardAnalyzer(image_processor)

# Solver 依赖 BoardAnalyzer
solver = MinesweeperSolver(board_analyzer)
```

### 3. 观察者模式

GUI监听核心模块的状态变化：
```python
def update_status(message):
    self.status_label.config(text=message)
```

### 4. 策略模式

可替换的识别算法：
```python
class CustomRecognizer(ImageProcessor):
    def recognize_cell(self, cell_image):
        # 自定义识别策略
        pass
```

## 扩展指南

### 添加新的识别算法

```python
# src/core/advanced_recognizer.py
from .image_processor import ImageProcessor

class AdvancedRecognizer(ImageProcessor):
    def recognize_cell(self, cell_image):
        # 使用机器学习模型
        model = load_model()
        return model.predict(cell_image)
```

### 添加新的求解策略

```python
# src/core/probability_solver.py
from .solver import MinesweeperSolver

class ProbabilitySolver(MinesweeperSolver):
    def solve_with_probability(self):
        # 概率分析
        probabilities = self.calculate_probabilities()
        return self.get_best_moves(probabilities)
```

### 添加新的GUI组件

```python
# src/gui/statistics_panel.py
import tkinter as tk

class StatisticsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
    
    def update_stats(self, stats):
        # 更新统计信息
        pass
```

## 配置管理

所有配置集中在 `constants.py`:

```python
# 修改窗口大小
GUIConfig.WINDOW_SIZE = '1200x800'

# 修改截图延迟
GUIConfig.CAPTURE_DELAY = 3

# 修改识别阈值
ImageConfig.BRIGHT_THRESHOLD = 180
```

## 测试建议

### 单元测试结构

```
tests/
├── test_core/
│   ├── test_image_processor.py
│   ├── test_board_analyzer.py
│   └── test_solver.py
├── test_gui/
│   ├── test_main_window.py
│   └── test_widgets.py
└── test_utils/
    ├── test_constants.py
    └── test_image_utils.py
```

### 测试示例

```python
# tests/test_core/test_solver.py
import unittest
from src.core import MinesweeperSolver, BoardAnalyzer

class TestSolver(unittest.TestCase):
    def test_solve_simple_case(self):
        # 准备测试数据
        analyzer = MockBoardAnalyzer()
        solver = MinesweeperSolver(analyzer)
        
        # 执行求解
        safe, mines = solver.solve()
        
        # 验证结果
        self.assertEqual(len(safe), 3)
        self.assertEqual(len(mines), 2)
```

## 性能优化

### 1. 图像处理优化

- 使用ROI减少处理区域
- 缓存识别结果
- 并行处理格子

### 2. 内存优化

- 及时释放大图像
- 使用生成器处理大数据
- 限制历史记录

### 3. 响应速度优化

- 异步截图
- 进度反馈
- 后台分析

## 依赖关系

```
MainWindow
  ├─> ImageProcessor
  ├─> BoardAnalyzer
  │   └─> ImageProcessor
  └─> MinesweeperSolver
      └─> BoardAnalyzer
```

## 总结

本项目采用清晰的三层架构：
1. **GUI层** - 用户交互
2. **Core层** - 业务逻辑
3. **Utils层** - 工具支持

这种设计具有以下优势：
- ✅ 易于理解和维护
- ✅ 支持功能扩展
- ✅ 便于单元测试
- ✅ 降低模块耦合
- ✅ 提高代码复用

