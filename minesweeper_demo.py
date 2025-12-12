"""
扫雷辅助工具 - 演示版本
使用模拟的扫雷棋盘进行演示
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class MinesweeperDemo:
  def __init__(self, rows=9, cols=9, mines=10):
    self.rows = rows
    self.cols = cols
    self.mines = mines
    self.board = None
    self.revealed = None
    self.mine_positions = set()
    
  def create_board(self):
    """创建扫雷棋盘"""
    # 初始化棋盘
    self.board = np.zeros((self.rows, self.cols), dtype=int)
    self.revealed = np.zeros((self.rows, self.cols), dtype=bool)
    
    # 随机放置地雷
    positions = np.random.choice(
      self.rows * self.cols, 
      size=self.mines, 
      replace=False
    )
    
    for pos in positions:
      row, col = pos // self.cols, pos % self.cols
      self.mine_positions.add((row, col))
      self.board[row, col] = -1  # -1 表示地雷
    
    # 计算每个格子周围的地雷数
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i, j] != -1:
          count = self._count_adjacent_mines(i, j)
          self.board[i, j] = count
  
  def _count_adjacent_mines(self, row, col):
    """计算周围地雷数量"""
    count = 0
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        nr, nc = row + dr, col + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
          if self.board[nr, nc] == -1:
            count += 1
    return count
  
  def reveal_cell(self, row, col):
    """翻开一个格子"""
    if self.board[row, col] == -1:
      return False  # 踩到雷
    
    self.revealed[row, col] = True
    
    # 如果是0，自动翻开周围
    if self.board[row, col] == 0:
      self._reveal_adjacent(row, col)
    
    return True
  
  def _reveal_adjacent(self, row, col):
    """递归翻开相邻的空格"""
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        nr, nc = row + dr, col + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
          if not self.revealed[nr, nc] and self.board[nr, nc] != -1:
            self.revealed[nr, nc] = True
            if self.board[nr, nc] == 0:
              self._reveal_adjacent(nr, nc)
  
  def get_visible_board(self):
    """获取玩家可见的棋盘状态"""
    visible = np.full((self.rows, self.cols), -1, dtype=int)  # -1表示未翻开
    for i in range(self.rows):
      for j in range(self.cols):
        if self.revealed[i, j]:
          visible[i, j] = self.board[i, j]
    return visible
  
  def solve(self):
    """求解当前状态"""
    visible = self.get_visible_board()
    safe_cells = []
    mine_cells = []
    
    for i in range(self.rows):
      for j in range(self.cols):
        if visible[i, j] > 0:  # 如果是数字
          result = self._analyze_neighbors(i, j, visible)
          safe_cells.extend(result['safe'])
          mine_cells.extend(result['mines'])
    
    return list(set(safe_cells)), list(set(mine_cells))
  
  def _analyze_neighbors(self, row, col, visible):
    """分析某个数字格周围的情况"""
    number = visible[row, col]
    neighbors = self._get_neighbors(row, col)
    
    unknown = []
    
    for nr, nc in neighbors:
      if visible[nr, nc] == -1:  # 未翻开
        unknown.append((nr, nc))
    
    result = {'safe': [], 'mines': []}
    
    # 如果未知格子数等于数字，所有未知格都是雷
    if len(unknown) == number:
      result['mines'] = unknown
    
    # 如果没有未知格子，说明已经处理完
    if number == 0 or len(unknown) == 0:
      result['safe'] = []
    
    return result
  
  def _get_neighbors(self, row, col):
    """获取相邻格子"""
    neighbors = []
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        nr, nc = row + dr, col + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
          neighbors.append((nr, nc))
    return neighbors
  
  def visualize(self, safe_cells=None, mine_cells=None, cell_size=40):
    """可视化棋盘"""
    width = self.cols * cell_size
    height = self.rows * cell_size
    
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
      font = ImageFont.truetype("arial.ttf", cell_size // 2)
    except:
      font = ImageFont.load_default()
    
    visible = self.get_visible_board()
    
    # 绘制格子
    for i in range(self.rows):
      for j in range(self.cols):
        x = j * cell_size
        y = i * cell_size
        
        # 绘制边框
        draw.rectangle([x, y, x + cell_size, y + cell_size], 
                      outline='black', width=1)
        
        if self.revealed[i, j]:
          # 已翻开的格子
          if self.board[i, j] == -1:
            # 地雷
            draw.rectangle([x, y, x + cell_size, y + cell_size], 
                          fill='red')
            draw.text((x + cell_size//2, y + cell_size//2), 
                     '💣', fill='black', anchor='mm')
          elif self.board[i, j] == 0:
            # 空格
            draw.rectangle([x, y, x + cell_size, y + cell_size], 
                          fill='lightgray')
          else:
            # 数字
            colors = ['blue', 'green', 'red', 'purple', 
                     'maroon', 'turquoise', 'black', 'gray']
            color = colors[min(self.board[i, j] - 1, len(colors) - 1)]
            draw.rectangle([x, y, x + cell_size, y + cell_size], 
                          fill='lightgray')
            draw.text((x + cell_size//2, y + cell_size//2), 
                     str(self.board[i, j]), fill=color, 
                     anchor='mm', font=font)
        else:
          # 未翻开的格子
          draw.rectangle([x, y, x + cell_size, y + cell_size], 
                        fill='darkgray')
    
    # 绘制提示
    if safe_cells:
      for row, col in safe_cells:
        x = col * cell_size
        y = row * cell_size
        draw.rectangle([x+2, y+2, x + cell_size-2, y + cell_size-2], 
                      outline='green', width=3)
    
    if mine_cells:
      for row, col in mine_cells:
        x = col * cell_size
        y = row * cell_size
        draw.rectangle([x+2, y+2, x + cell_size-2, y + cell_size-2], 
                      outline='red', width=3)
    
    return img


def main():
  """演示程序"""
  print("=== 扫雷辅助工具 - 演示版 ===\n")
  
  # 创建游戏
  print("创建 9x9 棋盘，10个地雷...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  game.create_board()
  
  # 随机翻开几个格子
  print("随机翻开一些格子...")
  import random
  for _ in range(5):
    row = random.randint(0, 8)
    col = random.randint(0, 8)
    if (row, col) not in game.mine_positions:
      game.reveal_cell(row, col)
  
  # 保存初始状态
  print("\n保存初始状态...")
  img1 = game.visualize()
  img1.save('demo_initial.png')
  print("已保存到: demo_initial.png")
  
  # 求解
  print("\n分析当前状态...")
  safe_cells, mine_cells = game.solve()
  
  print(f"\n找到 {len(safe_cells)} 个安全格子")
  print(f"找到 {len(mine_cells)} 个地雷格子")
  
  if safe_cells:
    print("\n✅ 安全格子（绿色边框）:")
    for row, col in safe_cells:
      print(f"   行 {row+1}, 列 {col+1}")
  
  if mine_cells:
    print("\n💣 地雷格子（红色边框）:")
    for row, col in mine_cells:
      print(f"   行 {row+1}, 列 {col+1}")
      # 验证是否正确
      is_mine = (row, col) in game.mine_positions
      print(f"      验证: {'✓ 正确' if is_mine else '✗ 错误'}")
  
  # 保存带提示的状态
  print("\n保存带提示的状态...")
  img2 = game.visualize(safe_cells, mine_cells)
  img2.save('demo_hints.png')
  print("已保存到: demo_hints.png")
  
  # 显示棋盘
  print("\n当前可见棋盘:")
  visible = game.get_visible_board()
  
  # 打印表头
  print("    ", end="")
  for j in range(game.cols):
    print(f"{j+1:3}", end="")
  print()
  
  # 打印棋盘
  for i in range(game.rows):
    print(f"{i+1:3} ", end="")
    for j in range(game.cols):
      val = visible[i, j]
      if val == -1:
        print("  ■", end="")
      elif val == 0:
        print("  ·", end="")
      else:
        print(f"  {val}", end="")
    print()
  
  print("\n图例:")
  print("  ■ = 未翻开")
  print("  · = 空白")
  print("  数字 = 周围地雷数")
  
  print("\n请查看生成的图片文件以查看详细提示！")


if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

