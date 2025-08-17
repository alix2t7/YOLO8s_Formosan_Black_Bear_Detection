#!/bin/bash

# YOLOv8s 熊類檢測 Pipeline 快速啟動腳本

echo "🐻 YOLOv8s Bear Detection Pipeline"
echo "=================================="

# 檢查 Python 版本
echo "🔍 檢查 Python 環境..."
python --version

# 安裝依賴
echo "📦 安裝依賴套件..."
pip install -r requirements.txt

# 創建必要目錄
echo "📁 創建工作目錄..."
mkdir -p results/training results/optimization checkpoints logs

echo "✅ 環境準備完成！"
echo ""
echo "使用方式："
echo "  python main.py --mode full      # 執行完整流程"
echo "  python main.py --mode setup     # 僅環境設置"
echo "  python main.py --mode validate  # 僅數據驗證"  
echo "  python main.py --mode optimize  # 僅超參優化"
echo "  python main.py --mode train     # 僅模型訓練"
echo ""
echo "🚀 準備開始訓練！"
