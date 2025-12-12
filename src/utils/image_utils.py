"""
图像处理工具函数
"""

import cv2
import numpy as np
from PIL import Image
from PySide6.QtGui import QPixmap, QImage


def numpy_to_pil(image):
  """
  将numpy数组转换为PIL图像
  
  Args:
    image: numpy数组图像（BGR格式）
    
  Returns:
    PIL Image对象
  """
  if isinstance(image, np.ndarray):
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
  return image


def resize_to_fit(image, canvas_width, canvas_height):
  """
  调整图像大小以适应画布
  
  Args:
    image: PIL Image对象
    canvas_width: 画布宽度
    canvas_height: 画布高度
    
  Returns:
    调整后的PIL Image对象
  """
  img_ratio = image.width / image.height
  canvas_ratio = canvas_width / canvas_height
  
  if img_ratio > canvas_ratio:
    new_width = canvas_width
    new_height = int(canvas_width / img_ratio)
  else:
    new_height = canvas_height
    new_width = int(canvas_height * img_ratio)
  
  return image.resize((new_width, new_height), Image.LANCZOS)


def pil_to_qpixmap(pil_image):
  """
  将PIL图像转换为QPixmap
  
  Args:
    pil_image: PIL Image对象
    
  Returns:
    QPixmap对象
  """
  # 转换PIL图像为RGB模式
  if pil_image.mode != 'RGB':
    pil_image = pil_image.convert('RGB')
  
  # 获取图像数据
  img_data = pil_image.tobytes('raw', 'RGB')
  
  # 创建QImage
  qimage = QImage(
    img_data,
    pil_image.width,
    pil_image.height,
    pil_image.width * 3,
    QImage.Format.Format_RGB888
  )
  
  # 转换为QPixmap
  return QPixmap.fromImage(qimage)


def detect_board_region(image, min_size=200):
  """
  检测图像中的棋盘区域
  
  Args:
    image: numpy数组图像（BGR格式）
    min_size: 最小棋盘尺寸
    
  Returns:
    (x, y, w, h) 棋盘区域，如果未检测到返回None
  """
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray, 50, 150)
  
  contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  
  max_area = 0
  board_rect = None
  
  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    area = w * h
    if area > max_area and w > min_size and h > min_size:
      max_area = area
      board_rect = (x, y, w, h)
  
  return board_rect


def extract_board_region(image, region):
  """
  从图像中提取棋盘区域
  
  Args:
    image: numpy数组图像
    region: (x, y, w, h) 区域坐标
    
  Returns:
    提取的区域图像
  """
  if region:
    x, y, w, h = region
    return image[y:y+h, x:x+w]
  return image


def get_cell_image(board_image, row, col, cell_size):
  """
  获取指定位置的格子图像
  
  Args:
    board_image: 棋盘图像
    row: 行索引
    col: 列索引
    cell_size: 格子大小
    
  Returns:
    格子图像
  """
  x_start = col * cell_size
  y_start = row * cell_size
  return board_image[y_start:y_start+cell_size, x_start:x_start+cell_size]

