"""
图像处理器
负责截图和图像识别
"""

import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageDraw

from utils.constants import Colors, ImageConfig
from utils.image_utils import detect_board_region, extract_board_region


class ImageProcessor:
  """图像处理器类"""
  
  def __init__(self):
    self.screenshot = None
    self.board_region = None
  
  def capture_screenshot(self, region=None):
    """
    捕获屏幕截图
    
    Args:
      region: 可选的截图区域 (x, y, width, height)
      
    Returns:
      numpy数组图像（BGR格式）
    """
    screenshot = pyautogui.screenshot(region=region)
    self.screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return self.screenshot
  
  def detect_board(self, image=None):
    """
    检测棋盘区域
    
    Args:
      image: 可选的图像，如果为None则使用上次截图
      
    Returns:
      (x, y, w, h) 棋盘区域坐标
    """
    if image is None:
      image = self.screenshot
    
    if image is None:
      return None
    
    self.board_region = detect_board_region(image, ImageConfig.MIN_BOARD_SIZE)
    return self.board_region
  
  def get_board_image(self):
    """
    获取棋盘区域图像
    
    Returns:
      棋盘图像
    """
    if self.screenshot is None:
      return None
    
    return extract_board_region(self.screenshot, self.board_region)
  
  def recognize_cell(self, cell_image):
    """
    识别单个格子的状态
    
    Args:
      cell_image: 格子图像
      
    Returns:
      格子状态（-1=未翻开, 0=空白, 1-8=数字）
    """
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
    avg_color = np.mean(gray)
    
    if avg_color > ImageConfig.BRIGHT_THRESHOLD:
      return -1  # 未翻开
    elif avg_color < ImageConfig.DARK_THRESHOLD:
      return 0   # 空白
    else:
      return self._detect_number(cell_image)
  
  def _detect_number(self, cell_image):
    """
    检测格子中的数字
    
    Args:
      cell_image: 格子图像
      
    Returns:
      数字（1-8）或0
    """
    hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
    
    # 检查饱和度
    if np.max(hsv[:, :, 1]) < ImageConfig.COLOR_SATURATION:
      return 0
    
    # 通过色调判断数字
    h_channel = hsv[:, :, 0]
    dominant_hue = np.median(h_channel[h_channel > 0])
    
    # 简化的数字识别（基于颜色）
    if 100 < dominant_hue < 130:
      return 1  # 蓝色
    elif 40 < dominant_hue < 80:
      return 2  # 绿色
    elif dominant_hue > 160 or dominant_hue < 10:
      return 3  # 红色
    
    return 0
  
  def create_hint_overlay(self, image, safe_cells, mine_cells, board_region, cell_size):
    """
    创建提示覆盖层
    
    Args:
      image: 原始图像（numpy数组）
      safe_cells: 安全格子列表 [(row, col), ...]
      mine_cells: 地雷格子列表 [(row, col), ...]
      board_region: 棋盘区域 (x, y, w, h)
      cell_size: 格子大小
      
    Returns:
      带提示的PIL Image对象
    """
    # 转换为PIL图像
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    if not board_region:
      return img
    
    x_offset, y_offset = board_region[0], board_region[1]
    
    # 绘制安全格子
    for row, col in safe_cells:
      self._draw_safe_cell(draw, row, col, x_offset, y_offset, cell_size)
    
    # 绘制地雷格子
    for row, col in mine_cells:
      self._draw_mine_cell(draw, row, col, x_offset, y_offset, cell_size)
    
    # 合并图像
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay)
    
    return result
  
  def _draw_safe_cell(self, draw, row, col, x_offset, y_offset, cell_size):
    """绘制安全格子标记"""
    x = x_offset + col * cell_size
    y = y_offset + row * cell_size
    
    # 绘制绿色边框
    draw.rectangle(
      [x, y, x + cell_size, y + cell_size],
      outline=Colors.SAFE_COLOR,
      width=4
    )
    
    # 绘制勾号
    center_x = x + cell_size // 2
    center_y = y + cell_size // 2
    size = cell_size // 4
    
    draw.line(
      [(center_x - size, center_y), (center_x, center_y + size)],
      fill=Colors.SAFE_COLOR,
      width=3
    )
    draw.line(
      [(center_x, center_y + size), (center_x + size, center_y - size)],
      fill=Colors.SAFE_COLOR,
      width=3
    )
  
  def _draw_mine_cell(self, draw, row, col, x_offset, y_offset, cell_size):
    """绘制地雷格子标记"""
    x = x_offset + col * cell_size
    y = y_offset + row * cell_size
    
    # 绘制红色边框
    draw.rectangle(
      [x, y, x + cell_size, y + cell_size],
      outline=Colors.MINE_COLOR,
      width=4
    )
    
    # 绘制X号
    center_x = x + cell_size // 2
    center_y = y + cell_size // 2
    size = cell_size // 4
    
    draw.line(
      [(center_x - size, center_y - size), (center_x + size, center_y + size)],
      fill=Colors.MINE_COLOR,
      width=3
    )
    draw.line(
      [(center_x - size, center_y + size), (center_x + size, center_y - size)],
      fill=Colors.MINE_COLOR,
      width=3
    )

