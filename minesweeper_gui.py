"""
扫雷辅助工具 - GUI版本
带图形界面的扫雷辅助工具，可以实时显示提示
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import numpy as np
import pyautogui
from threading import Thread
import time


class MinesweeperGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("扫雷辅助工具")
    self.root.geometry("1000x700")
    
    # 数据
    self.screenshot = None
    self.board = None
    self.rows = 9
    self.cols = 9
    self.cell_size = 0
    self.board_region = None
    self.safe_cells = []
    self.mine_cells = []
    
    self.setup_ui()
    
  def setup_ui(self):
    """设置用户界面"""
    # 标题
    title_label = tk.Label(
      self.root, 
      text="🎮 扫雷辅助工具", 
      font=("Arial", 20, "bold"),
      pady=10
    )
    title_label.pack()
    
    # 控制面板
    control_frame = tk.Frame(self.root, pady=10)
    control_frame.pack()
    
    # 棋盘大小设置
    size_frame = tk.Frame(control_frame)
    size_frame.pack(side=tk.LEFT, padx=10)
    
    tk.Label(size_frame, text="棋盘大小:", font=("Arial", 10)).pack(side=tk.LEFT)
    
    self.size_var = tk.StringVar(value="9x9")
    size_combo = ttk.Combobox(
      size_frame, 
      textvariable=self.size_var,
      values=["9x9", "16x16", "16x30", "自定义"],
      width=10,
      state="readonly"
    )
    size_combo.pack(side=tk.LEFT, padx=5)
    size_combo.bind("<<ComboboxSelected>>", self.on_size_changed)
    
    # 自定义大小输入
    self.custom_frame = tk.Frame(control_frame)
    self.custom_frame.pack(side=tk.LEFT, padx=5)
    
    tk.Label(self.custom_frame, text="行:").pack(side=tk.LEFT)
    self.rows_entry = tk.Entry(self.custom_frame, width=5)
    self.rows_entry.pack(side=tk.LEFT, padx=2)
    self.rows_entry.insert(0, "9")
    
    tk.Label(self.custom_frame, text="列:").pack(side=tk.LEFT)
    self.cols_entry = tk.Entry(self.custom_frame, width=5)
    self.cols_entry.pack(side=tk.LEFT, padx=2)
    self.cols_entry.insert(0, "9")
    
    self.custom_frame.pack_forget()  # 默认隐藏
    
    # 按钮
    btn_frame = tk.Frame(control_frame)
    btn_frame.pack(side=tk.LEFT, padx=20)
    
    self.capture_btn = tk.Button(
      btn_frame,
      text="📸 捕获屏幕 (5秒后)",
      command=self.start_capture,
      bg="#4CAF50",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5
    )
    self.capture_btn.pack(side=tk.LEFT, padx=5)
    
    self.analyze_btn = tk.Button(
      btn_frame,
      text="🔍 分析并提示",
      command=self.analyze_board,
      bg="#2196F3",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5,
      state=tk.DISABLED
    )
    self.analyze_btn.pack(side=tk.LEFT, padx=5)
    
    self.save_btn = tk.Button(
      btn_frame,
      text="💾 保存图片",
      command=self.save_image,
      bg="#FF9800",
      fg="white",
      font=("Arial", 10, "bold"),
      padx=15,
      pady=5,
      state=tk.DISABLED
    )
    self.save_btn.pack(side=tk.LEFT, padx=5)
    
    # 状态栏
    self.status_label = tk.Label(
      self.root,
      text="准备就绪 - 请点击'捕获屏幕'开始",
      font=("Arial", 10),
      bg="#f0f0f0",
      pady=5
    )
    self.status_label.pack(fill=tk.X)
    
    # 主显示区域
    display_frame = tk.Frame(self.root)
    display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 左侧 - 原始图像
    left_frame = tk.LabelFrame(
      display_frame, 
      text="📷 捕获的图像",
      font=("Arial", 10, "bold")
    )
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    self.original_canvas = tk.Canvas(left_frame, bg="white")
    self.original_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 右侧 - 提示图像和信息
    right_frame = tk.Frame(display_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    # 提示图像
    hint_frame = tk.LabelFrame(
      right_frame,
      text="💡 游戏提示",
      font=("Arial", 10, "bold")
    )
    hint_frame.pack(fill=tk.BOTH, expand=True)
    
    self.hint_canvas = tk.Canvas(hint_frame, bg="white")
    self.hint_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 提示信息
    info_frame = tk.LabelFrame(
      right_frame,
      text="ℹ️ 提示信息",
      font=("Arial", 10, "bold")
    )
    info_frame.pack(fill=tk.BOTH, padx=0, pady=5)
    
    self.info_text = tk.Text(
      info_frame,
      height=10,
      font=("Courier New", 9),
      wrap=tk.WORD
    )
    self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 添加滚动条
    scrollbar = tk.Scrollbar(self.info_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.info_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=self.info_text.yview)
    
    # 图例
    legend_frame = tk.Frame(self.root, bg="#f8f8f8", pady=5)
    legend_frame.pack(fill=tk.X)
    
    tk.Label(
      legend_frame,
      text="🟢 绿色边框 = 安全格子(可点击)    🔴 红色边框 = 地雷格子(需标记)",
      font=("Arial", 10),
      bg="#f8f8f8"
    ).pack()
  
  def on_size_changed(self, event=None):
    """棋盘大小改变时"""
    size = self.size_var.get()
    if size == "自定义":
      self.custom_frame.pack(side=tk.LEFT, padx=5)
    else:
      self.custom_frame.pack_forget()
      if size == "9x9":
        self.rows, self.cols = 9, 9
      elif size == "16x16":
        self.rows, self.cols = 16, 16
      elif size == "16x30":
        self.rows, self.cols = 16, 30
  
  def start_capture(self):
    """开始捕获屏幕"""
    self.update_status("⏱️ 5秒后将捕获屏幕，请切换到扫雷游戏窗口...")
    self.capture_btn.config(state=tk.DISABLED)
    
    # 在新线程中延迟捕获
    Thread(target=self.capture_screen_delayed, daemon=True).start()
  
  def capture_screen_delayed(self):
    """延迟捕获屏幕"""
    for i in range(5, 0, -1):
      self.root.after(0, self.update_status, f"⏱️ {i} 秒后捕获...")
      time.sleep(1)
    
    # 捕获屏幕
    self.root.after(0, self.capture_and_display)
  
  def capture_and_display(self):
    """捕获并显示屏幕"""
    try:
      # 捕获屏幕
      screenshot = pyautogui.screenshot()
      self.screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
      
      # 检测棋盘区域
      self.board_region = self.detect_board(self.screenshot)
      
      # 显示原始图像
      self.display_image(self.screenshot, self.original_canvas)
      
      self.update_status("✅ 屏幕捕获成功！请点击'分析并提示'按钮")
      self.capture_btn.config(state=tk.NORMAL)
      self.analyze_btn.config(state=tk.NORMAL)
      
    except Exception as e:
      messagebox.showerror("错误", f"捕获屏幕失败：{str(e)}")
      self.capture_btn.config(state=tk.NORMAL)
  
  def detect_board(self, image):
    """检测棋盘区域"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    max_area = 0
    board_rect = None
    
    for contour in contours:
      x, y, w, h = cv2.boundingRect(contour)
      area = w * h
      if area > max_area and w > 200 and h > 200:
        max_area = area
        board_rect = (x, y, w, h)
    
    return board_rect
  
  def analyze_board(self):
    """分析棋盘并生成提示"""
    if self.screenshot is None:
      messagebox.showwarning("警告", "请先捕获屏幕！")
      return
    
    try:
      self.update_status("🔍 正在分析棋盘...")
      
      # 获取棋盘大小
      if self.size_var.get() == "自定义":
        self.rows = int(self.rows_entry.get())
        self.cols = int(self.cols_entry.get())
      
      # 分析棋盘
      self.board = self.analyze_board_state(self.screenshot)
      
      # 求解
      self.safe_cells, self.mine_cells = self.solve()
      
      # 生成提示图像
      hint_image = self.create_hint_overlay()
      
      # 显示提示图像
      self.display_image(hint_image, self.hint_canvas)
      
      # 显示提示信息
      self.display_hint_info()
      
      self.save_btn.config(state=tk.NORMAL)
      self.update_status(
        f"✅ 分析完成！找到 {len(self.safe_cells)} 个安全格子，"
        f"{len(self.mine_cells)} 个地雷格子"
      )
      
    except Exception as e:
      messagebox.showerror("错误", f"分析失败：{str(e)}")
      import traceback
      traceback.print_exc()
  
  def analyze_board_state(self, image):
    """分析棋盘状态"""
    if self.board_region:
      x, y, w, h = self.board_region
      board_img = image[y:y+h, x:x+w]
    else:
      board_img = image
    
    h, w = board_img.shape[:2]
    self.cell_size = min(w // self.cols, h // self.rows)
    
    board = np.zeros((self.rows, self.cols), dtype=int)
    
    for i in range(self.rows):
      for j in range(self.cols):
        x_start = j * self.cell_size
        y_start = i * self.cell_size
        cell = board_img[y_start:y_start+self.cell_size,
                        x_start:x_start+self.cell_size]
        
        board[i, j] = self.recognize_cell(cell)
    
    return board
  
  def recognize_cell(self, cell_image):
    """识别单个格子"""
    gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
    avg_color = np.mean(gray)
    
    if avg_color > 200:
      return -1  # 未翻开
    elif avg_color < 100:
      return 0   # 空白
    else:
      return self.detect_number(cell_image)
  
  def detect_number(self, cell_image):
    """检测格子中的数字"""
    hsv = cv2.cvtColor(cell_image, cv2.COLOR_BGR2HSV)
    
    if np.max(hsv[:, :, 1]) < 50:
      return 0
    
    h_channel = hsv[:, :, 0]
    dominant_hue = np.median(h_channel[h_channel > 0])
    
    if 100 < dominant_hue < 130:
      return 1
    elif 40 < dominant_hue < 80:
      return 2
    elif dominant_hue > 160 or dominant_hue < 10:
      return 3
    
    return 0
  
  def solve(self):
    """求解扫雷"""
    if self.board is None:
      return [], []
    
    safe_cells = []
    mine_cells = []
    
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i, j] > 0:
          result = self.analyze_neighbors(i, j)
          safe_cells.extend(result['safe'])
          mine_cells.extend(result['mines'])
    
    return list(set(safe_cells)), list(set(mine_cells))
  
  def analyze_neighbors(self, row, col):
    """分析邻居格子"""
    number = self.board[row, col]
    neighbors = self.get_neighbors(row, col)
    
    unknown = []
    flagged = []
    
    for nr, nc in neighbors:
      if self.board[nr, nc] == -1:
        unknown.append((nr, nc))
      elif self.board[nr, nc] == -2:
        flagged.append((nr, nc))
    
    result = {'safe': [], 'mines': []}
    
    if len(unknown) == number - len(flagged):
      result['mines'] = unknown
    
    if len(flagged) == number:
      result['safe'] = unknown
    
    return result
  
  def get_neighbors(self, row, col):
    """获取邻居格子"""
    neighbors = []
    for dr in [-1, 0, 1]:
      for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
          continue
        nr, nc = row + dr, col + dc
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
          neighbors.append((nr, nc))
    return neighbors
  
  def create_hint_overlay(self):
    """创建提示覆盖层"""
    img = Image.fromarray(cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2RGB))
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    if not self.board_region:
      return img
    
    x_offset, y_offset = self.board_region[0], self.board_region[1]
    
    # 绘制安全格子（绿色）
    for row, col in self.safe_cells:
      x = x_offset + col * self.cell_size
      y = y_offset + row * self.cell_size
      draw.rectangle(
        [x, y, x + self.cell_size, y + self.cell_size],
        outline=(0, 255, 0, 255),
        width=4
      )
      # 绘制勾号
      center_x = x + self.cell_size // 2
      center_y = y + self.cell_size // 2
      size = self.cell_size // 4
      draw.line(
        [(center_x - size, center_y), (center_x, center_y + size)],
        fill=(0, 255, 0, 255),
        width=3
      )
      draw.line(
        [(center_x, center_y + size), (center_x + size, center_y - size)],
        fill=(0, 255, 0, 255),
        width=3
      )
    
    # 绘制雷格子（红色）
    for row, col in self.mine_cells:
      x = x_offset + col * self.cell_size
      y = y_offset + row * self.cell_size
      draw.rectangle(
        [x, y, x + self.cell_size, y + self.cell_size],
        outline=(255, 0, 0, 255),
        width=4
      )
      # 绘制X号
      center_x = x + self.cell_size // 2
      center_y = y + self.cell_size // 2
      size = self.cell_size // 4
      draw.line(
        [(center_x - size, center_y - size), (center_x + size, center_y + size)],
        fill=(255, 0, 0, 255),
        width=3
      )
      draw.line(
        [(center_x - size, center_y + size), (center_x + size, center_y - size)],
        fill=(255, 0, 0, 255),
        width=3
      )
    
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay)
    
    return result
  
  def display_image(self, image, canvas):
    """在画布上显示图像"""
    # 转换为PIL图像
    if isinstance(image, np.ndarray):
      image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # 获取画布大小
    canvas.update()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    # 调整图像大小以适应画布
    img_ratio = image.width / image.height
    canvas_ratio = canvas_width / canvas_height
    
    if img_ratio > canvas_ratio:
      new_width = canvas_width
      new_height = int(canvas_width / img_ratio)
    else:
      new_height = canvas_height
      new_width = int(canvas_height * img_ratio)
    
    image = image.resize((new_width, new_height), Image.LANCZOS)
    
    # 转换为PhotoImage并显示
    photo = ImageTk.PhotoImage(image)
    canvas.delete("all")
    canvas.create_image(
      canvas_width // 2,
      canvas_height // 2,
      image=photo,
      anchor=tk.CENTER
    )
    canvas.image = photo  # 保持引用
  
  def display_hint_info(self):
    """显示提示信息"""
    self.info_text.delete(1.0, tk.END)
    
    info = f"{'='*50}\n"
    info += f"  扫雷提示信息\n"
    info += f"{'='*50}\n\n"
    
    info += f"📊 统计:\n"
    info += f"  • 棋盘大小: {self.rows} x {self.cols}\n"
    info += f"  • 安全格子: {len(self.safe_cells)} 个\n"
    info += f"  • 地雷格子: {len(self.mine_cells)} 个\n\n"
    
    if self.safe_cells:
      info += f"🟢 安全格子（建议点击）:\n"
      for i, (row, col) in enumerate(self.safe_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(self.safe_cells) > 10:
        info += f"  ... 还有 {len(self.safe_cells)-10} 个\n"
      info += "\n"
    
    if self.mine_cells:
      info += f"🔴 地雷格子（建议标记）:\n"
      for i, (row, col) in enumerate(self.mine_cells[:10], 1):
        info += f"  {i}. 行 {row+1}, 列 {col+1}\n"
      if len(self.mine_cells) > 10:
        info += f"  ... 还有 {len(self.mine_cells)-10} 个\n"
      info += "\n"
    
    if not self.safe_cells and not self.mine_cells:
      info += "⚠️ 未找到明确的提示\n"
      info += "可能需要:\n"
      info += "  • 翻开更多格子\n"
      info += "  • 检查棋盘大小设置\n"
      info += "  • 重新捕获清晰的图像\n"
    
    self.info_text.insert(1.0, info)
  
  def save_image(self):
    """保存提示图像"""
    if self.screenshot is None:
      messagebox.showwarning("警告", "没有可保存的图像！")
      return
    
    try:
      filename = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")],
        initialfile="minesweeper_hint.png"
      )
      
      if filename:
        hint_image = self.create_hint_overlay()
        hint_image.save(filename)
        messagebox.showinfo("成功", f"图片已保存到:\n{filename}")
    
    except Exception as e:
      messagebox.showerror("错误", f"保存失败：{str(e)}")
  
  def update_status(self, message):
    """更新状态栏"""
    self.status_label.config(text=message)


def main():
  """主函数"""
  root = tk.Tk()
  app = MinesweeperGUI(root)
  root.mainloop()


if __name__ == '__main__':
  main()

