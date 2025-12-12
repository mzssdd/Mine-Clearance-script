"""
自定义GUI组件
"""

import tkinter as tk
from tkinter import ttk


class ControlPanel(tk.Frame):
  """控制面板组件"""
  
  def __init__(self, parent, on_size_change, on_capture, on_analyze, on_save):
    super().__init__(parent, pady=10)
    
    self.on_size_change = on_size_change
    self.on_capture = on_capture
    self.on_analyze = on_analyze
    self.on_save = on_save
    
    self._create_widgets()
  
  def _create_widgets(self):
    """创建控件"""
    # 棋盘大小设置
    size_frame = tk.Frame(self)
    size_frame.pack(side=tk.LEFT, padx=10)
    
    tk.Label(size_frame, text="棋盘大小:", font=("Arial", 10)).pack(side=tk.LEFT)
    
    self.size_var = tk.StringVar(value="9x9")
    self.size_combo = ttk.Combobox(
      size_frame,
      textvariable=self.size_var,
      values=["9x9", "16x16", "16x30", "自定义"],
      width=10,
      state="readonly"
    )
    self.size_combo.pack(side=tk.LEFT, padx=5)
    self.size_combo.bind("<<ComboboxSelected>>", lambda e: self.on_size_change(self.size_var.get()))
    
    # 自定义大小输入
    self.custom_frame = tk.Frame(self)
    
    tk.Label(self.custom_frame, text="行:").pack(side=tk.LEFT)
    self.rows_entry = tk.Entry(self.custom_frame, width=5)
    self.rows_entry.pack(side=tk.LEFT, padx=2)
    self.rows_entry.insert(0, "9")
    
    tk.Label(self.custom_frame, text="列:").pack(side=tk.LEFT)
    self.cols_entry = tk.Entry(self.custom_frame, width=5)
    self.cols_entry.pack(side=tk.LEFT, padx=2)
    self.cols_entry.insert(0, "9")
    
    # 按钮区域
    btn_frame = tk.Frame(self)
    btn_frame.pack(side=tk.LEFT, padx=20)
    
    self.capture_btn = tk.Button(
      btn_frame,
      text="📸 捕获屏幕 (5秒后)",
      command=self.on_capture,
      bg="#4CAF50",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5
    )
    self.capture_btn.pack(side=tk.LEFT, padx=5)
    
    self.analyze_btn = tk.Button(
      btn_frame,
      text="🔍 分析并提示",
      command=self.on_analyze,
      bg="#2196F3",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5,
      state=tk.DISABLED
    )
    self.analyze_btn.pack(side=tk.LEFT, padx=5)
    
    self.save_btn = tk.Button(
      btn_frame,
      text="💾 保存图片",
      command=self.on_save,
      bg="#FF9800",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5,
      state=tk.DISABLED
    )
    self.save_btn.pack(side=tk.LEFT, padx=5)
  
  def show_custom_inputs(self, show=True):
    """显示或隐藏自定义输入"""
    if show:
      self.custom_frame.pack(side=tk.LEFT, padx=5)
    else:
      self.custom_frame.pack_forget()
  
  def get_custom_size(self):
    """获取自定义大小"""
    try:
      rows = int(self.rows_entry.get())
      cols = int(self.cols_entry.get())
      return rows, cols
    except ValueError:
      return None, None
  
  def enable_analyze(self, enabled=True):
    """启用/禁用分析按钮"""
    self.analyze_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
  
  def enable_save(self, enabled=True):
    """启用/禁用保存按钮"""
    self.save_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)
  
  def enable_capture(self, enabled=True):
    """启用/禁用捕获按钮"""
    self.capture_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)


class ImageCanvas(tk.Canvas):
  """图像显示画布"""
  
  def __init__(self, parent, **kwargs):
    super().__init__(parent, bg="white", **kwargs)
    self.photo = None
  
  def display_image(self, pil_image, fit_to_canvas=True):
    """
    显示PIL图像
    
    Args:
      pil_image: PIL Image对象
      fit_to_canvas: 是否调整大小适应画布
    """
    from utils.image_utils import resize_to_fit, create_photo_image
    
    if fit_to_canvas:
      self.update()
      canvas_width = self.winfo_width()
      canvas_height = self.winfo_height()
      pil_image = resize_to_fit(pil_image, canvas_width, canvas_height)
    
    self.photo = create_photo_image(pil_image)
    self.delete("all")
    
    canvas_width = self.winfo_width()
    canvas_height = self.winfo_height()
    
    self.create_image(
      canvas_width // 2,
      canvas_height // 2,
      image=self.photo,
      anchor=tk.CENTER
    )


class InfoText(tk.Text):
  """信息显示文本框"""
  
  def __init__(self, parent, **kwargs):
    super().__init__(
      parent,
      font=("Courier New", 9),
      wrap=tk.WORD,
      **kwargs
    )
    
    # 添加滚动条
    scrollbar = tk.Scrollbar(self)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=self.yview)
  
  def set_text(self, text):
    """设置文本内容"""
    self.delete(1.0, tk.END)
    self.insert(1.0, text)
  
  def append_text(self, text):
    """追加文本"""
    self.insert(tk.END, text)

