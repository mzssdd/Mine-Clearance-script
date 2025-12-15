"""
扫雷游戏核心逻辑
"""

import random
from typing import Tuple, List, Set


class Cell:
  """单个格子"""
  
  def __init__(self):
    self.is_mine = False        # 是否是地雷
    self.is_revealed = False    # 是否已翻开
    self.is_flagged = False     # 是否已标记
    self.adjacent_mines = 0     # 周围地雷数
    self.row = 0
    self.col = 0


class MinesweeperGame:
  """扫雷游戏类"""
  
  def __init__(self, rows: int = 9, cols: int = 9, mines: int = 10):
    """
    初始化游戏
    
    Args:
      rows: 行数
      cols: 列数
      mines: 地雷数量
    """
    self.rows = rows
    self.cols = cols
    self.total_mines = mines
    self.board: List[List[Cell]] = []
    self.game_over = False
    self.game_won = False
    self.first_click = True
    self.revealed_count = 0
    self.flag_count = 0
    
    self._init_board()
  
  def _init_board(self):
    """初始化棋盘"""
    self.board = []
    for i in range(self.rows):
      row = []
      for j in range(self.cols):
        cell = Cell()
        cell.row = i
        cell.col = j
        row.append(cell)
      self.board.append(row)
  
  def start_game(self, first_row: int, first_col: int):
    """
    开始游戏（第一次点击后生成地雷）
    
    Args:
      first_row: 第一次点击的行
      first_col: 第一次点击的列
    """
    if not self.first_click:
      return
    
    self.first_click = False
    self._place_mines(first_row, first_col)
    self._calculate_adjacent_mines()
  
  def _place_mines(self, safe_row: int, safe_col: int):
    """
    放置地雷（确保第一次点击的位置及其周围是安全的）
    
    Args:
      safe_row: 安全区域的行
      safe_col: 安全区域的列
    """
    # 计算安全区域（第一次点击及其周围8格）
    safe_cells = set()
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        r, c = safe_row + dr, safe_col + dc
        if 0 <= r < self.rows and 0 <= c < self.cols:
          safe_cells.add((r, c))
    
    # 随机放置地雷
    placed = 0
    while placed < self.total_mines:
      row = random.randint(0, self.rows - 1)
      col = random.randint(0, self.cols - 1)
      
      if (row, col) not in safe_cells and not self.board[row][col].is_mine:
        self.board[row][col].is_mine = True
        placed += 1
  
  def _calculate_adjacent_mines(self):
    """计算每个格子周围的地雷数"""
    for i in range(self.rows):
      for j in range(self.cols):
        if not self.board[i][j].is_mine:
          count = 0
          for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
              if di == 0 and dj == 0:
                continue
              ni, nj = i + di, j + dj
              if 0 <= ni < self.rows and 0 <= nj < self.cols:
                if self.board[ni][nj].is_mine:
                  count += 1
          self.board[i][j].adjacent_mines = count
  
  def reveal(self, row: int, col: int) -> bool:
    """
    翻开一个格子
    
    Args:
      row: 行索引
      col: 列索引
      
    Returns:
      True表示成功，False表示踩雷
    """
    if self.game_over:
      return False
    
    # 第一次点击时生成地雷
    if self.first_click:
      self.start_game(row, col)
    
    cell = self.board[row][col]
    
    # 已翻开或已标记的格子不能翻开
    if cell.is_revealed or cell.is_flagged:
      return True
    
    # 踩雷了
    if cell.is_mine:
      cell.is_revealed = True
      self.game_over = True
      self._reveal_all_mines()
      return False
    
    # 翻开格子
    self._reveal_cell(row, col)
    
    # 检查是否获胜
    self._check_win()
    
    return True
  
  def _reveal_cell(self, row: int, col: int):
    """
    递归翻开格子（如果是空白格则翻开周围）
    
    Args:
      row: 行索引
      col: 列索引
    """
    if not (0 <= row < self.rows and 0 <= col < self.cols):
      return
    
    cell = self.board[row][col]
    
    if cell.is_revealed or cell.is_flagged or cell.is_mine:
      return
    
    cell.is_revealed = True
    self.revealed_count += 1
    
    # 如果是空白格（周围没有地雷），递归翻开周围
    if cell.adjacent_mines == 0:
      for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
          if di == 0 and dj == 0:
            continue
          self._reveal_cell(row + di, col + dj)
  
  def toggle_flag(self, row: int, col: int) -> bool:
    """
    切换标记状态
    
    Args:
      row: 行索引
      col: 列索引
      
    Returns:
      True表示成功
    """
    if self.game_over:
      return False
    
    cell = self.board[row][col]
    
    # 已翻开的格子不能标记
    if cell.is_revealed:
      return False
    
    if cell.is_flagged:
      cell.is_flagged = False
      self.flag_count -= 1
    else:
      # 限制标记数量不超过地雷总数
      if self.flag_count < self.total_mines:
        cell.is_flagged = True
        self.flag_count += 1
    
    return True
  
  def _reveal_all_mines(self):
    """游戏结束时显示所有地雷"""
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i][j].is_mine:
          self.board[i][j].is_revealed = True
  
  def _check_win(self):
    """检查是否获胜"""
    # 所有非地雷格子都已翻开
    total_cells = self.rows * self.cols
    if self.revealed_count == total_cells - self.total_mines:
      self.game_won = True
      self.game_over = True
  
  def get_cell(self, row: int, col: int) -> Cell:
    """获取指定格子"""
    return self.board[row][col]
  
  def get_board_state(self):
    """
    获取棋盘状态（用于AI分析）
    
    Returns:
      二维数组，-1=未翻开，0=空白，1-8=数字，-2=已标记
    """
    import numpy as np
    state = np.zeros((self.rows, self.cols), dtype=int)
    
    for i in range(self.rows):
      for j in range(self.cols):
        cell = self.board[i][j]
        if cell.is_flagged:
          state[i][j] = -2
        elif not cell.is_revealed:
          state[i][j] = -1
        elif cell.is_mine:
          state[i][j] = -1  # 地雷显示为未知（游戏中不会出现）
        else:
          state[i][j] = cell.adjacent_mines
    
    return state
  
  def reset(self):
    """重置游戏"""
    self.game_over = False
    self.game_won = False
    self.first_click = True
    self.revealed_count = 0
    self.flag_count = 0
    self._init_board()
  
  def get_remaining_mines(self) -> int:
    """获取剩余地雷数（总数-标记数）"""
    return self.total_mines - self.flag_count


