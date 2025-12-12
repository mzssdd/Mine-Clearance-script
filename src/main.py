"""
扫雷辅助工具 - 主程序入口
"""

import sys
import os

# 设置DPI感知，避免警告
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gui.main_window import MainWindow


def main():
  """主函数"""
  # 设置高DPI缩放策略
  QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
  )
  
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())


if __name__ == '__main__':
  main()

