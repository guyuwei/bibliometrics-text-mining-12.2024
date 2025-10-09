#!/bin/bash

# 文本挖掘和文献分析系统启动脚本
# 自动关闭之前的实例并启动新实例

echo "🔄 正在关闭之前的Streamlit实例..."
pkill -f streamlit

# 等待进程完全关闭
sleep 2

echo "🚀 启动文本挖掘和文献分析系统..."
cd /Users/gyw/Desktop/Project/2025/zyj_text_mining/Program

# 启动Streamlit应用程序
streamlit run main.py

echo "✅ 应用程序已启动！"
echo "🌐 本地访问地址: http://localhost:8501"
echo "🌐 网络访问地址: http://198.18.0.1:8501"
