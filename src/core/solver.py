"""
扫雷求解器
实现扫雷游戏的逻辑推理
"""

from utils.constants import CellState


class MinesweeperSolver:
  """扫雷求解器类"""
  
  def __init__(self, board_analyzer):
    """
    初始化求解器
    
    Args:
      board_analyzer: BoardAnalyzer实例
    """
    self.board_analyzer = board_analyzer
    self.safe_cells = []
    self.mine_cells = []
    self.safe_reasons = {}  # 安全格子的推理依据
    self.mine_reasons = {}  # 地雷格子的推理依据
  
  def solve(self):
    """
    求解当前棋盘
    
    Returns:
      (safe_cells, mine_cells) 安全格子和地雷格子的列表
    """
    board = self.board_analyzer.get_board_state()
    
    if board is None:
      return [], []
    
    self.safe_cells = []
    self.mine_cells = []
    self.safe_reasons = {}
    self.mine_reasons = {}
    
    rows, cols = board.shape
    
    # 遍历所有数字格子
    for i in range(rows):
      for j in range(cols):
        if board[i, j] > 0:  # 如果是数字格子
          result = self._analyze_cell(i, j, board)
          
          # 记录安全格子及其原因
          for cell in result['safe']:
            if cell not in self.safe_reasons:
              self.safe_cells.append(cell)
              self.safe_reasons[cell] = result['reason']
          
          # 记录地雷格子及其原因
          for cell in result['mines']:
            if cell not in self.mine_reasons:
              self.mine_cells.append(cell)
              self.mine_reasons[cell] = result['reason']
    
    return self.safe_cells, self.mine_cells
  
  def _analyze_cell(self, row, col, board):
    """
    分析单个数字格子周围的情况
    
    Args:
      row: 行索引
      col: 列索引
      board: 棋盘状态
      
    Returns:
      dict包含safe、mines和reason
    """
    number = board[row, col]
    neighbors = self._get_neighbors(row, col, board.shape)
    
    unknown = []  # 未知格子
    flagged = []  # 已标记的格子
    
    for nr, nc in neighbors:
      if board[nr, nc] == CellState.UNKNOWN:
        unknown.append((nr, nc))
      elif board[nr, nc] == CellState.FLAGGED:
        flagged.append((nr, nc))
    
    result = {'safe': [], 'mines': [], 'reason': ''}
    
    # 规则1: 如果未知格子数 = 剩余雷数，所有未知格子都是雷
    remaining_mines = number - len(flagged)
    if len(unknown) == remaining_mines and remaining_mines > 0:
      result['mines'] = unknown
      result['reason'] = (
        f"位置({row+1},{col+1})数字{number}，"
        f"周围已标记{len(flagged)}个雷，"
        f"剩余{len(unknown)}个未知格子=剩余{remaining_mines}个雷，"
        f"因此这些格子必定是雷"
      )
    
    # 规则2: 如果已标记雷数 = 数字，所有未知格子都安全
    if len(flagged) == number and len(unknown) > 0:
      result['safe'] = unknown
      result['reason'] = (
        f"位置({row+1},{col+1})数字{number}，"
        f"周围已标记{len(flagged)}个雷（等于数字），"
        f"因此剩余{len(unknown)}个格子必定安全"
      )
    
    return result
  
  def _get_neighbors(self, row, col, shape):
    """
    获取相邻格子的坐标
    
    Args:
      row: 行索引
      col: 列索引
      shape: 棋盘形状 (rows, cols)
      
    Returns:
      相邻格子坐标列表
    """
    rows, cols = shape
    neighbors = []
    
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        
        nr, nc = row + dr, col + dc
        
        if 0 <= nr < rows and 0 <= nc < cols:
          neighbors.append((nr, nc))
    
    return neighbors
  
  def get_results(self):
    """
    获取求解结果
    
    Returns:
      (safe_cells, mine_cells) 元组
    """
    return self.safe_cells, self.mine_cells
  
  def get_statistics(self):
    """
    获取统计信息
    
    Returns:
      dict包含safe_count和mine_count
    """
    return {
      'safe_count': len(self.safe_cells),
      'mine_count': len(self.mine_cells),
      'has_hints': len(self.safe_cells) > 0 or len(self.mine_cells) > 0
    }
  
  def get_reasons(self):
    """
    获取推理依据
    
    Returns:
      dict包含safe_reasons和mine_reasons
    """
    return {
      'safe_reasons': self.safe_reasons,
      'mine_reasons': self.mine_reasons
    }

