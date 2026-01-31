-- Step 2: Inventory transactions, locations, specs, and price history
-- 步驟 2：庫存交易、儲位、規格、價格歷史

-- 位置類型（倉庫 / 車輛 / 單位 / 人員）
CREATE TYPE IF NOT EXISTS location_type AS ENUM ('warehouse', 'vehicle', 'unit', 'person');

CREATE TABLE IF NOT EXISTS location (
    location_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,            -- 位置名稱（中央倉、救護車 A1 等）
    type location_type NOT NULL,   -- 位置類型
    parent_id INT REFERENCES location(location_id) -- 階層（可選）
);

-- 交易類型（入庫 / 出庫 / 調整）
CREATE TYPE IF NOT EXISTS txn_type AS ENUM ('in', 'out', 'adjust');

-- 庫存交易：單一真相來源（不再存「當前庫存」）
CREATE TABLE IF NOT EXISTS inventory_txn (
    txn_id BIGSERIAL PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES product(product_id),
    location_id INT NOT NULL REFERENCES location(location_id),
    txn_type txn_type NOT NULL,
    qty INT NOT NULL CHECK (qty > 0), -- 預設 qty 為正數
    unit_cost NUMERIC(10,2),
    note TEXT,
    txn_time TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 常用索引：依品項 + 時間、依儲位查詢
CREATE INDEX IF NOT EXISTS idx_txn_product_time ON inventory_txn(product_id, txn_time DESC);
CREATE INDEX IF NOT EXISTS idx_txn_location ON inventory_txn(location_id);

-- 規格：彈性 key/value（如「容量」「防護等級」）
CREATE TABLE IF NOT EXISTS product_spec (
    product_id TEXT NOT NULL REFERENCES product(product_id),
    spec_key TEXT NOT NULL,
    spec_value TEXT NOT NULL,
    PRIMARY KEY (product_id, spec_key)
);

-- 價格歷史：成本/定價/特價
CREATE TYPE IF NOT EXISTS price_type AS ENUM ('cost', 'list', 'sale');

CREATE TABLE IF NOT EXISTS product_price (
    product_id TEXT NOT NULL REFERENCES product(product_id),
    price_type price_type NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_to DATE,
    PRIMARY KEY (product_id, price_type, valid_from)
);

-- View：即時庫存（依品項 x 位置）
CREATE OR REPLACE VIEW stock_on_hand AS
SELECT
    product_id,
    location_id,
    SUM(CASE WHEN txn_type IN ('in', 'adjust') THEN qty ELSE -qty END) AS qty_on_hand
FROM inventory_txn
GROUP BY product_id, location_id;

-- View：低庫存警示（門檻 10）
CREATE OR REPLACE VIEW low_stock AS
SELECT product_id, location_id, qty_on_hand
FROM stock_on_hand
WHERE qty_on_hand < 10
ORDER BY qty_on_hand ASC;
