"""
主窗口类
"""

from PySide6.QtWidgets import (
  QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
  QGroupBox, QMessageBox, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import time

from core.minesweeper_game import MinesweeperGame
from core.solver import MinesweeperSolver
from core.board_analyzer import BoardAnalyzer
from gui.game_board import GameBoard
from utils.constants import GUIConfig, BOARD_SIZES


class SimpleBoardAnalyzer:
  """简化的棋盘分析器（用于内置游戏）"""
  
  def __init__(self, game: MinesweeperGame):
    self.game = game
  
  def get_board_state(self):
    """获取棋盘状态"""
    return self.game.get_board_state()
  
  def get_board_info(self):
    """获取棋盘信息"""
    return {
      'rows': self.game.rows,
      'cols': self.game.cols,
      'board': self.get_board_state()
    }


class MainWindow(QMainWindow):
  """主窗口类"""
  
  def __init__(self):
    super().__init__()
    self.setWindowTitle("🎮 扫雷游戏 + AI智能提示")
    self.resize(800, 700)
    
    # 游戏数据
    self.game_board = None
    self.solver = None
    self.timer = QTimer()
    self.start_time = 0
    self.elapsed_time = 0
    
    # 难度配置
    self.difficulties = {
      '初级 (9x9)': {'rows': 9, 'cols': 9, 'mines': 10},
      '中级 (16x16)': {'rows': 16, 'cols': 16, 'mines': 40},
      '高级 (16x30)': {'rows': 16, 'cols': 30, 'mines': 99},
    }
    
    self.setup_ui()
    self.new_game()
  
  def setup_ui(self):
    """设置用户界面"""
    # 创建中心部件
    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    main_layout = QVBoxLayout()
    central_widget.setLayout(main_layout)
    
    # 标题
    title_label = QLabel("🎮 扫雷游戏 + AI智能提示")
    title_label.setFont(QFont('Arial', 20, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet("padding: 10px; color: #2c3e50;")
    main_layout.addWidget(title_label)
    
    # 控制面板
    control_layout = QHBoxLayout()
    
    # 难度选择
    difficulty_label = QLabel("难度:")
    difficulty_label.setFont(QFont('Arial', 10))
    control_layout.addWidget(difficulty_label)
    
    self.difficulty_combo = QComboBox()
    self.difficulty_combo.addItems(list(self.difficulties.keys()))
    self.difficulty_combo.setCurrentText('初级 (9x9)')
    control_layout.addWidget(self.difficulty_combo)
    
    control_layout.addSpacing(20)
    
    # 新游戏按钮
    new_game_btn = QPushButton("🎯 新游戏")
    new_game_btn.setFont(QFont('Arial', 10, QFont.Weight.Bold))
    new_game_btn.setStyleSheet("""
      QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 4px;
      }
      QPushButton:hover {
        background-color: #45a049;
      }
    """)
    new_game_btn.clicked.connect(self.new_game)
    control_layout.addWidget(new_game_btn)
    
    # AI提示按钮
    self.hint_btn = QPushButton("💡 AI提示")
    self.hint_btn.setFont(QFont('Arial', 10, QFont.Weight.Bold))
    self.hint_btn.setStyleSheet("""
      QPushButton {
        background-color: #2196F3;
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 4px;
      }
      QPushButton:hover {
        background-color: #0b7dda;
      }
      QPushButton:disabled {
        background-color: #cccccc;
      }
    """)
    self.hint_btn.clicked.connect(self.show_hint)
    control_layout.addWidget(self.hint_btn)
    
    # 清除提示按钮
    clear_hint_btn = QPushButton("🧹 清除提示")
    clear_hint_btn.setFont(QFont('Arial', 10, QFont.Weight.Bold))
    clear_hint_btn.setStyleSheet("""
      QPushButton {
        background-color: #FF9800;
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 4px;
      }
      QPushButton:hover {
        background-color: #e68900;
      }
    """)
    clear_hint_btn.clicked.connect(self.clear_hint)
    control_layout.addWidget(clear_hint_btn)
    
    control_layout.addStretch()
    
    main_layout.addLayout(control_layout)
    
    # 游戏信息栏
    info_layout = QHBoxLayout()
    
    # 地雷计数器
    self.mine_label = QLabel("💣 剩余: 10")
    self.mine_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
    self.mine_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
    info_layout.addWidget(self.mine_label)
    
    info_layout.addStretch()
    
    # 计时器
    self.timer_label = QLabel("⏱️ 时间: 0")
    self.timer_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
    self.timer_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
    info_layout.addWidget(self.timer_label)
    
    main_layout.addLayout(info_layout)
    
    # 游戏区域
    game_layout = QHBoxLayout()
    
    # 左侧 - 游戏棋盘
    left_group = QGroupBox("🎮 游戏棋盘")
    left_group.setFont(QFont('Arial', 10, QFont.Weight.Bold))
    left_layout = QVBoxLayout()
    
    # 创建游戏棋盘容器
    board_container = QWidget()
    board_container_layout = QHBoxLayout()
    board_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    board_container.setLayout(board_container_layout)
    
    self.game_board = GameBoard()
    self.game_board.cell_revealed.connect(self.on_cell_revealed)
    self.game_board.game_over_signal.connect(self.on_game_over)
    board_container_layout.addWidget(self.game_board)
    
    left_layout.addWidget(board_container)
    left_group.setLayout(left_layout)
    game_layout.addWidget(left_group, stretch=2)
    
    # 右侧 - AI提示信息
    right_group = QGroupBox("💡 AI提示信息")
    right_group.setFont(QFont('Arial', 10, QFont.Weight.Bold))
    right_layout = QVBoxLayout()
    
    self.hint_text = QLabel()
    self.hint_text.setFont(QFont('Courier New', 9))
    self.hint_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.hint_text.setWordWrap(True)
    self.hint_text.setStyleSheet("""
      QLabel {
        background-color: white;
        border: 1px solid #ccc;
        padding: 10px;
      }
    """)
    self.hint_text.setMinimumWidth(250)
    right_layout.addWidget(self.hint_text)
    
    right_group.setLayout(right_layout)
    game_layout.addWidget(right_group, stretch=1)
    
    main_layout.addLayout(game_layout)
    
    # 操作说明
    help_label = QLabel(
      "💡 提示: 左键翻开格子 | 右键标记地雷 | "
      "使用AI提示获取安全格子和地雷位置"
    )
    help_label.setFont(QFont('Arial', 9))
    help_label.setStyleSheet("background-color: #f8f8f8; padding: 8px;")
    help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(help_label)
    
    # 计时器设置
    self.timer.timeout.connect(self.update_timer)
  
  def new_game(self):
    """开始新游戏"""
    # 获取难度
    difficulty = self.difficulty_combo.currentText()
    config = self.difficulties[difficulty]
    
    # 初始化游戏棋盘
    self.game_board.init_game(
      config['rows'],
      config['cols'],
      config['mines']
    )
    
    # 重置计时器
    self.elapsed_time = 0
    self.timer.stop()
    self.update_timer()
    
    # 更新地雷计数
    self.update_mine_count()
    
    # 清除提示
    self.clear_hint()
    
    # 启用AI提示按钮
    self.hint_btn.setEnabled(True)
  
  def on_cell_revealed(self):
    """格子被翻开时"""
    # 第一次翻开时启动计时器
    if not self.timer.isActive():
      self.timer.start(1000)
      self.start_time = time.time()
    
    # 更新地雷计数
    self.update_mine_count()
  
  def update_mine_count(self):
    """更新地雷计数显示"""
    game = self.game_board.get_game()
    if game:
      remaining = game.get_remaining_mines()
      self.mine_label.setText(f"💣 剩余: {remaining}")
  
  def update_timer(self):
    """更新计时器显示"""
    if self.timer.isActive():
      self.elapsed_time = int(time.time() - self.start_time)
    self.timer_label.setText(f"⏱️ 时间: {self.elapsed_time}")
  
  def on_game_over(self, won: bool):
    """游戏结束"""
    self.timer.stop()
    self.hint_btn.setEnabled(False)
    
    if won:
      QMessageBox.information(
        self,
        "🎉 恭喜",
        f"你赢了！\n用时: {self.elapsed_time} 秒"
      )
    else:
      QMessageBox.information(
        self,
        "💥 游戏结束",
        "很遗憾，你踩到地雷了！\n"
        "点击'新游戏'重新开始"
      )
  
  def show_hint(self):
    """显示AI提示"""
    game = self.game_board.get_game()
    if not game or game.game_over or game.first_click:
      QMessageBox.warning(
        self,
        "提示",
        "请先开始游戏（翻开至少一个格子）！"
      )
      return
    
    # 创建分析器和求解器
    analyzer = SimpleBoardAnalyzer(game)
    solver = MinesweeperSolver(analyzer)
    
    # 求解
    safe_cells, mine_cells = solver.solve()
    
    # 显示提示信息
    self.display_hint_info(safe_cells, mine_cells)
    
    # 在棋盘上标记（通过改变按钮样式）
    self.highlight_hints(safe_cells, mine_cells)
  
  def display_hint_info(self, safe_cells, mine_cells):
    """显示提示信息"""
    info = "━━━━━━━━━━━━━━━\n"
    info += "  AI 提示信息\n"
    info += "━━━━━━━━━━━━━━━\n\n"
    
    info += f"📊 统计:\n"
    info += f"  安全格子: {len(safe_cells)} 个\n"
    info += f"  地雷格子: {len(mine_cells)} 个\n\n"
    
    if safe_cells:
      info += "🟢 安全格子（建议点击）:\n"
      for i, (row, col) in enumerate(safe_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(safe_cells) > 10:
        info += f"  ... 还有 {len(safe_cells)-10} 个\n"
      info += "\n"
    
    if mine_cells:
      info += "🔴 地雷格子（建议标记）:\n"
      for i, (row, col) in enumerate(mine_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(mine_cells) > 10:
        info += f"  ... 还有 {len(mine_cells)-10} 个\n"
      info += "\n"
    
    if not safe_cells and not mine_cells:
      info += "⚠️ 未找到明确的提示\n\n"
      info += "可能需要:\n"
      info += "  • 翻开更多格子\n"
      info += "  • 根据已知信息推理\n"
      info += "  • 需要一定的运气！\n"
    
    self.hint_text.setText(info)
  
  def highlight_hints(self, safe_cells, mine_cells):
    """在棋盘上高亮显示提示"""
    if not self.game_board.buttons:
      return
    
    # 高亮安全格子（绿色边框）
    for row, col in safe_cells:
      btn = self.game_board.buttons[row][col]
      if not btn.is_revealed:
        btn.setStyleSheet("""
          QPushButton {
            background-color: #90EE90;
            border: 3px solid #00ff00;
            font-weight: bold;
          }
          QPushButton:hover {
            background-color: #7FDD7F;
          }
        """)
    
    # 高亮地雷格子（红色边框）
    for row, col in mine_cells:
      btn = self.game_board.buttons[row][col]
      if not btn.is_revealed:
        btn.setStyleSheet("""
          QPushButton {
            background-color: #FFB6C1;
            border: 3px solid #ff0000;
            font-weight: bold;
          }
          QPushButton:hover {
            background-color: #FFA5B0;
          }
        """)
  
  def clear_hint(self):
    """清除提示"""
    self.hint_text.setText(
      "点击 '💡 AI提示' 按钮\n"
      "获取AI分析结果\n\n"
      "AI会告诉你:\n"
      "  🟢 哪些格子是安全的\n"
      "  🔴 哪些格子是地雷\n\n"
      "提示: 翻开的格子越多，\n"
      "AI提示越准确！"
    )
    
    # 恢复按钮样式
    if not self.game_board.buttons:
      return
    
    game = self.game_board.get_game()
    if not game:
      return
    
    for i in range(game.rows):
      for j in range(game.cols):
        cell = game.get_cell(i, j)
        self.game_board.buttons[i][j].update_display(cell, game.game_over)

