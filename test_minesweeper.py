"""
测试扫雷辅助工具的基本功能
"""

import numpy as np
from minesweeper_demo import MinesweeperDemo


def test_board_creation():
  """测试棋盘创建"""
  print("测试1: 棋盘创建...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  game.create_board()
  
  # 检查地雷数量
  mine_count = np.sum(game.board == -1)
  assert mine_count == 10, f"地雷数量错误: {mine_count} != 10"
  print("✓ 棋盘创建成功，地雷数量正确")


def test_reveal():
  """测试格子翻开"""
  print("\n测试2: 格子翻开...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  game.create_board()
  
  # 找一个不是地雷的格子
  for i in range(game.rows):
    for j in range(game.cols):
      if game.board[i, j] != -1:
        result = game.reveal_cell(i, j)
        assert result == True, "翻开非雷格子应该返回True"
        assert game.revealed[i, j] == True, "格子应该被标记为已翻开"
        print(f"✓ 成功翻开格子 ({i}, {j})")
        return


def test_solver():
  """测试求解器"""
  print("\n测试3: 求解器...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  game.create_board()
  
  # 翻开一些格子
  revealed_count = 0
  for i in range(game.rows):
    for j in range(game.cols):
      if game.board[i, j] != -1 and revealed_count < 10:
        game.reveal_cell(i, j)
        revealed_count += 1
  
  # 运行求解器
  safe_cells, mine_cells = game.solve()
  
  print(f"✓ 找到 {len(safe_cells)} 个安全格子")
  print(f"✓ 找到 {len(mine_cells)} 个地雷格子")
  
  # 验证地雷预测
  if mine_cells:
    correct = 0
    for row, col in mine_cells:
      if (row, col) in game.mine_positions:
        correct += 1
    
    accuracy = correct / len(mine_cells) * 100
    print(f"✓ 地雷预测准确率: {accuracy:.1f}%")


def test_visualization():
  """测试可视化"""
  print("\n测试4: 可视化...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  game.create_board()
  
  # 翻开一些格子
  for i in range(3):
    for j in range(3):
      if game.board[i, j] != -1:
        game.reveal_cell(i, j)
  
  # 生成图像
  img = game.visualize()
  assert img is not None, "图像生成失败"
  assert img.size == (360, 360), f"图像尺寸错误: {img.size}"
  
  # 保存测试图像
  img.save('test_output.png')
  print("✓ 图像生成成功，已保存到 test_output.png")


def test_neighbors():
  """测试邻居查找"""
  print("\n测试5: 邻居查找...")
  game = MinesweeperDemo(rows=9, cols=9, mines=10)
  
  # 测试角落
  neighbors = game._get_neighbors(0, 0)
  assert len(neighbors) == 3, f"左上角应该有3个邻居，实际: {len(neighbors)}"
  
  # 测试边缘
  neighbors = game._get_neighbors(0, 4)
  assert len(neighbors) == 5, f"上边缘应该有5个邻居，实际: {len(neighbors)}"
  
  # 测试中间
  neighbors = game._get_neighbors(4, 4)
  assert len(neighbors) == 8, f"中间应该有8个邻居，实际: {len(neighbors)}"
  
  print("✓ 邻居查找功能正常")


def main():
  """运行所有测试"""
  print("=== 扫雷辅助工具测试 ===\n")
  
  try:
    test_board_creation()
    test_reveal()
    test_neighbors()
    test_solver()
    test_visualization()
    
    print("\n" + "="*50)
    print("✅ 所有测试通过！")
    print("="*50)
    
  except AssertionError as e:
    print(f"\n❌ 测试失败: {e}")
    return False
  
  except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
    return False
  
  return True


if __name__ == '__main__':
  success = main()
  exit(0 if success else 1)

