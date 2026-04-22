#!/bin/bash
# 图片样本筛选器启动脚本

# 设置编码
export LANG=en_US.UTF-8

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "未找到虚拟环境，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败，请确认已安装 Python 3 并加入 PATH。"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否已安装
pip show pillow > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装依赖库（pillow）..."
    pip install -r requirements.txt
fi

# 运行主程序
python main.py

# 程序结束后等待用户按键（可选）
echo "程序已退出。按任意键关闭..."
read -n 1