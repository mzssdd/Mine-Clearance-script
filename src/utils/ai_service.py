"""
AI服务模块
用于生成自然语言解释
"""

import requests
import json


class AIService:
  """AI服务类"""
  
  def __init__(self, api_key: str):
    """
    初始化AI服务
    
    Args:
      api_key: API密钥
    """
    self.api_key = api_key
    self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
    self.model = "deepseek-ai/DeepSeek-V3"
  
  def generate_explanation(self, cell_info: dict) -> str:
    """
    生成格子的自然语言解释
    
    Args:
      cell_info: 格子信息，包含position, reason等
      
    Returns:
      自然语言解释
    """
    try:
      prompt = f"""你是一个扫雷游戏的AI助手。请根据以下推理依据，用简洁清晰的中文解释为什么这个格子是地雷：

推理依据：{cell_info['reason']}
格子位置：行{cell_info['row']}，列{cell_info['col']}

要求：
1. 用1-2句话解释
2. 语言简洁易懂
3. 突出逻辑推理过程
4. 不要重复位置信息
5. 直接给出解释，不要加"根据"、"因为"等开头词

示例格式：
"数字3周围有3个未知格子且需要3个雷，所以这些格子必定是雷。"
"""
      
      headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
      }
      
      data = {
        "model": self.model,
        "messages": [
          {
            "role": "user",
            "content": prompt
          }
        ],
        "temperature": 0.3,
        "max_tokens": 100
      }
      
      response = requests.post(
        self.api_url,
        headers=headers,
        json=data,
        timeout=10
      )
      
      if response.status_code == 200:
        result = response.json()
        explanation = result['choices'][0]['message']['content'].strip()
        return explanation
      else:
        # API调用失败，返回原始推理依据
        return cell_info['reason']
    
    except Exception as e:
      # 发生异常，返回原始推理依据
      print(f"AI解释生成失败: {e}")
      return cell_info['reason']
  
  def batch_generate_explanations(self, cells_info: list) -> dict:
    """
    批量生成解释
    
    Args:
      cells_info: 格子信息列表
      
    Returns:
      {(row, col): explanation} 字典
    """
    explanations = {}
    
    for cell_info in cells_info:
      row, col = cell_info['row'], cell_info['col']
      explanation = self.generate_explanation(cell_info)
      explanations[(row, col)] = explanation
    
    return explanations
  
  def analyze_probability(self, board_state: dict) -> dict:
    """
    使用AI进行概率分析，处理无确定性答案的情况
    
    Args:
      board_state: 棋盘状态字典，包含：
        - revealed_cells: [(row, col, number), ...]  已翻开的格子
        - flagged_cells: [(row, col), ...]  已标记的地雷
        - unknown_cells: [(row, col), ...]  未知格子
        - total_mines: 总地雷数
        - remaining_mines: 剩余地雷数
        - rows: 行数
        - cols: 列数
        
    Returns:
      {
        'suggestions': [{'cell': (row, col), 'probability': float, 'reason': str}, ...],
        'analysis': str  # AI的整体分析
      }
    """
    try:
      # 构建棋盘描述
      board_desc = self._build_board_description(board_state)
      
      prompt = f"""你是一个扫雷游戏的高级AI分析师。当前游戏遇到了无法用确定性逻辑推理的情况，需要你进行概率分析。

当前棋盘信息：
{board_desc}

任务：
1. 分析当前局面，找出相对安全概率最高的3-5个格子
2. 为每个格子估算安全概率（0-100%）
3. 解释选择理由

输出格式（严格按照JSON格式）：
{{
  "suggestions": [
    {{"row": 行号, "col": 列号, "probability": 概率值, "reason": "选择理由"}},
    ...
  ],
  "analysis": "整体局面分析（1-2句话）"
}}

要求：
- 概率值为0-100的整数
- 理由简洁清晰（10-20字）
- 优先推荐概率最高的格子
- 考虑边缘格子通常较安全
- 必须返回有效的JSON格式
"""
      
      headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
      }
      
      data = {
        "model": self.model,
        "messages": [
          {
            "role": "user",
            "content": prompt
          }
        ],
        "temperature": 0.5,
        "max_tokens": 500
      }
      
      response = requests.post(
        self.api_url,
        headers=headers,
        json=data,
        timeout=15
      )
      
      if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # 尝试解析JSON响应
        try:
          # 移除可能的markdown代码块标记
          if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
              content = content[4:]
          
          analysis_result = json.loads(content)
          return analysis_result
        except json.JSONDecodeError:
          # JSON解析失败，返回默认结果
          return self._get_fallback_suggestion(board_state)
      else:
        return self._get_fallback_suggestion(board_state)
    
    except Exception as e:
      print(f"AI概率分析失败: {e}")
      return self._get_fallback_suggestion(board_state)
  
  def _build_board_description(self, board_state: dict) -> str:
    """构建棋盘描述文本"""
    desc = []
    desc.append(f"棋盘大小：{board_state['rows']}行 × {board_state['cols']}列")
    desc.append(f"总地雷数：{board_state['total_mines']}")
    desc.append(f"剩余地雷数：{board_state['remaining_mines']}")
    desc.append(f"已翻开格子数：{len(board_state['revealed_cells'])}")
    desc.append(f"已标记地雷数：{len(board_state['flagged_cells'])}")
    desc.append(f"未知格子数：{len(board_state['unknown_cells'])}")
    
    # 添加部分已翻开格子的详细信息（避免过长）
    if board_state['revealed_cells']:
      desc.append("\n关键数字格子（部分）：")
      for i, (row, col, num) in enumerate(board_state['revealed_cells'][:20]):
        if num > 0:  # 只显示有数字的格子
          desc.append(f"  行{row+1}列{col+1}: 数字{num}")
    
    return "\n".join(desc)
  
  def _get_fallback_suggestion(self, board_state: dict) -> dict:
    """
    AI分析失败时的降级策略：选择边缘或角落的未知格子
    """
    unknown = board_state['unknown_cells']
    if not unknown:
      return {
        'suggestions': [],
        'analysis': '没有可选择的格子'
      }
    
    rows = board_state['rows']
    cols = board_state['cols']
    
    # 优先选择四个角和边缘
    corner_cells = [
      (0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1)
    ]
    
    suggestions = []
    for row, col in unknown:
      if (row, col) in corner_cells:
        suggestions.append({
          'row': row,
          'col': col,
          'probability': 60,
          'reason': '角落位置，相对安全'
        })
      elif row == 0 or row == rows-1 or col == 0 or col == cols-1:
        suggestions.append({
          'row': row,
          'col': col,
          'probability': 55,
          'reason': '边缘位置，邻居较少'
        })
    
    # 如果没有边缘格子，随机选择
    if not suggestions and unknown:
      for row, col in unknown[:3]:
        suggestions.append({
          'row': row,
          'col': col,
          'probability': 50,
          'reason': '需要尝试运气'
        })
    
    return {
      'suggestions': suggestions[:5],
      'analysis': '无明确推理依据，建议尝试边缘或角落位置'
    }


