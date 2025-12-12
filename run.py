"""
扫雷辅助工具启动脚本
"""

import sys
from pathlib import Path

# 添加src目录到路径
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == '__main__':
  from main import main  # type: ignore
  main()

