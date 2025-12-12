"""
扫雷辅助工具
能够识别屏幕上的扫雷游戏并给出游戏提示
"""

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageDraw, ImageFont
import time
from typing import List, Tuple, Set


class MinesweeperSolver:
  def __init__(self):
    self.board = None
    self.rows = 0
    self.cols = 0
    self.cell_size = 0
    self.board_region = None
    
  def capture_screen(self, region=None):
    """捕获屏幕或指定区域"""
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
  
  def detect_board(self, image):
    """检测扫雷棋盘区域"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大的矩形区域作为棋盘
    max_area = 0
    board_rect = None
    
    for contour in contours:
      x, y, w, h = cv2.boundingRect(contour)
      area = w * h
      # 棋盘应该是一个相对大的矩形
      if area > max_area and w > 200 and h > 200:
        max_area = area
        board_rect = (x, y, w, h)
    
    return board_rect
  
  def recognize_cell(self, cell_image):
    """识别单个格子的状态"""
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
    avg_color = np.mean(gray)
    
    # 根据颜色和纹理判断格子状态
    if avg_color > 200:  # 未翻开的格子（浅色）
      return -1
    elif avg_color < 100:  # 已翻开的空白格子
      return 0
    else:
      # 尝试识别数字（1-8）
      # 这里简化处理，实际应该用OCR或模板匹配
      return self._detect_number(cell_image)
  
  def _detect_number(self, cell_image):
    """检测格子中的数字"""
    # 转换为灰度图
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
    
    # 使用颜色来区分不同的数字
    # 1-蓝色, 2-绿色, 3-红色, 4-深蓝, 5-深红, 6-青色, 7-黑色, 8-灰色
    hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
    
    # 检测是否有明显的颜色（数字）
    if np.max(hsv[:, :, 1]) < 50:  # 饱和度很低，可能是空白
      return 0
    
    # 简化：通过亮度和颜色粗略判断
    # 实际项目中应该使用更精确的方法
    h_channel = hsv[:, :, 0]
    dominant_hue = np.median(h_channel[h_channel > 0])
    
    if dominant_hue < 130 and dominant_hue > 100:
      return 1  # 蓝色
    elif dominant_hue < 80 and dominant_hue > 40:
      return 2  # 绿色
    elif dominant_hue > 160 or dominant_hue < 10:
      return 3  # 红色
    
    # 默认返回未知状态
    return 0
  
  def analyze_board(self, image, grid_size=(9, 9)):
    """分析整个棋盘"""
    self.rows, self.cols = grid_size
    
    if self.board_region:
      x, y, w, h = self.board_region
      board_img = image[y:y+h, x:x+w]
    else:
      board_img = image
    
    h, w = board_img.shape[:2]
    self.cell_size = min(w // self.cols, h // self.rows)
    
    # 创建棋盘矩阵
    self.board = np.zeros((self.rows, self.cols), dtype=int)
    
    for i in range(self.rows):
      for j in range(self.cols):
        x_start = j * self.cell_size
        y_start = i * self.cell_size
        cell = board_img[y_start:y_start+self.cell_size, 
                        x_start:x_start+self.cell_size]
        
        self.board[i, j] = self.recognize_cell(cell)
    
    return self.board
  
  def solve(self):
    """求解扫雷游戏，返回安全位置和雷位置"""
    if self.board is None:
      return [], []
    
    safe_cells = []
    mine_cells = []
    
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i, j] > 0:  # 如果是数字
          result = self._analyze_neighbors(i, j)
          safe_cells.extend(result['safe'])
          mine_cells.extend(result['mines'])
    
    return list(set(safe_cells)), list(set(mine_cells))
  
  def _analyze_neighbors(self, row, col):
    """分析某个数字格周围的情况"""
    number = self.board[row, col]
    neighbors = self._get_neighbors(row, col)
    
    unknown = []
    flagged = []
    
    for nr, nc in neighbors:
      if self.board[nr, nc] == -1:  # 未翻开
        unknown.append((nr, nc))
      elif self.board[nr, nc] == -2:  # 已标记为雷
        flagged.append((nr, nc))
    
    result = {'safe': [], 'mines': []}
    
    # 如果未知格子数等于剩余雷数，所有未知格都是雷
    if len(unknown) == number - len(flagged):
      result['mines'] = unknown
    
    # 如果标记的雷数等于数字，所有未知格都是安全的
    if len(flagged) == number:
      result['safe'] = unknown
    
    return result
  
  def _get_neighbors(self, row, col):
    """获取相邻格子的坐标"""
    neighbors = []
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        nr, nc = row + dr, col + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
          neighbors.append((nr, nc))
    return neighbors
  
  def create_hint_overlay(self, original_image, safe_cells, mine_cells):
    """创建提示覆盖层"""
    img = Image.fromarray(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    if not self.board_region:
      return img
    
    x_offset, y_offset = self.board_region[0], self.board_region[1]
    
    # 绘制安全格子（绿色）
    for row, col in safe_cells:
      x = x_offset + col * self.cell_size
      y = y_offset + row * self.cell_size
      draw.rectangle(
        [x, y, x + self.cell_size, y + self.cell_size],
        outline=(0, 255, 0, 200),
        width=3
      )
      draw.text(
        (x + self.cell_size // 2, y + self.cell_size // 2),
        '✓',
        fill=(0, 255, 0, 255),
        anchor='mm'
      )
    
    # 绘制雷格子（红色）
    for row, col in mine_cells:
      x = x_offset + col * self.cell_size
      y = y_offset + row * self.cell_size
      draw.rectangle(
        [x, y, x + self.cell_size, y + self.cell_size],
        outline=(255, 0, 0, 200),
        width=3
      )
      draw.text(
        (x + self.cell_size // 2, y + self.cell_size // 2),
        '💣',
        fill=(255, 0, 0, 255),
        anchor='mm'
      )
    
    # 合并图像
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay)
    
    return result


def main():
  """主函数"""
  print("=== 扫雷辅助工具 ===")
  print("使用说明：")
  print("1. 打开扫雷游戏")
  print("2. 按下 's' 键开始扫描并获取提示")
  print("3. 按下 'q' 键退出")
  print("\n绿色方框 ✓ = 安全，可以点击")
  print("红色方框 💣 = 地雷，需要标记")
  print()
  
  solver = MinesweeperSolver()
  
  while True:
    print("\n等待命令...")
    print("按 's' 扫描游戏，按 'q' 退出")
    
    command = input("请输入命令: ").strip().lower()
    
    if command == 'q':
      print("退出程序")
      break
    
    if command == 's':
      print("\n正在捕获屏幕...")
      
      # 选择区域提示
      print("请将鼠标移动到扫雷游戏窗口")
      print("5秒后开始捕获...")
      time.sleep(5)
      
      # 捕获屏幕
      screenshot = solver.capture_screen()
      
      print("正在分析棋盘...")
      
      # 检测棋盘区域
      board_rect = solver.detect_board(screenshot)
      
      if board_rect:
        solver.board_region = board_rect
        print(f"检测到棋盘区域: {board_rect}")
      else:
        print("警告: 未能自动检测到棋盘区域，将分析整个屏幕")
      
      # 询问棋盘大小
      print("\n请输入棋盘大小（默认 9x9）:")
      print("初级: 9x9, 中级: 16x16, 高级: 16x30")
      size_input = input("输入格式 '行x列' (如: 9x9): ").strip()
      
      if size_input:
        try:
          rows, cols = map(int, size_input.split('x'))
          grid_size = (rows, cols)
        except:
          grid_size = (9, 9)
      else:
        grid_size = (9, 9)
      
      # 分析棋盘
      board = solver.analyze_board(screenshot, grid_size)
      print("\n当前棋盘状态:")
      print(board)
      
      # 求解
      print("\n正在计算提示...")
      safe_cells, mine_cells = solver.solve()
      
      print(f"\n找到 {len(safe_cells)} 个安全格子")
      print(f"找到 {len(mine_cells)} 个地雷格子")
      
      if safe_cells:
        print("\n安全格子（可以点击）:")
        for row, col in safe_cells[:5]:  # 只显示前5个
          print(f"  行{row+1}, 列{col+1}")
        if len(safe_cells) > 5:
          print(f"  ... 还有 {len(safe_cells)-5} 个")
      
      if mine_cells:
        print("\n地雷格子（需要标记）:")
        for row, col in mine_cells[:5]:
          print(f"  行{row+1}, 列{col+1}")
        if len(mine_cells) > 5:
          print(f"  ... 还有 {len(mine_cells)-5} 个")
      
      # 创建提示图像
      print("\n正在生成提示图像...")
      hint_image = solver.create_hint_overlay(screenshot, safe_cells, mine_cells)
      
      # 保存结果
      output_path = 'minesweeper_hint.png'
      hint_image.save(output_path)
      print(f"\n提示图像已保存到: {output_path}")
      print("请查看图像以获得详细提示")


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print("\n\n程序被用户中断")
  except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

