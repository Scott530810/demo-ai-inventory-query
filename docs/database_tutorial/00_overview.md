# Database Tutorial (PostgreSQL) - Step-by-step

本教學以現有的救護車庫存 demo 為起點，逐步從「單一表」演進到
「正規化 + 交易式庫存 + 多倉/多車輛」的實務設計。

## Learning goals / 學習目標
- Normalization / 正規化：1NF/2NF/3NF、參照表、資料一致性
- Indexing / 索引：常見查詢的索引設計
- Transactions / 交易：入庫/出庫/調整與稽核軌跡
- History / 歷史：價格變動、庫存流向
- Queries / 查詢：即時庫存、低庫存警示、分類彙總

## Steps (in order) / 步驟
1) 單表基準檢視（現有 `ambulance_inventory_demo.sql`）
2) 正規化主檔（分類、品牌、供應商）
3) 增加儲位/位置（倉庫 / 車輛 / 單位）
4) 改用交易式庫存（單一真相來源）
5) 加入規格與價格歷史
6) 建立 View、索引與範例查詢

每一步都有對應的 SQL 檔與練習清單。

- Schema files: `docs/database_tutorial/01_normalize_schema.sql`, `02_transactions_schema.sql`
- Seed file: `docs/database_tutorial/03_seed_minimal.sql`
- Query file: `docs/database_tutorial/04_queries.sql`
- Exercises: `docs/database_tutorial/05_exercises.md`

## 命名建議（中文欄位？）
- PostgreSQL 支援中文表/欄位，但需要使用雙引號，且大小寫敏感。
- 工具/ORM/IDE 的相容性與團隊維護成本會增加。
- 建議：資料表/欄位用英文（snake_case），顯示名稱用中文（UI/報表/註解）。
