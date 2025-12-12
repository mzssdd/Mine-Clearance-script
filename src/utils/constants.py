"""
常量定义
"""

# 棋盘大小预设
BOARD_SIZES = {
  'BEGINNER': (9, 9),
  'INTERMEDIATE': (16, 16),
  'EXPERT': (16, 30),
}

# 棋盘大小选项（用于GUI下拉框）
SIZE_OPTIONS = ['9x9', '16x16', '16x30', '自定义']

# 颜色定义
class Colors:
  """颜色常量"""
  SAFE_COLOR = (0, 255, 0, 255)      # 绿色 - 安全格子
  MINE_COLOR = (255, 0, 0, 255)      # 红色 - 地雷格子
  SAFE_OUTLINE = (0, 255, 0)         # 绿色边框
  MINE_OUTLINE = (255, 0, 0)         # 红色边框

# GUI配置
class GUIConfig:
  """GUI配置常量"""
  WINDOW_TITLE = '扫雷辅助工具'
  WINDOW_SIZE = '1000x700'
  CAPTURE_DELAY = 5  # 截图延迟秒数
  
  # 按钮颜色
  BTN_CAPTURE_BG = '#4CAF50'
  BTN_ANALYZE_BG = '#2196F3'
  BTN_SAVE_BG = '#FF9800'
  BTN_FG = 'white'
  
  # 字体
  TITLE_FONT = ('Arial', 20, 'bold')
  LABEL_FONT = ('Arial', 10)
  BUTTON_FONT = ('Arial', 10, 'bold')
  INFO_FONT = ('Courier New', 9)

# 图像处理常量
class ImageConfig:
  """图像处理配置"""
  MIN_BOARD_SIZE = 200  # 最小棋盘尺寸（像素）
  CANNY_LOW = 50
  CANNY_HIGH = 150
  
  # 识别阈值
  BRIGHT_THRESHOLD = 200  # 未翻开格子的亮度阈值
  DARK_THRESHOLD = 100    # 空白格子的亮度阈值
  COLOR_SATURATION = 50   # 颜色饱和度阈值

# 状态消息
class Messages:
  """状态消息"""
  READY = '准备就绪 - 请点击\'捕获屏幕\'开始'
  CAPTURING = '⏱️ {}秒后捕获...'
  CAPTURE_SUCCESS = '✅ 屏幕捕获成功！请点击\'分析并提示\'按钮'
  ANALYZING = '🔍 正在分析棋盘...'
  ANALYSIS_COMPLETE = '✅ 分析完成！找到 {} 个安全格子，{} 个地雷格子'
  NO_HINTS = '⚠️ 未找到明确的提示'
  
  # 警告消息
  WARNING_NO_SCREENSHOT = '请先捕获屏幕！'
  WARNING_NO_IMAGE = '没有可保存的图像！'
  
  # 错误消息
  ERROR_CAPTURE = '捕获屏幕失败：{}'
  ERROR_ANALYZE = '分析失败：{}'
  ERROR_SAVE = '保存失败：{}'
  
  # 成功消息
  SUCCESS_SAVE = '图片已保存到:\n{}'

# 格子状态
class CellState:
  """格子状态常量"""
  UNKNOWN = -1   # 未翻开
  EMPTY = 0      # 空白
  FLAGGED = -2   # 已标记为雷
  # 1-8 表示数字

# 文件相关
class FileConfig:
  """文件配置"""
  DEFAULT_FILENAME = 'minesweeper_hint.png'
  FILE_TYPES = [('PNG图片', '*.png'), ('所有文件', '*.*')]

