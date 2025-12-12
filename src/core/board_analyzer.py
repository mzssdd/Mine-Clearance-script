"""
棋盘分析器
负责分析棋盘状态
"""

import numpy as np

from utils.image_utils import get_cell_image


class BoardAnalyzer:
  """棋盘分析器类"""
  
  def __init__(self, image_processor):
    """
    初始化分析器
    
    Args:
      image_processor: ImageProcessor实例
    """
    self.image_processor = image_processor
    self.board = None
    self.rows = 9
    self.cols = 9
    self.cell_size = 0
  
  def set_board_size(self, rows, cols):
    """
    设置棋盘大小
    
    Args:
      rows: 行数
      cols: 列数
    """
    self.rows = rows
    self.cols = cols
  
  def analyze(self):
    """
    分析棋盘状态
    
    Returns:
      numpy数组，表示棋盘状态
    """
    board_image = self.image_processor.get_board_image()
    
    if board_image is None:
      return None
    
    h, w = board_image.shape[:2]
    self.cell_size = min(w // self.cols, h // self.rows)
    
    # 创建棋盘矩阵
    self.board = np.zeros((self.rows, self.cols), dtype=int)
    
    # 识别每个格子
    for i in range(self.rows):
      for j in range(self.cols):
        cell = get_cell_image(board_image, i, j, self.cell_size)
        self.board[i, j] = self.image_processor.recognize_cell(cell)
    
    return self.board
  
  def get_board_state(self):
    """
    获取当前棋盘状态
    
    Returns:
      numpy数组
    """
    return self.board
  
  def get_cell_size(self):
    """
    获取格子大小
    
    Returns:
      格子大小（像素）
    """
    return self.cell_size
  
  def get_board_info(self):
    """
    获取棋盘信息
    
    Returns:
      dict包含rows, cols, cell_size
    """
    return {
      'rows': self.rows,
      'cols': self.cols,
      'cell_size': self.cell_size,
      'board': self.board
    }

