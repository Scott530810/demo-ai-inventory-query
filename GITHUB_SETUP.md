# GitHub 設置指南

## ✅ Git 已準備完成！

您的本地 Git repository 已經設置完成，包含：
- ✅ 2 個提交記錄
- ✅ 33 個文件
- ✅ 完整的 .gitignore
- ✅ 專業的 README.md

---

## 🚀 推送到 GitHub

### 步驟 1: 在 GitHub 創建 Repository

1. 前往 [GitHub](https://github.com/)
2. 點擊右上角的 **+** → **New repository**
3. 填寫資訊：
   - **Repository name**: `ambulance-inventory` (或您喜歡的名稱)
   - **Description**: `Natural language to SQL query system for ambulance equipment inventory using Ollama`
   - **Visibility**: 選擇 Public 或 Private
   - **⚠️ 不要勾選**: "Add a README file"
   - **⚠️ 不要勾選**: "Add .gitignore"
   - **⚠️ 不要勾選**: "Choose a license"
4. 點擊 **Create repository**

### 步驟 2: 推送本地代碼到 GitHub

GitHub 會顯示指令，或者您可以直接使用以下命令：

```bash
# 在專案目錄中執行
cd "c:\Users\scott\Desktop\files (1)"

# 添加遠端 repository（替換 YOUR_REPO_NAME 為您的 repository 名稱）
git remote add origin https://github.com/Scott530810/YOUR_REPO_NAME.git

# 推送到 GitHub
git push -u origin master
```

### 步驟 2-1: 如果出現認證問題

GitHub 現在需要使用 Personal Access Token (PAT) 而不是密碼。

#### 方法 A: 使用 GitHub Desktop（推薦，最簡單）

1. 下載並安裝 [GitHub Desktop](https://desktop.github.com/)
2. 登入您的 GitHub 帳戶
3. File → Add Local Repository → 選擇專案資料夾
4. 點擊 "Publish repository"

#### 方法 B: 使用 Personal Access Token

1. 前往 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 點擊 "Generate new token (classic)"
3. 設定：
   - Note: `Ambulance Inventory System`
   - Expiration: 選擇過期時間
   - 勾選: `repo` (完整的 repository 權限)
4. 點擊 "Generate token"
5. **⚠️ 複製並保存 token（只會顯示一次！）**

然後使用：
```bash
# 添加遠端（使用 token）
git remote add origin https://Scott530810:YOUR_TOKEN_HERE@github.com/Scott530810/YOUR_REPO_NAME.git

# 推送
git push -u origin master
```

#### 方法 C: 使用 SSH

```bash
# 生成 SSH key（如果還沒有）
ssh-keygen -t ed25519 -C "scott@lapspeedtrading.com"

# 複製公鑰
cat ~/.ssh/id_ed25519.pub

# 前往 GitHub → Settings → SSH and GPG keys → New SSH key
# 貼上公鑰並保存

# 添加遠端（使用 SSH）
git remote add origin git@github.com:Scott530810/YOUR_REPO_NAME.git

# 推送
git push -u origin master
```

---

## 📝 完整命令範例

```bash
# 1. 進入專案目錄
cd "c:\Users\scott\Desktop\files (1)"

# 2. 確認 Git 狀態
git status
git log --oneline

# 3. 添加遠端 repository（替換為您的 repo URL）
git remote add origin https://github.com/Scott530810/ambulance-inventory.git

# 4. 確認遠端設定
git remote -v

# 5. 推送到 GitHub
git push -u origin master

# 6. 查看推送結果
# 應該看到類似：
# Enumerating objects: 42, done.
# Counting objects: 100% (42/42), done.
# ...
# To https://github.com/Scott530810/ambulance-inventory.git
#  * [new branch]      master -> master
```

---

## 🎨 推送後的工作

### 1. 查看您的 Repository

訪問: `https://github.com/Scott530810/YOUR_REPO_NAME`

應該可以看到：
- ✅ README.md 顯示在首頁
- ✅ 所有文件和資料夾
- ✅ 提交歷史

### 2. 添加 Topics（標籤）

在 repository 頁面：
1. 點擊右側的 ⚙️（Settings）旁的齒輪
2. 添加 topics: `python`, `ollama`, `postgresql`, `docker`, `nlp`, `sql-generator`

### 3. 添加 License（可選）

如果想要開源：
1. 在 repository 頁面點擊 "Add file" → "Create new file"
2. 檔名輸入: `LICENSE`
3. 右側點擊 "Choose a license template"
4. 選擇 MIT License
5. Commit

### 4. 更新 README.md 中的連結

如果 repository 名稱不是 `ambulance-inventory`，需要更新 README.md：

```bash
# 編輯 README.md，將所有
# https://github.com/Scott530810/ambulance-inventory
# 替換為您的實際 repository URL

# 然後提交更新
git add README.md
git commit -m "docs: Update repository URLs in README"
git push
```

---

## 🔄 日常 Git 工作流程

### 修改代碼後

```bash
# 1. 查看更改
git status
git diff

# 2. 添加更改
git add .
# 或只添加特定文件
git add ambulance_inventory/config.py

# 3. 提交
git commit -m "feat: Add new feature"

# 4. 推送到 GitHub
git push
```

### 提交訊息規範

使用 Conventional Commits 格式：

- `feat:` - 新功能
- `fix:` - 錯誤修復
- `docs:` - 文檔更新
- `style:` - 代碼格式（不影響功能）
- `refactor:` - 重構
- `test:` - 測試
- `chore:` - 其他雜項

範例：
```bash
git commit -m "feat: Add query result caching with Redis"
git commit -m "fix: Resolve SQL injection vulnerability"
git commit -m "docs: Update installation instructions"
```

---

## 🌿 分支管理

### 創建功能分支

```bash
# 創建並切換到新分支
git checkout -b feature/add-web-api

# 進行開發...
git add .
git commit -m "feat: Implement FastAPI web endpoints"

# 推送分支到 GitHub
git push -u origin feature/add-web-api

# 在 GitHub 上創建 Pull Request
```

### 切換回主分支

```bash
git checkout master
git pull  # 獲取最新更改
```

---

## 📊 查看歷史和狀態

```bash
# 查看提交歷史
git log --oneline --graph

# 查看特定文件的歷史
git log --oneline -- ambulance_inventory/config.py

# 查看某次提交的詳細內容
git show COMMIT_HASH

# 查看所有分支
git branch -a

# 查看遠端連接
git remote -v
```

---

## ⚠️ 常見問題

### Q1: 推送時要求輸入用戶名密碼，但密碼錯誤

**A**: GitHub 已停用密碼認證，需要使用 Personal Access Token 或 SSH。
參考上方「步驟 2-1: 如果出現認證問題」。

### Q2: 推送時出現 "Updates were rejected"

**A**: 遠端有更新，需要先拉取：
```bash
git pull --rebase origin master
git push
```

### Q3: 不小心提交了敏感資訊（密碼、token 等）

**A**:
```bash
# 如果還沒推送
git reset --soft HEAD~1  # 撤銷最後一次提交
# 修改文件
git add .
git commit -m "fix: Remove sensitive data"

# 如果已經推送，需要 force push（危險！）
# 建議聯繫 GitHub Support 或使用 BFG Repo-Cleaner
```

### Q4: 想要忽略某些文件

**A**: 編輯 `.gitignore`，然後：
```bash
git rm --cached FILE_NAME  # 從 Git 移除但保留本地文件
git commit -m "chore: Update .gitignore"
git push
```

---

## 🎯 現在就試試！

```bash
# 複製以下命令，替換 YOUR_REPO_NAME
cd "c:\Users\scott\Desktop\files (1)"
git remote add origin https://github.com/Scott530810/YOUR_REPO_NAME.git
git push -u origin master
```

**成功後，您的代碼就在 GitHub 上了！** 🎉

---

## 📚 更多資源

- [GitHub Docs](https://docs.github.com/)
- [Git 教學](https://git-scm.com/book/zh-tw/v2)
- [GitHub Desktop](https://desktop.github.com/)

---

**配置完成日期**: 2026-01-14
**Git 用戶**: Scott530810
**Email**: scott@lapspeedtrading.com
