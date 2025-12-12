"""
自定义GUI组件
"""

from PySide6.QtWidgets import (
  QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
  QComboBox, QLineEdit, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont


class ControlPanel(QWidget):
  """控制面板组件"""
  
  size_changed = Signal(str)
  capture_clicked = Signal()
  analyze_clicked = Signal()
  save_clicked = Signal()
  
  def __init__(self, parent=None):
    super().__init__(parent)
    self._create_widgets()
  
  def _create_widgets(self):
    """创建控件"""
    layout = QHBoxLayout()
    layout.setContentsMargins(10, 10, 10, 10)
    
    # 棋盘大小设置
    size_label = QLabel("棋盘大小:")
    size_label.setFont(QFont("Arial", 10))
    layout.addWidget(size_label)
    
    self.size_combo = QComboBox()
    self.size_combo.addItems(["9x9", "16x16", "16x30", "自定义"])
    self.size_combo.setCurrentText("9x9")
    self.size_combo.setFixedWidth(100)
    self.size_combo.currentTextChanged.connect(self.size_changed.emit)
    layout.addWidget(self.size_combo)
    
    # 自定义大小输入
    self.custom_frame = QWidget()
    custom_layout = QHBoxLayout()
    custom_layout.setContentsMargins(0, 0, 0, 0)
    
    custom_layout.addWidget(QLabel("行:"))
    self.rows_entry = QLineEdit("9")
    self.rows_entry.setFixedWidth(50)
    custom_layout.addWidget(self.rows_entry)
    
    custom_layout.addWidget(QLabel("列:"))
    self.cols_entry = QLineEdit("9")
    self.cols_entry.setFixedWidth(50)
    custom_layout.addWidget(self.cols_entry)
    
    self.custom_frame.setLayout(custom_layout)
    self.custom_frame.hide()
    layout.addWidget(self.custom_frame)
    
    layout.addSpacing(20)
    
    # 按钮区域
    self.capture_btn = QPushButton("📸 捕获屏幕 (5秒后)")
    self.capture_btn.setStyleSheet("""
      QPushButton {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 5px 15px;
        border: none;
        border-radius: 3px;
      }
      QPushButton:hover {
        background-color: #45a049;
      }
    """)
    self.capture_btn.clicked.connect(self.capture_clicked.emit)
    layout.addWidget(self.capture_btn)
    
    self.analyze_btn = QPushButton("🔍 分析并提示")
    self.analyze_btn.setStyleSheet("""
      QPushButton {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
        padding: 5px 15px;
        border: none;
        border-radius: 3px;
      }
      QPushButton:hover {
        background-color: #0b7dda;
      }
      QPushButton:disabled {
        background-color: #cccccc;
      }
    """)
    self.analyze_btn.setEnabled(False)
    self.analyze_btn.clicked.connect(self.analyze_clicked.emit)
    layout.addWidget(self.analyze_btn)
    
    self.save_btn = QPushButton("💾 保存图片")
    self.save_btn.setStyleSheet("""
      QPushButton {
        background-color: #FF9800;
        color: white;
        font-weight: bold;
        padding: 5px 15px;
        border: none;
        border-radius: 3px;
      }
      QPushButton:hover {
        background-color: #e68900;
      }
      QPushButton:disabled {
        background-color: #cccccc;
      }
    """)
    self.save_btn.setEnabled(False)
    self.save_btn.clicked.connect(self.save_clicked.emit)
    layout.addWidget(self.save_btn)
    
    layout.addStretch()
    self.setLayout(layout)
  
  def show_custom_inputs(self, show=True):
    """显示或隐藏自定义输入"""
    self.custom_frame.setVisible(show)
  
  def get_custom_size(self):
    """获取自定义大小"""
    try:
      rows = int(self.rows_entry.text())
      cols = int(self.cols_entry.text())
      return rows, cols
    except ValueError:
      return None, None
  
  def enable_analyze(self, enabled=True):
    """启用/禁用分析按钮"""
    self.analyze_btn.setEnabled(enabled)
  
  def enable_save(self, enabled=True):
    """启用/禁用保存按钮"""
    self.save_btn.setEnabled(enabled)
  
  def enable_capture(self, enabled=True):
    """启用/禁用捕获按钮"""
    self.capture_btn.setEnabled(enabled)


class ImageCanvas(QLabel):
  """图像显示画布"""
  
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setStyleSheet("background-color: white; border: 1px solid #ccc;")
    self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.setScaledContents(False)
  
  def display_image(self, pil_image, fit_to_canvas=True):
    """
    显示PIL图像
    
    Args:
      pil_image: PIL Image对象
      fit_to_canvas: 是否调整大小适应画布
    """
    from utils.image_utils import resize_to_fit, pil_to_qpixmap
    
    if fit_to_canvas:
      canvas_width = self.width()
      canvas_height = self.height()
      if canvas_width > 0 and canvas_height > 0:
        pil_image = resize_to_fit(pil_image, canvas_width, canvas_height)
    
    pixmap = pil_to_qpixmap(pil_image)
    self.setPixmap(pixmap)


class InfoText(QTextEdit):
  """信息显示文本框"""
  
  def __init__(self, parent=None, height=None):
    super().__init__(parent)
    self.setFont(QFont("Courier New", 9))
    self.setReadOnly(True)
    if height:
      self.setMinimumHeight(height * 20)
  
  def set_text(self, text):
    """设置文本内容"""
    self.setPlainText(text)
  
  def append_text(self, text):
    """追加文本"""
    self.append(text)

