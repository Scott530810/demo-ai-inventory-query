# 本機 Git 使用指南

## 🎉 恭喜！您的本機 Git 已設置完成

您選擇了完全私密的方案：**本機 Git + 定期備份**

這是最安全、最私密的版本控制方式！

---

## ✅ 當前狀態

```
Git Repository: 已初始化 ✅
提交記錄: 2 個
追蹤文件: 33 個
用戶名: Scott530810
Email: scott@lapspeedtrading.com
```

---

## 📚 **日常使用指南**

### 基本工作流程

```bash
# 進入專案目錄
cd "c:\Users\scott\Desktop\files (1)"

# 1. 查看當前狀態
git status

# 2. 查看修改內容
git diff

# 3. 添加修改的文件
git add .                              # 添加所有修改
git add ambulance_inventory/config.py  # 只添加特定文件

# 4. 提交變更
git commit -m "feat: Add new feature"

# 5. 查看歷史
git log --oneline
```

### 提交訊息規範

使用清晰的提交訊息：

```bash
git commit -m "feat: Add query caching"           # 新功能
git commit -m "fix: Resolve database timeout"      # 錯誤修復
git commit -m "docs: Update README"                # 文檔更新
git commit -m "refactor: Simplify config loading"  # 重構
git commit -m "test: Add unit tests for validator" # 測試
git commit -m "chore: Update dependencies"         # 雜項
```

---

## 🔍 **查看歷史和變更**

### 查看提交歷史

```bash
# 簡潔格式
git log --oneline

# 圖形化顯示
git log --oneline --graph --all

# 查看最近 5 次提交
git log --oneline -5

# 查看某個文件的歷史
git log --oneline -- ambulance_inventory/config.py

# 查看某人的提交
git log --author="Scott"

# 查看某個時間範圍的提交
git log --since="2026-01-01" --until="2026-01-31"
```

### 查看變更內容

```bash
# 查看工作區的變更（還沒 add）
git diff

# 查看已暫存的變更（已 add 但還沒 commit）
git diff --staged

# 查看特定文件的變更
git diff ambulance_inventory/config.py

# 查看兩個提交之間的差異
git diff COMMIT1 COMMIT2

# 查看某次提交的詳細內容
git show COMMIT_HASH
```

### 查看文件歷史版本

```bash
# 查看某個文件在某次提交時的內容
git show COMMIT_HASH:ambulance_inventory/config.py

# 恢復某個文件到特定版本（不修改歷史）
git checkout COMMIT_HASH -- ambulance_inventory/config.py
```

---

## 🔄 **撤銷操作**

### 撤銷工作區的修改

```bash
# 撤銷單個文件的修改（還沒 add）
git checkout -- filename

# 撤銷所有修改（危險！）
git checkout -- .
```

### 撤銷暫存區的文件

```bash
# 將文件從暫存區移除（保留修改）
git reset HEAD filename

# 移除所有暫存的文件
git reset HEAD .
```

### 撤銷提交

```bash
# 撤銷最後一次提交（保留修改）
git reset --soft HEAD~1

# 撤銷最後一次提交（修改回到工作區）
git reset --mixed HEAD~1

# 撤銷最後一次提交（完全刪除）⚠️ 危險
git reset --hard HEAD~1

# 修改最後一次提交的訊息
git commit --amend -m "New message"

# 修改最後一次提交（添加遺漏的文件）
git add forgotten_file
git commit --amend --no-edit
```

---

## 🌿 **分支管理**

### 創建和切換分支

```bash
# 查看所有分支
git branch

# 創建新分支
git branch feature-xyz

# 切換分支
git checkout feature-xyz

# 創建並切換（一步完成）
git checkout -b feature-xyz

# 重命名分支
git branch -m old-name new-name
```

### 合併分支

```bash
# 切換到主分支
git checkout master

# 合併功能分支
git merge feature-xyz

# 如果有衝突，手動解決後：
git add .
git commit -m "Merge feature-xyz"
```

### 刪除分支

```bash
# 刪除已合併的分支
git branch -d feature-xyz

# 強制刪除分支（即使未合併）
git branch -D feature-xyz
```

---

## 🏷️ **標籤管理**

```bash
# 創建輕量標籤
git tag v2.0.0

# 創建註解標籤（推薦）
git tag -a v2.0.0 -m "Version 2.0.0 - Major refactor"

# 查看所有標籤
git tag

# 查看標籤詳細資訊
git show v2.0.0

# 刪除標籤
git tag -d v2.0.0

# 為過去的提交打標籤
git tag -a v1.0.0 COMMIT_HASH -m "Initial version"
```

---

## 💾 **備份策略**

### 方法 1: 備份到外接硬碟（推薦）

使用自動備份腳本：

```powershell
# 1. 修改腳本中的備份路徑（如果需要）
# 編輯 backup-to-external.ps1，修改 $BackupDrive

# 2. 執行備份
.\backup-to-external.ps1

# 功能：
# ✅ 自動檢查 Git 狀態
# ✅ 創建帶時間戳的備份
# ✅ 自動清理舊備份（保留最近 5 個）
# ✅ 顯示備份大小和資訊
```

### 方法 2: 備份到 NAS

```powershell
# 1. 修改 NAS 路徑
# 編輯 backup-to-nas.ps1，修改 $NasPath

# 2. 執行備份
.\backup-to-nas.ps1

# 功能：
# ✅ 檢查 NAS 連接
# ✅ 使用 Robocopy 高效備份
# ✅ 多線程傳輸
# ✅ 自動清理舊備份（保留最近 10 個）
```

### 方法 3: 手動備份

```powershell
# 簡單的手動備份
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
Copy-Item -Path "c:\Users\scott\Desktop\files (1)" `
          -Destination "E:\Backup\ambulance-inventory_$timestamp" `
          -Recurse
```

### 建議的備份頻率

- 📅 **每日工作後**: 如果有修改代碼
- 📅 **每週一次**: 即使沒有修改（安全起見）
- 📅 **重大更新前**: 添加新功能或重構前
- 📅 **重要里程碑**: 版本發布時

---

## 📊 **實用技巧**

### 查看文件責任歸屬

```bash
# 查看每一行是誰在何時修改的
git blame ambulance_inventory/config.py

# 只看特定範圍的行
git blame -L 10,20 ambulance_inventory/config.py
```

### 搜索歷史

```bash
# 在提交訊息中搜索
git log --grep="feature"

# 在代碼中搜索（查找何時添加/刪除某段代碼）
git log -S "OllamaConfig"

# 查找哪次提交修改了某個函數
git log -L :function_name:file.py
```

### 暫存工作進度

```bash
# 暫存當前修改（不提交）
git stash

# 查看暫存列表
git stash list

# 恢復最近的暫存
git stash pop

# 恢復特定的暫存
git stash apply stash@{0}

# 刪除暫存
git stash drop stash@{0}
```

### 清理工作區

```bash
# 查看哪些文件會被刪除（預覽）
git clean -n

# 刪除未追蹤的文件
git clean -f

# 刪除未追蹤的文件和目錄
git clean -fd
```

---

## 🔧 **Git 配置**

### 查看配置

```bash
# 查看所有配置
git config --list

# 查看特定配置
git config user.name
git config user.email
```

### 修改配置

```bash
# 修改用戶名
git config user.name "New Name"

# 修改 Email
git config user.email "new@email.com"

# 設置預設編輯器
git config core.editor "code --wait"  # VS Code

# 設置別名
git config alias.st status
git config alias.co checkout
git config alias.br branch
git config alias.ci commit
```

---

## 📈 **統計資訊**

```bash
# 查看貢獻統計
git shortlog -s -n

# 查看代碼行數統計
git log --author="Scott" --pretty=tformat: --numstat | \
awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }'

# 查看文件修改次數
git log --all -M -C --name-only --format='format:' "$@" | sort | grep -v '^$' | uniq -c | sort -n
```

---

## 🎯 **最佳實踐**

### 提交頻率

- ✅ **經常提交**: 完成一個小功能就提交
- ✅ **每個提交都可運行**: 不要提交無法運行的代碼
- ✅ **提交訊息清晰**: 讓未來的自己理解

### 分支使用

```bash
# 主分支
master          # 穩定版本

# 功能分支
feature/xxx     # 新功能開發
fix/xxx         # 錯誤修復
refactor/xxx    # 重構
docs/xxx        # 文檔更新
```

### 避免的事情

- ❌ 不要提交大型二進制文件
- ❌ 不要提交敏感資訊（密碼、token）
- ❌ 不要提交臨時文件（*.tmp, *.log）
- ❌ 不要使用 `git push --force`（本機無遠端所以不適用）

---

## 🚑 **常見問題**

### Q1: 不小心提交了錯誤的文件

```bash
# 如果還沒推送（本機使用，永遠是這種情況）
git reset --soft HEAD~1
# 修正文件
git add correct_files
git commit -m "Correct commit"
```

### Q2: 想要恢復到某個舊版本

```bash
# 查看歷史，找到目標版本
git log --oneline

# 恢復到特定版本（創建新分支）
git checkout -b old-version COMMIT_HASH

# 或直接恢復整個專案到舊版本（危險！）
git reset --hard COMMIT_HASH
```

### Q3: 合併時出現衝突

```bash
# 1. 查看衝突文件
git status

# 2. 手動編輯衝突文件，解決衝突標記
# <<<<<<< HEAD
# 當前分支的內容
# =======
# 要合併分支的內容
# >>>>>>> branch-name

# 3. 標記為已解決
git add conflicted_file

# 4. 完成合併
git commit
```

### Q4: 想要忽略某些文件

```bash
# 編輯 .gitignore
echo "*.log" >> .gitignore
echo "temp/" >> .gitignore

# 如果文件已經被追蹤，需要先移除
git rm --cached filename
git commit -m "chore: Update .gitignore"
```

---

## 📚 **學習資源**

### 推薦閱讀

- [Pro Git Book](https://git-scm.com/book/zh-tw/v2) - 官方中文書
- [Git 教學](https://gitbook.tw/) - 繁體中文教學
- [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_TW) - 互動式學習

### Git GUI 工具

如果不習慣命令列，可以使用圖形介面工具：

- **VS Code** - 內建 Git 支援（推薦）
- **GitHub Desktop** - 簡單易用（即使不用 GitHub 也能用）
- **Sourcetree** - 功能強大
- **GitKraken** - 漂亮的介面

---

## 🎓 **進階技巧**

### 查看文件在每次提交時的變化

```bash
# 查看文件的演變歷史
git log -p ambulance_inventory/config.py
```

### 比較不同版本的文件

```bash
# 比較工作區和某次提交
git diff COMMIT_HASH ambulance_inventory/config.py

# 比較兩次提交
git diff COMMIT1 COMMIT2 ambulance_inventory/config.py
```

### Cherry-pick（挑選提交）

```bash
# 將另一個分支的某次提交應用到當前分支
git cherry-pick COMMIT_HASH
```

### Rebase（變基）

```bash
# 整理提交歷史（本機使用，很安全）
git rebase -i HEAD~5  # 整理最近 5 次提交
```

---

## ✅ **每日檢查清單**

```bash
# 早上開始工作前
git status              # 查看狀態
git log --oneline -5    # 查看最近的提交

# 工作完成後
git add .
git commit -m "feat: Implement XXX"
git log --oneline -1    # 確認提交

# 每週備份
.\backup-to-external.ps1  # 或 backup-to-nas.ps1
```

---

## 🎉 **開始使用**

```bash
cd "c:\Users\scott\Desktop\files (1)"
git status
git log --oneline --graph --all
```

**您的代碼現在受到完整的版本控制保護！** 🎊

---

**創建日期**: 2026-01-14
**Git 版本**: 2.x
**配置**: 本機私密模式
