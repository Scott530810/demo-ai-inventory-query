# 推送到 GitHub 指南

## 🚀 準備推送到 GitHub

您的本機 Git 已經準備好，現在只需要 3 個步驟就能推送到 GitHub！

---

## 步驟 1: 在 GitHub 創建 Repository

### 選項 A: 通過網頁創建（推薦）

1. 前往 https://github.com/new
2. 填寫資訊：
   - **Repository name**: `ambulance-inventory-query`（或您喜歡的名稱）
   - **Description**: `Natural language to SQL query system using Ollama (qwen3:30b)`
   - **Visibility**:
     - 選 **Public** = 所有人可見（適合作品集）
     - 選 **Private** = 只有您可見（完全私密）
   - ⚠️ **重要**: 不要勾選以下選項：
     - [ ] Add a README file
     - [ ] Add .gitignore
     - [ ] Choose a license

3. 點擊 **Create repository**

### 選項 B: 使用 GitHub CLI（進階）

```bash
gh repo create ambulance-inventory-query --public --source=. --remote=origin --push
```

---

## 步驟 2: 推送到 GitHub

GitHub 創建完成後，會顯示 repository URL，類似：
```
https://github.com/Scott530810/ambulance-inventory-query.git
```

### 執行推送命令

```bash
cd "c:\Users\scott\Desktop\files (1)"

# 添加 GitHub 作為遠端 repository
git remote add origin https://github.com/Scott530810/REPO_NAME.git

# 推送所有提交
git push -u origin master
```

⚠️ **替換 `REPO_NAME`** 為您實際的 repository 名稱！

---

## 步驟 3: 處理認證

GitHub 已不再接受密碼認證，您需要選擇以下方式之一：

### 方式 A: GitHub Desktop（最簡單）⭐ 推薦

1. 下載安裝: https://desktop.github.com/
2. 登入您的 GitHub 帳戶
3. File → Add Local Repository
4. 選擇 `c:\Users\scott\Desktop\files (1)`
5. 點擊 "Publish repository"
6. ✅ 完成！

### 方式 B: Personal Access Token (PAT)

1. 前往 https://github.com/settings/tokens
2. 點擊 "Generate new token" → "Generate new token (classic)"
3. 設定：
   - **Note**: `Ambulance Inventory System`
   - **Expiration**: 選擇過期時間（建議 90 days）
   - **Select scopes**: 勾選 `repo`（完整的 repository 權限）
4. 點擊 "Generate token"
5. ⚠️ **複製 token**（只會顯示一次！）

然後使用 token 推送：

```bash
# 方法 1: 使用 token 作為密碼
git remote add origin https://github.com/Scott530810/REPO_NAME.git
git push -u origin master
# 當要求輸入密碼時，貼上 token

# 方法 2: 直接在 URL 中包含 token
git remote add origin https://Scott530810:YOUR_TOKEN_HERE@github.com/Scott530810/REPO_NAME.git
git push -u origin master
```

### 方式 C: SSH Key（最安全）

1. 生成 SSH key：
```bash
ssh-keygen -t ed25519 -C "scott@lapspeedtrading.com"
# 按 Enter 使用預設路徑
# 設定 passphrase（或直接按 Enter 跳過）
```

2. 複製公鑰：
```bash
cat ~/.ssh/id_ed25519.pub
```

3. 前往 https://github.com/settings/keys
4. 點擊 "New SSH key"
5. 貼上公鑰並儲存

6. 使用 SSH URL 推送：
```bash
git remote add origin git@github.com:Scott530810/REPO_NAME.git
git push -u origin master
```

---

## 🎯 完整推送命令（選擇您的方式）

### 使用 HTTPS + Token
```bash
cd "c:\Users\scott\Desktop\files (1)"

# 1. 添加遠端（替換 REPO_NAME 和 YOUR_TOKEN）
git remote add origin https://Scott530810:YOUR_TOKEN@github.com/Scott530810/REPO_NAME.git

# 2. 推送
git push -u origin master

# 3. 確認推送成功
git remote -v
```

### 使用 SSH
```bash
cd "c:\Users\scott\Desktop\files (1)"

# 1. 添加遠端（替換 REPO_NAME）
git remote add origin git@github.com:Scott530810/REPO_NAME.git

# 2. 推送
git push -u origin master

# 3. 確認推送成功
git remote -v
```

---

## ✅ 確認推送成功

推送成功後，您應該看到：

```
Enumerating objects: 42, done.
Counting objects: 100% (42/42), done.
Delta compression using up to 8 threads
Compressing objects: 100% (36/36), done.
Writing objects: 100% (42/42), 15.23 KiB | 1.23 MiB/s, done.
Total 42 (delta 8), reused 0 (delta 0), pack-reused 0
To https://github.com/Scott530810/REPO_NAME.git
 * [new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

然後訪問您的 repository:
```
https://github.com/Scott530810/REPO_NAME
```

您應該能看到：
- ✅ README.md 顯示在首頁
- ✅ 所有文件和資料夾
- ✅ 4 次提交記錄
- ✅ 完整的專案結構

---

## 🎨 推送後的設定

### 1. 添加 Topics（標籤）

在 repository 頁面右側：
1. 點擊 ⚙️ 齒輪圖示
2. 添加 topics:
   - `python`
   - `ollama`
   - `postgresql`
   - `docker`
   - `nlp`
   - `natural-language-processing`
   - `sql-generator`
   - `llm`
   - `qwen`

### 2. 添加 License（可選）

如果想要開源：
1. 點擊 "Add file" → "Create new file"
2. 檔名: `LICENSE`
3. 點擊右側 "Choose a license template"
4. 選擇 "MIT License"
5. Commit

### 3. 設定 Repository 說明

在 repository 頁面：
1. 點擊右上角 ⚙️ Settings
2. 找到 "About" 區塊
3. 點擊 ⚙️ 編輯
4. 添加：
   - Description: `Natural language to SQL query system for ambulance equipment inventory using Ollama (qwen3:30b)`
   - Website: （如果有的話）
   - Topics: 如上方列表

---

## 🔄 日後的推送流程

設定好遠端後，日常推送非常簡單：

```bash
# 1. 修改代碼
# 2. 提交到本機 Git
git add .
git commit -m "feat: Add new feature"

# 3. 推送到 GitHub
git push

# 就這麼簡單！✨
```

---

## 🌿 分支管理

### 創建新分支並推送

```bash
# 創建並切換到新分支
git checkout -b feature/new-feature

# 進行開發...
git add .
git commit -m "feat: Implement new feature"

# 推送新分支到 GitHub
git push -u origin feature/new-feature
```

### 在 GitHub 上創建 Pull Request

1. 前往 repository 頁面
2. 點擊 "Pull requests" → "New pull request"
3. 選擇分支
4. 填寫 PR 說明
5. 點擊 "Create pull request"

---

## 🔧 常見問題

### Q1: 推送時提示 "remote origin already exists"

```bash
# 查看現有遠端
git remote -v

# 移除現有遠端
git remote remove origin

# 重新添加
git remote add origin https://github.com/Scott530810/REPO_NAME.git
```

### Q2: 推送時提示 "Updates were rejected"

這表示 GitHub 上有您本機沒有的提交（通常不會發生在新 repo）

```bash
# 拉取並合併
git pull origin master --allow-unrelated-histories

# 然後重新推送
git push -u origin master
```

### Q3: 忘記 Token 或想更換

1. 前往 https://github.com/settings/tokens
2. 刪除舊 token
3. 生成新 token
4. 更新遠端 URL：
```bash
git remote set-url origin https://Scott530810:NEW_TOKEN@github.com/Scott530810/REPO_NAME.git
```

### Q4: 想要修改 repository 名稱

1. 在 GitHub 上: Settings → Repository name → Rename
2. 更新本機遠端 URL:
```bash
git remote set-url origin https://github.com/Scott530810/NEW_REPO_NAME.git
```

---

## 📊 推送內容總覽

您將推送：
- ✅ 4 次提交記錄
- ✅ 36 個文件
- ✅ 完整的版本歷史
- ✅ 所有文檔和代碼

推送的文件包括：
- 📦 模組化代碼（11 個 Python 文件）
- 📝 專業文檔（9 個 Markdown 文件）
- 🐳 Docker 配置
- 🔧 備份腳本
- 📋 配置文件

---

## 🎯 準備好了嗎？

選擇您的推送方式：

### 最簡單：GitHub Desktop
1. 下載安裝 GitHub Desktop
2. 登入
3. Add Local Repository
4. Publish ✅

### 稍微複雜：命令列 + Token
1. 在 GitHub 創建 repository
2. 生成 Personal Access Token
3. 執行推送命令

### 進階用戶：SSH
1. 生成 SSH key
2. 添加到 GitHub
3. 使用 SSH URL 推送

---

**準備好後告訴我，我會協助您完成推送！** 🚀
