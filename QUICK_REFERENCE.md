# 快速參考卡 📋

## 🎊 您的系統已完全設置完成！

**版本**: 2.0.0
**模式**: 本機私密 Git + 定期備份
**狀態**: ✅ 生產就緒

---

## 🚀 **快速啟動命令**

### 運行系統

```bash
# 方式 1: 本機運行
python run_refactored.py --interactive

# 方式 2: Docker 運行
docker-compose -f docker-compose.ollama.yml up -d
docker exec -it ambulance-query-ollama python run_refactored.py --interactive
```

---

## 💾 **Git 日常使用**

```bash
# 進入專案目錄
cd "c:\Users\scott\Desktop\files (1)"

# 查看狀態
git status

# 提交變更
git add .
git commit -m "feat: Your message"

# 查看歷史
git log --oneline
```

---

## 🗂️ **備份**

### 備份到外接硬碟
```powershell
.\backup-to-external.ps1
```

### 備份到 NAS
```powershell
# 先編輯腳本修改 NAS 路徑
.\backup-to-nas.ps1
```

---

## 📚 **完整文檔**

| 文檔 | 用途 |
|------|------|
| [QUICK_START.md](QUICK_START.md) | 快速入門 |
| [LOCAL_GIT_GUIDE.md](LOCAL_GIT_GUIDE.md) | 本機 Git 完整指南 ⭐ |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系統架構 |
| [REFACTOR_GUIDE.md](REFACTOR_GUIDE.md) | 重構說明 |
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Docker 使用 |
| [CHANGELOG.md](CHANGELOG.md) | 版本歷史 |

---

## 🛠️ **系統模式**

```bash
--check        # 系統檢查
--demo         # Demo 模式（5 個範例查詢）
--interactive  # 互動模式（推薦）
```

---

## 📁 **專案結構**

```
ambulance_inventory/    # 核心模組（11 個文件）
├── config.py          # 配置
├── database.py        # 資料庫
├── ollama_client.py   # Ollama API
├── query_engine.py    # 查詢引擎
├── main.py           # 主程式
├── ui/               # 使用者介面
└── utils/            # 工具函數

文檔/
├── README.md         # 專案說明
├── LOCAL_GIT_GUIDE.md    # Git 指南 ⭐
├── QUICK_START.md    # 快速開始
└── ...

備份工具/
├── backup-to-external.ps1  # 外接硬碟備份
└── backup-to-nas.ps1       # NAS 備份
```

---

## 🎯 **建議的工作流程**

### 每日
1. 開始工作前: `git status`
2. 完成功能後: `git commit -m "feat: XXX"`
3. 工作結束: 檢查 `git log`

### 每週
1. 執行備份: `.\backup-to-external.ps1`
2. 檢查備份: 確認外接硬碟有最新備份

### 每月
1. 查看歷史: `git log --oneline --graph`
2. 清理工作區: `git clean -n` 檢查後 `git clean -fd`

---

## 🔥 **常用命令**

```bash
# Git
git status              # 查看狀態
git log --oneline      # 查看歷史
git diff               # 查看變更
git add .              # 添加所有
git commit -m "msg"    # 提交

# 系統
python run_refactored.py --check      # 檢查
python run_refactored.py --interactive # 互動

# Docker
docker-compose -f docker-compose.ollama.yml up -d    # 啟動
docker-compose -f docker-compose.ollama.yml down     # 停止
docker exec -it ambulance-query-ollama bash          # 進入容器
```

---

## 💡 **提示**

- 📖 不確定怎麼用？看 [LOCAL_GIT_GUIDE.md](LOCAL_GIT_GUIDE.md)
- 🐛 遇到問題？運行 `--check` 模式
- 💾 記得定期備份！
- 🌿 大功能？創建分支: `git checkout -b feature-xxx`

---

## 📞 **需要幫助？**

1. 查看 [LOCAL_GIT_GUIDE.md](LOCAL_GIT_GUIDE.md) - 完整的 Git 使用指南
2. 查看 [QUICK_START.md](QUICK_START.md) - 系統使用說明
3. 運行 `python run_refactored.py --check` - 系統診斷

---

**版本**: 2.0.0
**更新**: 2026-01-14
**模式**: 本機私密
**Git 提交**: 3 個

🎉 **一切就緒，開始使用吧！**
