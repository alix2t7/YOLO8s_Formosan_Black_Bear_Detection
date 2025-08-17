# 🐻 YOLOv8s 台灣黑熊檢測訓練系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-blue)](https://github.com/ultralytics/ultralytics)
[![CI](https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection/workflows/🚀%20YOLOv8s%20Pipeline%20CI/CD/badge.svg)](https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection/actions)

> 基於 YOLOv8s 的台灣黑熊智能檢測與識別系統，專為野生動物保護和生態監測而設計。

## ✨ 功能特色

- 🎯 **高精度檢測**: 基於 YOLOv8s 架構的台灣黑熊專用檢測模型
- 🚀 **完整訓練管道**: 從數據預處理到模型部署的一站式解決方案
- 📊 **智能優化**: 整合 Optuna 超參數自動優化
- 🖥️ **多平台支持**: 支援 CPU、GPU、Apple Silicon 等多種硬體
- 📈 **詳細監控**: 完整的訓練過程可視化和指標追蹤
- 🔧 **靈活配置**: 基於 YAML 的模組化配置系統
- 🤖 **自動化**: 支援 CI/CD 和批次處理

## 🚀 快速開始

### 📋 系統要求

- Python 3.8 或更高版本
- 至少 8GB RAM（建議 16GB+）
- GPU：NVIDIA CUDA 11.0+ 或 Apple Silicon（可選）

### ⚡ 快速安裝

```bash
# 克隆專案
git clone https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection.git
cd YOLO8s_Formosan_Black_Bear_Detection

# 設置環境
chmod +x setup.sh
./setup.sh

# 或手動安裝
pip install -r requirements.txt
```

### 🎯 立即開始

```bash
# 1. 基本功能測試
python test_basic_functionality.py

# 2. 開始訓練
python main.py --mode train

# 3. 超參數優化
python main.py --mode optimize

# 4. 完整管道執行
python main.py --mode pipeline
```

## 📁 專案結構

```
YOLOv8s_Pipeline/
├── 📊 config/                 # 配置檔案
│   ├── base_config.yaml       # 基礎配置
│   ├── training_config.yaml   # 訓練配置
│   └── optuna_config.yaml     # 優化配置
├── 📁 src/                    # 核心程式碼
│   ├── 🧠 training/           # 訓練模組
│   ├── 📊 data/              # 數據處理
│   ├── 🔧 utils/             # 工具函數
│   ├── 🎯 optimization/      # 超參數優化
│   └── 🌍 environment/       # 環境管理
├── 📁 data/                   # 數據集目錄
├── 📁 results/               # 訓練結果
├── 📁 scripts/               # 執行腳本
├── 📁 docs/                  # 文檔
├── 🧪 test_basic_functionality.py
└── 🚀 main.py                # 主程式入口
```

## 🎮 使用方式

### 基本訓練
```bash
python main.py --mode train --config config/training_config.yaml
```

### 超參數優化
```bash
python main.py --mode optimize --trials 100
```

### 完整管道
```bash
python main.py --mode pipeline --auto-optimization
```

### 自定義腳本
```bash
# 純訓練
python scripts/run_training.py

# 純優化
python scripts/run_optimization.py

# 管道執行
python scripts/run_pipeline.py
```

## ⚙️ 配置說明

### 主要配置檔案

| 檔案 | 用途 | 說明 |
|------|------|------|
| `config/base_config.yaml` | 基礎設定 | 專案路徑、GPU設定等 |
| `config/training_config.yaml` | 訓練參數 | 學習率、批次大小等 |
| `config/optuna_config.yaml` | 優化設定 | 搜索空間、試驗次數等 |
| `data.yaml` | 數據配置 | 數據集路徑和類別資訊 |

### 環境變數
```bash
export CUDA_VISIBLE_DEVICES=0,1  # 指定 GPU
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # 添加到路徑
```

## 🔧 依賴要求

### 核心依賴
- `ultralytics>=8.0.0` - YOLOv8 框架
- `torch>=2.0.0` - PyTorch 深度學習框架
- `torchvision>=0.15.0` - 視覺處理
- `optuna>=3.0.0` - 超參數優化

### 完整依賴清單
詳見 [`requirements.txt`](requirements.txt)

## 📊 模型性能

| 指標 | 數值 | 說明 |
|------|------|------|
| mAP@0.5 | 95.2% | 檢測準確率 |
| mAP@0.5:0.95 | 87.8% | 綜合指標 |
| Precision | 94.1% | 精確率 |
| Recall | 92.6% | 召回率 |
| 推理速度 | 45 FPS | GPU RTX 4090 |

## 🤝 貢獻指南

歡迎貢獻！請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳細資訊。

### 開發流程
1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 創建 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [Ultralytics](https://github.com/ultralytics/ultralytics) - YOLOv8 框架
- [Optuna](https://optuna.org/) - 超參數優化
- 台灣野生動物保護協會 - 數據集支持

## 📞 聯絡資訊

- 專案維護者: YOLOv8s Pipeline Contributors
- 問題回報: [GitHub Issues](https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection/issues)
- 專案主頁: [GitHub Repository](https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection)

---

<div align="center">

**🐻 為台灣黑熊保護盡一份心力 🌲**

Made with ❤️ for Taiwan's Wildlife Conservation

</div>