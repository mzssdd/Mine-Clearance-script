"""
主窗口类
"""

from PySide6.QtWidgets import (
  QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
  QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
import time

from core import BoardAnalyzer, ImageProcessor, MinesweeperSolver
from utils.constants import GUIConfig, Messages, FileConfig, BOARD_SIZES
from utils.image_utils import numpy_to_pil
from gui.widgets import ControlPanel, ImageCanvas, InfoText


class CaptureThread(QThread):
  """截屏线程"""
  
  countdown_signal = Signal(int)
  capture_signal = Signal()
  
  def __init__(self, delay):
    super().__init__()
    self.delay = delay
  
  def run(self):
    """线程运行"""
    for i in range(self.delay, 0, -1):
      self.countdown_signal.emit(i)
      time.sleep(1)
    
    self.capture_signal.emit()


class MainWindow(QMainWindow):
  """主窗口类"""
  
  def __init__(self):
    super().__init__()
    self.setWindowTitle(GUIConfig.WINDOW_TITLE)
    
    # 解析窗口大小
    width, height = map(int, GUIConfig.WINDOW_SIZE.split('x'))
    self.resize(width, height)
    
    # 初始化核心组件
    self.image_processor = ImageProcessor()
    self.board_analyzer = BoardAnalyzer(self.image_processor)
    self.solver = MinesweeperSolver(self.board_analyzer)
    
    # 数据
    self.rows = 9
    self.cols = 9
    
    self.setup_ui()
  
  def setup_ui(self):
    """设置用户界面"""
    # 创建中心部件
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    main_layout = QVBoxLayout()
    central_widget.setLayout(main_layout)
    
    # 标题
    title_label = QLabel(f"🎮 {GUIConfig.WINDOW_TITLE}")
    title_label.setFont(QFont(GUIConfig.TITLE_FONT[0], GUIConfig.TITLE_FONT[1]))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("padding: 10px;")
    main_layout.addWidget(title_label)
    
    # 控制面板
    self.control_panel = ControlPanel()
    self.control_panel.size_changed.connect(self.on_size_changed)
    self.control_panel.capture_clicked.connect(self.start_capture)
    self.control_panel.analyze_clicked.connect(self.analyze_board)
    self.control_panel.save_clicked.connect(self.save_image)
    main_layout.addWidget(self.control_panel)
    
    # 状态栏
    self.status_label = QLabel(Messages.READY)
    self.status_label.setFont(QFont(GUIConfig.LABEL_FONT[0], GUIConfig.LABEL_FONT[1]))
    self.status_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
    main_layout.addWidget(self.status_label)
    
    # 主显示区域
    display_layout = QHBoxLayout()
    
    # 左侧 - 原始图像
    left_group = QGroupBox("📷 捕获的图像")
    left_group.setFont(QFont(GUIConfig.BUTTON_FONT[0], GUIConfig.BUTTON_FONT[1]))
    left_layout = QVBoxLayout()
    self.original_canvas = ImageCanvas()
    self.original_canvas.setMinimumSize(400, 400)
    left_layout.addWidget(self.original_canvas)
    left_group.setLayout(left_layout)
    display_layout.addWidget(left_group)
    
    # 右侧 - 提示图像和信息
    right_layout = QVBoxLayout()
    
    # 提示图像
    hint_group = QGroupBox("💡 游戏提示")
    hint_group.setFont(QFont(GUIConfig.BUTTON_FONT[0], GUIConfig.BUTTON_FONT[1]))
    hint_layout = QVBoxLayout()
    self.hint_canvas = ImageCanvas()
    self.hint_canvas.setMinimumSize(400, 300)
    hint_layout.addWidget(self.hint_canvas)
    hint_group.setLayout(hint_layout)
    right_layout.addWidget(hint_group)
    
    # 提示信息
    info_group = QGroupBox("ℹ️ 提示信息")
    info_group.setFont(QFont(GUIConfig.BUTTON_FONT[0], GUIConfig.BUTTON_FONT[1]))
    info_layout = QVBoxLayout()
    self.info_text = InfoText(height=10)
    info_layout.addWidget(self.info_text)
    info_group.setLayout(info_layout)
    right_layout.addWidget(info_group)
    
    display_layout.addLayout(right_layout)
    main_layout.addLayout(display_layout)
    
    # 图例
    legend_label = QLabel("🟢 绿色边框 = 安全格子(可点击)    🔴 红色边框 = 地雷格子(需标记)")
    legend_label.setFont(QFont(GUIConfig.LABEL_FONT[0], GUIConfig.LABEL_FONT[1]))
    legend_label.setStyleSheet("background-color: #f8f8f8; padding: 5px;")
    legend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(legend_label)
  
  def on_size_changed(self, size):
    """棋盘大小改变时"""
    if size == "自定义":
      self.control_panel.show_custom_inputs(True)
    else:
      self.control_panel.show_custom_inputs(False)
      if size == "9x9":
        self.rows, self.cols = BOARD_SIZES['BEGINNER']
      elif size == "16x16":
        self.rows, self.cols = BOARD_SIZES['INTERMEDIATE']
      elif size == "16x30":
        self.rows, self.cols = BOARD_SIZES['EXPERT']
  
  def start_capture(self):
    """开始捕获屏幕"""
    self.update_status(f"⏱️ {GUIConfig.CAPTURE_DELAY}秒后将捕获屏幕，请切换到扫雷游戏窗口...")
    self.control_panel.enable_capture(False)
    
    # 创建并启动截屏线程
    self.capture_thread = CaptureThread(GUIConfig.CAPTURE_DELAY)
    self.capture_thread.countdown_signal.connect(self.on_countdown)
    self.capture_thread.capture_signal.connect(self.capture_and_display)
    self.capture_thread.start()
  
  def on_countdown(self, seconds):
    """倒计时更新"""
    self.update_status(Messages.CAPTURING.format(seconds))
  
  def capture_and_display(self):
    """捕获并显示屏幕"""
    try:
      # 捕获屏幕
      screenshot = self.image_processor.capture_screenshot()
      
      # 检测棋盘区域
      self.image_processor.detect_board(screenshot)
      
      # 显示原始图像
      img = numpy_to_pil(screenshot)
      self.original_canvas.display_image(img)
      
      self.update_status(Messages.CAPTURE_SUCCESS)
      self.control_panel.enable_capture(True)
      self.control_panel.enable_analyze(True)
      
    except Exception as e:
      QMessageBox.critical(self, "错误", Messages.ERROR_CAPTURE.format(str(e)))
      self.control_panel.enable_capture(True)
  
  def analyze_board(self):
    """分析棋盘并生成提示"""
    if self.image_processor.screenshot is None:
      QMessageBox.warning(self, "警告", Messages.WARNING_NO_SCREENSHOT)
      return
    
    try:
      self.update_status(Messages.ANALYZING)
      
      # 获取棋盘大小
      if self.control_panel.size_combo.currentText() == "自定义":
        rows, cols = self.control_panel.get_custom_size()
        if rows is None or cols is None:
          QMessageBox.critical(self, "错误", "请输入有效的行列数！")
          return
        self.rows, self.cols = rows, cols
      
      # 设置棋盘大小
      self.board_analyzer.set_board_size(self.rows, self.cols)
      
      # 分析棋盘
      self.board_analyzer.analyze()
      
      # 求解
      safe_cells, mine_cells = self.solver.solve()
      
      # 生成提示图像
      hint_image = self.image_processor.create_hint_overlay(
        self.image_processor.screenshot,
        safe_cells,
        mine_cells,
        self.image_processor.board_region,
        self.board_analyzer.get_cell_size()
      )
      
      # 显示提示图像
      self.hint_canvas.display_image(hint_image)
      
      # 显示提示信息
      self.display_hint_info(safe_cells, mine_cells)
      
      self.control_panel.enable_save(True)
      self.update_status(Messages.ANALYSIS_COMPLETE.format(len(safe_cells), len(mine_cells)))
      
    except Exception as e:
      QMessageBox.critical(self, "错误", Messages.ERROR_ANALYZE.format(str(e)))
      import traceback
      traceback.print_exc()
  
  def display_hint_info(self, safe_cells, mine_cells):
    """显示提示信息"""
    info = f"{'='*50}\n"
    info += f"  扫雷提示信息\n"
    info += f"{'='*50}\n\n"
    
    info += f"📊 统计:\n"
    info += f"  • 棋盘大小: {self.rows} x {self.cols}\n"
    info += f"  • 安全格子: {len(safe_cells)} 个\n"
    info += f"  • 地雷格子: {len(mine_cells)} 个\n\n"
    
    if safe_cells:
      info += f"🟢 安全格子（建议点击）:\n"
      for i, (row, col) in enumerate(safe_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(safe_cells) > 10:
        info += f"  ... 还有 {len(safe_cells)-10} 个\n"
      info += "\n"
    
    if mine_cells:
      info += f"🔴 地雷格子（建议标记）:\n"
      for i, (row, col) in enumerate(mine_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(mine_cells) > 10:
        info += f"  ... 还有 {len(mine_cells)-10} 个\n"
      info += "\n"
    
    if not safe_cells and not mine_cells:
      info += Messages.NO_HINTS + "\n"
      info += "可能需要:\n"
      info += "  • 翻开更多格子\n"
      info += "  • 检查棋盘大小设置\n"
      info += "  • 重新捕获清晰的图像\n"
    
    self.info_text.set_text(info)
  
  def save_image(self):
    """保存提示图像"""
    if self.image_processor.screenshot is None:
      QMessageBox.warning(self, "警告", Messages.WARNING_NO_IMAGE)
      return
    
    try:
      filename, _ = QFileDialog.getSaveFileName(
        self,
        "保存图片",
        FileConfig.DEFAULT_FILENAME,
        "PNG文件 (*.png);;所有文件 (*.*)"
      )
      
      if filename:
        safe_cells, mine_cells = self.solver.get_results()
        hint_image = self.image_processor.create_hint_overlay(
          self.image_processor.screenshot,
          safe_cells,
          mine_cells,
          self.image_processor.board_region,
          self.board_analyzer.get_cell_size()
        )
        hint_image.save(filename)
        QMessageBox.information(self, "成功", Messages.SUCCESS_SAVE.format(filename))
    
    except Exception as e:
      QMessageBox.critical(self, "错误", Messages.ERROR_SAVE.format(str(e)))
  
  def update_status(self, message):
    """更新状态栏"""
    self.status_label.setText(message)

