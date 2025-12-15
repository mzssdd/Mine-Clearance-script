"""
扫雷游戏棋盘界面
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QColor

from core.minesweeper_game import MinesweeperGame, Cell


class CellButton(QPushButton):
  """单个格子按钮"""
  
  # 自定义信号
  left_clicked = Signal(int, int)   # 左键点击
  right_clicked = Signal(int, int)  # 右键点击
  
  def __init__(self, row: int, col: int):
    super().__init__()
    self.row = row
    self.col = col
    self.is_revealed = False
    self.is_flagged = False
    
    # 设置样式
    self.setFixedSize(40, 40)
    self.setFont(QFont('Arial', 12, QFont.Weight.Bold))
    self._set_unrevealed_style()
    
    # 禁用右键菜单
    self.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
  
  def mousePressEvent(self, event):
    """鼠标按下事件"""
    if event.button() == Qt.MouseButton.LeftButton:
      self.left_clicked.emit(self.row, self.col)
    elif event.button() == Qt.MouseButton.RightButton:
      self.right_clicked.emit(self.row, self.col)
  
  def update_display(self, cell: Cell, game_over: bool = False):
    """
    更新显示
    
    Args:
      cell: 格子数据
      game_over: 游戏是否结束
    """
    self.is_revealed = cell.is_revealed
    self.is_flagged = cell.is_flagged
    
    if cell.is_flagged and not cell.is_revealed:
      # 显示旗帜
      self.setText('🚩')
      self._set_flagged_style()
    elif cell.is_revealed:
      if cell.is_mine:
        # 显示地雷
        self.setText('💣')
        if game_over:
          self._set_mine_style()
        else:
          self._set_revealed_style()
      elif cell.adjacent_mines == 0:
        # 空白格子
        self.setText('')
        self._set_revealed_style()
      else:
        # 显示数字
        self.setText(str(cell.adjacent_mines))
        self._set_number_style(cell.adjacent_mines)
    else:
      # 未翻开
      self.setText('')
      self._set_unrevealed_style()
  
  def _set_unrevealed_style(self):
    """未翻开的样式"""
    self.setStyleSheet("""
      QPushButton {
        background-color: #c0c0c0;
        border: 2px outset #ffffff;
        border-right-color: #808080;
        border-bottom-color: #808080;
      }
      QPushButton:hover {
        background-color: #d0d0d0;
      }
      QPushButton:pressed {
        border: 2px inset #808080;
      }
    """)
  
  def _set_revealed_style(self):
    """已翻开的样式"""
    self.setStyleSheet("""
      QPushButton {
        background-color: #e0e0e0;
        border: 1px solid #a0a0a0;
      }
    """)
  
  def _set_flagged_style(self):
    """已标记的样式"""
    self.setStyleSheet("""
      QPushButton {
        background-color: #c0c0c0;
        border: 2px outset #ffffff;
        border-right-color: #808080;
        border-bottom-color: #808080;
        font-size: 20px;
      }
    """)
  
  def _set_mine_style(self):
    """地雷的样式（游戏结束）"""
    self.setStyleSheet("""
      QPushButton {
        background-color: #ff6666;
        border: 1px solid #ff0000;
        font-size: 20px;
      }
    """)
  
  def _set_number_style(self, number: int):
    """数字的样式"""
    # 不同数字不同颜色
    colors = {
      1: '#0000ff',  # 蓝色
      2: '#008000',  # 绿色
      3: '#ff0000',  # 红色
      4: '#000080',  # 深蓝
      5: '#800000',  # 棕色
      6: '#008080',  # 青色
      7: '#000000',  # 黑色
      8: '#808080',  # 灰色
    }
    
    color = colors.get(number, '#000000')
    self.setStyleSheet(f"""
      QPushButton {{
        background-color: #e0e0e0;
        border: 1px solid #a0a0a0;
        color: {color};
        font-weight: bold;
      }}
    """)


class GameBoard(QWidget):
  """游戏棋盘组件"""
  
  # 自定义信号
  cell_revealed = Signal()       # 格子被翻开
  game_over_signal = Signal(bool)  # 游戏结束（True=胜利，False=失败）
  
  def __init__(self, parent=None):
    super().__init__(parent)
    self.game = None
    self.buttons = []
    self.layout = QGridLayout()
    self.layout.setSpacing(1)
    self.layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.layout)
  
  def init_game(self, rows: int, cols: int, mines: int):
    """
    初始化游戏
    
    Args:
      rows: 行数
      cols: 列数
      mines: 地雷数量
    """
    # 清除旧的按钮
    self._clear_board()
    
    # 创建新游戏
    self.game = MinesweeperGame(rows, cols, mines)
    
    # 创建格子按钮
    self.buttons = []
    for i in range(rows):
      row_buttons = []
      for j in range(cols):
        btn = CellButton(i, j)
        btn.left_clicked.connect(self._on_cell_left_click)
        btn.right_clicked.connect(self._on_cell_right_click)
        self.layout.addWidget(btn, i, j)
        row_buttons.append(btn)
      self.buttons.append(row_buttons)
    
    # 调整大小
    self.adjustSize()
  
  def _clear_board(self):
    """清空棋盘"""
    while self.layout.count():
      item = self.layout.takeAt(0)
      if item.widget():
        item.widget().deleteLater()
    self.buttons = []
  
  def _on_cell_left_click(self, row: int, col: int):
    """左键点击格子"""
    if self.game is None or self.game.game_over:
      return
    
    success = self.game.reveal(row, col)
    self._update_board()
    
    if not success:
      # 踩雷了
      self.game_over_signal.emit(False)
    elif self.game.game_won:
      # 获胜了
      self.game_over_signal.emit(True)
    else:
      self.cell_revealed.emit()
  
  def _on_cell_right_click(self, row: int, col: int):
    """右键点击格子（标记/取消标记）"""
    if self.game is None or self.game.game_over:
      return
    
    self.game.toggle_flag(row, col)
    self._update_board()
  
  def _update_board(self):
    """更新棋盘显示"""
    if self.game is None:
      return
    
    for i in range(self.game.rows):
      for j in range(self.game.cols):
        cell = self.game.get_cell(i, j)
        self.buttons[i][j].update_display(cell, self.game.game_over)
  
  def get_game(self) -> MinesweeperGame:
    """获取游戏实例"""
    return self.game
  
  def reset_game(self):
    """重置游戏"""
    if self.game is None:
      return
    
    rows, cols, mines = self.game.rows, self.game.cols, self.game.total_mines
    self.init_game(rows, cols, mines)


