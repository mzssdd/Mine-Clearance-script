"""
主窗口类
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
import time

from core import BoardAnalyzer, ImageProcessor, MinesweeperSolver
from utils.constants import GUIConfig, Messages, FileConfig, BOARD_SIZES
from utils.image_utils import numpy_to_pil
from gui.widgets import ControlPanel, ImageCanvas, InfoText


class MainWindow:
  """主窗口类"""
  
  def __init__(self, root):
    self.root = root
    self.root.title(GUIConfig.WINDOW_TITLE)
    self.root.geometry(GUIConfig.WINDOW_SIZE)
    
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
    # 标题
    title_label = tk.Label(
      self.root,
      text=f"🎮 {GUIConfig.WINDOW_TITLE}",
      font=GUIConfig.TITLE_FONT,
      pady=10
    )
    title_label.pack()
    
    # 控制面板
    self.control_panel = ControlPanel(
      self.root,
      on_size_change=self.on_size_changed,
      on_capture=self.start_capture,
      on_analyze=self.analyze_board,
      on_save=self.save_image
    )
    self.control_panel.pack()
    
    # 状态栏
    self.status_label = tk.Label(
      self.root,
      text=Messages.READY,
      font=GUIConfig.LABEL_FONT,
      bg="#f0f0f0",
      pady=5
    )
    self.status_label.pack(fill=tk.X)
    
    # 主显示区域
    display_frame = tk.Frame(self.root)
    display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 左侧 - 原始图像
    left_frame = tk.LabelFrame(
      display_frame,
      text="📷 捕获的图像",
      font=GUIConfig.BUTTON_FONT
    )
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    self.original_canvas = ImageCanvas(left_frame)
    self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 右侧 - 提示图像和信息
    right_frame = tk.Frame(display_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    # 提示图像
    hint_frame = tk.LabelFrame(
      right_frame,
      text="💡 游戏提示",
      font=GUIConfig.BUTTON_FONT
    )
    hint_frame.pack(fill=tk.BOTH, expand=True)
    
    self.hint_canvas = ImageCanvas(hint_frame)
    self.hint_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 提示信息
    info_frame = tk.LabelFrame(
      right_frame,
      text="ℹ️ 提示信息",
      font=GUIConfig.BUTTON_FONT
    )
    info_frame.pack(fill=tk.BOTH, padx=0, pady=5)
    
    self.info_text = InfoText(info_frame, height=10)
    self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 图例
    legend_frame = tk.Frame(self.root, bg="#f8f8f8", pady=5)
    legend_frame.pack(fill=tk.X)
    
    tk.Label(
      legend_frame,
      text="🟢 绿色边框 = 安全格子(可点击)    🔴 红色边框 = 地雷格子(需标记)",
      font=GUIConfig.LABEL_FONT,
      bg="#f8f8f8"
    ).pack()
  
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
    
    # 在新线程中延迟捕获
    Thread(target=self.capture_screen_delayed, daemon=True).start()
  
  def capture_screen_delayed(self):
    """延迟捕获屏幕"""
    for i in range(GUIConfig.CAPTURE_DELAY, 0, -1):
      self.root.after(0, self.update_status, Messages.CAPTURING.format(i))
      time.sleep(1)
    
    # 捕获屏幕
    self.root.after(0, self.capture_and_display)
  
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
      messagebox.showerror("错误", Messages.ERROR_CAPTURE.format(str(e)))
      self.control_panel.enable_capture(True)
  
  def analyze_board(self):
    """分析棋盘并生成提示"""
    if self.image_processor.screenshot is None:
      messagebox.showwarning("警告", Messages.WARNING_NO_SCREENSHOT)
      return
    
    try:
      self.update_status(Messages.ANALYZING)
      
      # 获取棋盘大小
      if self.control_panel.size_var.get() == "自定义":
        rows, cols = self.control_panel.get_custom_size()
        if rows is None or cols is None:
          messagebox.showerror("错误", "请输入有效的行列数！")
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
      messagebox.showerror("错误", Messages.ERROR_ANALYZE.format(str(e)))
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
      messagebox.showwarning("警告", Messages.WARNING_NO_IMAGE)
      return
    
    try:
      filename = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=FileConfig.FILE_TYPES,
        initialfile=FileConfig.DEFAULT_FILENAME
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
        messagebox.showinfo("成功", Messages.SUCCESS_SAVE.format(filename))
    
    except Exception as e:
      messagebox.showerror("错误", Messages.ERROR_SAVE.format(str(e)))
  
  def update_status(self, message):
    """更新状态栏"""
    self.status_label.config(text=message)

