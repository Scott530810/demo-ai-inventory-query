# Exercises / 練習題

## A) Normalization / 正規化
1) Add `manufacturer_country` to `brand` and update seed data.  
   在 `brand` 新增 `manufacturer_country`，並更新種子資料。
2) Enforce that `supplier.name` must be unique and not empty.  
   `supplier.name` 需為唯一且不可空。
3) Create a `category_parent_id` to support category trees.  
   在 `category` 新增 `category_parent_id` 支援階層分類。

## B) Transactions & Integrity / 交易與完整性
1) Add a CHECK so `adjust` can be negative (design how you want to represent it).  
   設計調整量為負數的做法（例如允許 `qty` 為負或另建欄位）。
2) Add a trigger or a materialized view to speed up stock queries.  
   用 trigger 或 materialized view 加速庫存查詢。
3) Record who performed the transaction (`performed_by`).  
   在交易中記錄操作者（`performed_by`）。

## C) Indexing / 索引
1) Add an index for queries that filter by `txn_time` and `location_id`.  
   為 `txn_time` 與 `location_id` 查詢建立索引。
2) Create an index for fast lookup by `product.name` (case-insensitive search).  
   為 `product.name` 建立不分大小寫的搜尋索引。
3) Compare query plans before/after indexes.  
   比較有無索引的查詢計畫。

## D) Queries / 查詢
1) Find all products that have never moved (no transactions).  
   找出從未有交易紀錄的品項。
2) Find top 5 products by total inventory value.  
   找出庫存價值最高的前 5 名。
3) Find locations that are below a per-category threshold (e.g., AED < 2).  
   依分類門檻找出低於門檻的庫位。

## E) Data Modeling / 資料建模
1) Add `maintenance_due_date` for devices that require inspection.  
   為需保養設備增加 `maintenance_due_date`。
2) Model batch/lot numbers with expiration dates.  
   加入批號與效期欄位。
3) Split price into `cost`, `list`, and `contract` with history.  
   價格拆成成本/定價/合約價並保存歷史。
