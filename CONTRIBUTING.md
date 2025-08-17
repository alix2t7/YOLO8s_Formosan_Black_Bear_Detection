# Contributing to YOLOv8s Bear Detection Pipeline

我們歡迎您對 YOLOv8s 台灣黑熊檢測訓練系統的貢獻！

## 📋 貢獻方式

### 🐛 回報問題 (Bug Reports)

如果您發現了問題，請創建一個 Issue 並包含：

- **問題描述**: 清楚描述發生了什麼
- **重現步驟**: 詳細的重現步驟
- **預期行為**: 您期望的正確行為
- **環境資訊**: 
  - Python 版本
  - 操作系統
  - GPU/CUDA 版本 (如適用)
  - 依賴包版本

### 💡 功能建議 (Feature Requests)

我們歡迎新功能的建議！請創建 Issue 並包含：

- **功能描述**: 詳細描述建議的功能
- **使用案例**: 說明此功能的用途和價值
- **實現想法**: 如果有的話，提供實現的想法

### 🔧 程式碼貢獻 (Code Contributions)

1. **Fork 此專案**
2. **創建功能分支**: `git checkout -b feature/amazing-feature`
3. **提交您的修改**: `git commit -m 'Add some amazing feature'`
4. **推送到分支**: `git push origin feature/amazing-feature`
5. **創建 Pull Request**

## 🏗️ 開發環境設置

### 前置需求

- Python 3.8+
- Git
- GPU (推薦，但非必需)

### 設置步驟

1. **複製專案**:
```bash
git clone https://github.com/yourusername/YOLOv8s_0808_pipeline.git
cd YOLOv8s_0808_pipeline
```

2. **創建虛擬環境**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安裝依賴**:
```bash
pip install -r requirements.txt
```

4. **執行測試**:
```bash
python main.py --mode setup
```

## 📝 編碼規範

### Python 編碼風格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 風格指南
- 使用有意義的變數和函數名稱
- 添加適當的註釋和文檔字符串
- 保持函數簡潔，單一職責

### 程式碼結構

```python
"""模組級別的文檔字符串。

描述模組的用途和主要功能。
"""

import os
from typing import Dict, Any

class ExampleClass:
    """類的文檔字符串。
    
    描述類的用途和主要方法。
    
    Args:
        param1: 參數描述
        param2: 參數描述
    """
    
    def __init__(self, param1: str, param2: int):
        self.param1 = param1
        self.param2 = param2
    
    def example_method(self) -> Dict[str, Any]:
        """方法的文檔字符串。
        
        Returns:
            Dict[str, Any]: 返回值描述
        """
        return {"result": "success"}
```

### 提交訊息格式

使用清楚的提交訊息：

```
feat: 添加新的資料增強功能
fix: 修復超參數優化中的記憶體洩漏
docs: 更新安裝指南
style: 修正程式碼格式
refactor: 重構訓練循環邏輯
test: 添加資料驗證的單元測試
```

## 🧪 測試

### 執行測試

```bash
# 執行所有測試
python -m pytest

# 執行特定模組測試
python main.py --mode validate

# 執行環境測試
python main.py --mode setup
```

### 添加測試

為新功能添加適當的測試：

1. 單元測試放在 `tests/` 目錄
2. 集成測試使用真實資料
3. 確保測試覆蓋率足夠

## 📚 文檔

### 更新文檔

- 更新 `README.md` 如果添加新功能
- 更新 `CHANGELOG.md` 記錄變更
- 確保程式碼註釋是最新的
- 添加或更新配置檔案說明

### 撰寫文檔

- 使用清楚簡潔的語言
- 提供實際的使用範例
- 包含必要的截圖或圖表
- 保持中英文一致性

## ✅ Pull Request 檢查清單

提交 PR 前請確認：

- [ ] 程式碼遵循專案的編碼規範
- [ ] 添加了必要的測試
- [ ] 測試全部通過
- [ ] 更新了相關文檔
- [ ] 提交訊息清楚描述變更
- [ ] 沒有合併衝突
- [ ] PR 描述清楚說明變更內容

## 🤝 程式碼審查

### 審查標準

- **功能性**: 程式碼是否正確實現了預期功能
- **可讀性**: 程式碼是否易於理解和維護
- **效能**: 是否有效能問題或改善空間
- **安全性**: 是否有安全風險
- **一致性**: 是否符合專案的風格和架構

### 回應反饋

- 積極回應審查意見
- 解釋設計決策的原因
- 及時修正發現的問題
- 感謝審查者的時間和建議

## 🆘 需要幫助？

如果您有任何問題：

1. 查看現有的 [Issues](https://github.com/alix2t7/YOLO8s_Formosan_Black_Bear_Detection/issues)
2. 查看 [README.md](README.md) 和相關文檔
3. 創建新的 Issue 詢問問題
4. 加入我們的討論區

## 📄 授權

貢獻此專案即表示您同意您的貢獻將在與專案相同的 [MIT License](LICENSE) 下發布。

---

感謝您對改進 YOLOv8s 台灣黑熊檢測系統的貢獻！🐻 🚀
