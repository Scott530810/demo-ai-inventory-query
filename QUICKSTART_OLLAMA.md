# 🎯 Ollama 本地端版本 - 5分鐘快速開始

## ✨ 恭喜！您選擇了最佳方案

**您的配置：**
- ✅ Windows 11
- ✅ AMD Ryzen AI 7
- ✅ RTX 5070 (完美！)
- ✅ 已在用 Ollama + qwen2.5:32b

**這個組合運行本地 LLM 完全沒問題！**

---

## 🚀 三步驟啟動

### 第一步：確認 Ollama 設定（重要！）

**設定 Ollama 允許外部訪問：**

```powershell
# 在 PowerShell（管理員模式）執行
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
```

**然後重啟 Ollama：**
1. 關閉 Ollama（系統托盤右鍵 → Quit）
2. 重新開啟 Ollama

**驗證：**
```powershell
curl http://localhost:11434/api/tags
# 應該看到您已安裝的模型列表
```

---

### 第二步：啟動系統

**PowerShell（推薦）：**
```powershell
cd C:\Users\scott\Desktop\庫存查詢Demo
.\run-ollama.ps1
```

**選單：**
```
選擇 1 → 啟動系統
等待 10 秒...
```

---

### 第三步：系統檢查

```powershell
.\run-ollama.ps1
選擇 2 → 系統檢查
```

**會檢查：**
- ✅ 資料庫連接
- ✅ Ollama 連接
- ✅ 模型是否就緒
- ✅ 推理能力測試

**如果全部 ✅，就可以開始使用了！**

---

## 🎮 開始使用

### 方式一：執行 Demo（推薦）

```powershell
.\run-ollama.ps1
選擇 3 → 執行 Demo 查詢
```

**會自動執行 5 個查詢範例**

---

### 方式二：互動模式（最好玩）

```powershell
.\run-ollama.ps1
選擇 4 → 進入互動模式
```

**自由提問：**
```
💭 請輸入您的問題: 我需要配備一台新救護車，預算30萬，請推薦設備清單

（Ollama 會智能分析並給出完整規劃）
```

---

## 💡 試試這些問題

### 簡單查詢
- "請問 AED 除顫器還有哪幾款有庫存？"
- "Philips 的產品有哪些？"
- "哪些商品需要補貨？"

### 複雜查詢（展現 LLM 威力）
- "我需要配備新救護車，預算 15 萬，請推薦設備清單"
- "比較 Philips 和 ZOLL 的 AED 優缺點"
- "為新手推薦一套基本急救設備"
- "分析各品牌的價格競爭力"

---

## ⚡ 效能參考

**您的 RTX 5070 表現：**
- 模型載入：5-10秒（首次）
- 簡單查詢：5-8秒
- 複雜查詢：10-15秒

**完全可接受！而且完全免費！**

---

## 🔧 常見問題

### ❌ "無法連接到 Ollama"

**解決：**
1. 確認 Ollama 正在運行（檢查系統托盤）
2. 確認已設定 `OLLAMA_HOST=0.0.0.0`
3. 重啟 Ollama

---

### ❌ "模型未找到"

**解決：**
```powershell
# 下載模型（約 19GB）
ollama pull qwen2.5:32b
```

---

### ❌ "VRAM 不足"

**解決：**
```powershell
# 使用更小的模型
ollama pull qwen2.5:14b  # 只需 8GB VRAM

# 然後修改 docker-compose.ollama.yml
# OLLAMA_MODEL: qwen2.5:14b
```

---

## 📊 與其他版本對比

| | 假 Demo | OpenAI | **Ollama 本地** |
|---|---|---|---|
| 成本 | 免費 | ~$3/月 | **免費** ✅ |
| 隱私 | 安全 | 上雲 | **完全本地** ✅ |
| 速度 | 極快 | 快 | **快** ✅ |
| 離線 | ✅ | ❌ | **✅** |
| 複雜查詢 | ❌ | ✅ | **✅** |

**Ollama 本地端 = 最佳選擇！**

---

## 🎯 完整命令流程

```powershell
# 1. 確認 Ollama 設定
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
# 重啟 Ollama

# 2. 啟動系統
cd C:\Users\scott\Desktop\庫存查詢Demo
.\run-ollama.ps1
選擇 1

# 3. 系統檢查
.\run-ollama.ps1
選擇 2

# 4. 開始使用
.\run-ollama.ps1
選擇 4  # 互動模式

# 5. 提問
💭 我需要配備新救護車，預算30萬，請推薦
```

---

## 📚 詳細說明

完整文檔請看：`README_OLLAMA.md`

---

## 🎉 開始吧！

```powershell
.\run-ollama.ps1
```

**享受完全免費、隱私安全的本地端 AI！** 🚀

---

## 💬 需要幫助？

檢查這些檔案：
- `README_OLLAMA.md` - 完整說明
- `COMPARISON.md` - 版本對比
- `docker-compose.ollama.yml` - Docker 配置

**祝您使用愉快！** ✨
