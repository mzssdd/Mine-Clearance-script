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


