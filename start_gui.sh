#!/bin/bash

echo "===================================="
echo "  扫雷游戏 + AI智能提示"
echo "===================================="
echo ""
echo "正在启动游戏..."
echo ""

python3 run.py

if [ $? -ne 0 ]; then
    echo ""
    echo "错误：程序运行失败！"
    echo ""
    echo "可能的原因："
    echo "1. 未安装Python 3"
    echo "2. 未安装依赖包"
    echo ""
    echo "解决方案："
    echo "1. 确保已安装Python 3.7+"
    echo "2. 运行: pip3 install -r requirements.txt"
    echo ""
    read -p "按任意键继续..."
fi

