-- Step 1: Normalize master data (categories, brands, suppliers, products)
-- 步驟 1：正規化主檔（分類、品牌、供應商、品項）
-- 說明：保留既有 product_id，但把重複文字拆成參照表，避免拼字不一致。

CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE -- 分類名稱
);

CREATE TABLE IF NOT EXISTS brand (
    brand_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE -- 品牌名稱
);

CREATE TABLE IF NOT EXISTS supplier (
    supplier_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE, -- 供應商名稱
    contact TEXT,              -- 聯絡人
    phone TEXT                 -- 電話
);

CREATE TABLE IF NOT EXISTS product (
    product_id TEXT PRIMARY KEY,                       -- 既有品項代碼
    name TEXT NOT NULL,                                -- 品項名稱
    category_id INT NOT NULL REFERENCES category(category_id),
    brand_id INT REFERENCES brand(brand_id),
    supplier_id INT REFERENCES supplier(supplier_id),
    model TEXT,                                        -- 型號
    is_active BOOLEAN NOT NULL DEFAULT TRUE,           -- 是否啟用
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 常用查詢索引：依分類或品牌篩選
CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
CREATE INDEX IF NOT EXISTS idx_product_brand ON product(brand_id);
