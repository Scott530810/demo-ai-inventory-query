# Lesson Notes (Step-by-step) / 教學筆記

## Prerequisites / 前置條件
- PostgreSQL 15 running via docker-compose (already in this repo)
- `psql` available in the container or on host

## Step 0: Baseline (single-table) / 單表基準
目標：理解單表的問題與限制。
- 打開 `ambulance_inventory_demo.sql`
- 找出重複文字欄位（category/brand/supplier）
- 注意缺少「歷史」與「多位置庫存」的問題

## Step 1: Normalize master data / 正規化主檔
目標：把重複欄位拆成參照表。
- 套用 `01_normalize_schema.sql`
- `\\dt` 檢查新表
- 套用 `03_seed_minimal.sql`（只會填入最小資料）

## Step 2: Add locations and transactions / 增加位置與交易
目標：用交易記錄取代「當前庫存欄位」。
- 套用 `02_transactions_schema.sql`
- 再次執行 `03_seed_minimal.sql` 以產生交易資料
- 查詢 `stock_on_hand` 比對結果是否合理

## Step 3: Specs and price history / 規格與價格歷史
目標：支援彈性規格與價格變動。
- 檢查 `product_spec`、`product_price`
- 為某個品項新增較新的價格
- 用 `04_queries.sql` 查最新價格

## Step 4: Indexing / 索引
目標：理解索引如何改善查詢。
- 套用 schema 內的索引
- 對 `04_queries.sql` 使用 `EXPLAIN ANALYZE`
- 移除索引再測一次，比較差異

## Step 5: Exercises / 練習
目標：擴展模型與查詢能力。
- 完成 `05_exercises.md`
- 每題思考：是 schema 改動、資料改動、還是純查詢？
