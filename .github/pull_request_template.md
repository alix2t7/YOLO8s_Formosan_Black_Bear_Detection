---
name: 📋 Pull Request
about: 提交程式碼更改或新功能
title: '[PR] '
labels: ['pull-request']
assignees: ''

---

## 📋 變更摘要

**簡述此 PR 的變更內容**
清楚簡潔地描述此 Pull Request 的主要變更。

## 🔗 相關 Issue

**此 PR 解決了哪些 Issue**

- Fixes #(issue number)
- Closes #(issue number)
- Related to #(issue number)

## 🎯 變更類型

**請勾選適用的變更類型**

- [ ] 🐛 Bug fix（修復現有功能的錯誤）
- [ ] ✨ New feature（添加新功能）
- [ ] 💥 Breaking change（可能影響現有功能的變更）
- [ ] 📝 Documentation（文檔更新）
- [ ] 🎨 Style（程式碼格式、不影響功能的變更）
- [ ] ♻️ Refactor（重構現有程式碼）
- [ ] ⚡ Performance（性能改進）
- [ ] ✅ Test（添加或修改測試）
- [ ] 🔧 Chore（建置程序或輔助工具的變更）

## 🔄 變更詳情

### 主要變更

- **變更一**: 詳細描述
- **變更二**: 詳細描述
- **變更三**: 詳細描述

### 檔案變更

- `src/module1.py`: 功能描述
- `config/settings.yaml`: 配置更新
- `tests/test_module1.py`: 測試添加

## 🧪 測試

**描述您進行的測試**

### 測試環境

- **作業系統**: [例如 Windows 11, macOS 13.0, Ubuntu 22.04]
- **Python 版本**: [例如 3.9.16]
- **GPU**: [例如 NVIDIA RTX 4090, Apple M2, CPU only]

### 測試類型

- [ ] 單元測試
- [ ] 整合測試
- [ ] 功能測試
- [ ] 性能測試
- [ ] 手動測試

### 測試結果

```bash
# 測試命令和結果
python -m pytest tests/ -v
```

## 🎯 測試指南

**供 reviewers 測試的步驟**

1. Checkout 此分支
2. 安裝依賴: `pip install -r requirements.txt`
3. 執行測試: `python test_basic_functionality.py`
4. 驗證功能: [具體測試步驟]

## 📸 截圖（如適用）

**如果此 PR 包含 UI 或視覺化變更，請添加截圖**

## 📋 檢查清單

### 程式碼品質

- [ ] 我的程式碼遵循專案的風格指南
- [ ] 我已執行自我程式碼審查
- [ ] 我已註解複雜或難以理解的程式碼區域
- [ ] 我的變更沒有產生新的警告或錯誤

### 測試

- [ ] 我已添加涵蓋變更的測試
- [ ] 所有新的和現有的測試都通過
- [ ] 我已驗證測試涵蓋率沒有降低

### 文檔

- [ ] 我已更新相關文檔
- [ ] 我已更新 CHANGELOG.md（如適用）
- [ ] 我已更新 README.md（如適用）

### 相容性

- [ ] 我的變更與現有功能相容
- [ ] 我已確認沒有破壞現有的 API
- [ ] 我已測試在不同 Python 版本的相容性

## 🔍 Review 重點

**請 reviewers 特別注意的地方**

- 重點關注: [特定區域或功能]
- 性能影響: [是否有性能考量]
- 安全性: [是否涉及安全變更]

## 📝 額外備註

**其他需要說明的資訊**

## 🤝 感謝

**感謝幫助此 PR 的貢獻者**

- @username1：協助功能設計
- @username2：提供測試環境
