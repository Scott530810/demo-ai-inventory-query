-- 救護車庫存資料庫 Demo 數據
-- ============================================

-- 擴充向量檢索 (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 創建資料表
CREATE TABLE IF NOT EXISTS inventory (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(100),
    specifications TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    unit_price DECIMAL(10, 2) NOT NULL,
    supplier VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引
CREATE INDEX idx_category ON inventory(category);
CREATE INDEX idx_brand ON inventory(brand);
CREATE INDEX idx_stock_quantity ON inventory(stock_quantity);

-- RAG 文件片段表
CREATE TABLE IF NOT EXISTS rag_chunks (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    page INTEGER,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED
);

-- RAG 索引
CREATE INDEX IF NOT EXISTS rag_chunks_source_idx ON rag_chunks(source);
CREATE INDEX IF NOT EXISTS rag_chunks_tsv_idx ON rag_chunks USING GIN (tsv);
CREATE INDEX IF NOT EXISTS rag_chunks_embedding_idx ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 創建視圖：低庫存警示
CREATE OR REPLACE VIEW low_stock_alert AS
SELECT product_id, product_name, category, brand, stock_quantity, unit_price
FROM inventory
WHERE stock_quantity < 10
ORDER BY stock_quantity ASC;

-- 創建視圖：分類統計
CREATE OR REPLACE VIEW category_summary AS
SELECT
    category,
    COUNT(*) as product_count,
    SUM(stock_quantity) as total_stock,
    AVG(unit_price) as avg_price,
    SUM(stock_quantity * unit_price) as total_value
FROM inventory
GROUP BY category
ORDER BY total_value DESC;

-- ============================================
-- 插入示例數據
-- ============================================

-- AED除顫器
INSERT INTO inventory VALUES
('AED-001', 'HeartStart HS1 半自動體外心臟除顫器', 'AED除顫器', 'Philips', 'HS1', '全自動分析、語音指導、8年待機', 15, 45000, '飛利浦醫療', NOW()),
('AED-002', 'ZOLL AED Plus 半自動體外除顫器', 'AED除顫器', 'ZOLL', 'AED Plus', 'CPR即時回饋、5年待機', 8, 52000, '宙斯醫療', NOW()),
('AED-003', 'Mindray BeneHeart C2 自動體外除顫器', 'AED除顫器', 'Mindray', 'C2', '雙語語音、6年待機、IP55防護', 12, 38000, '邁瑞醫療', NOW()),
('AED-004', 'Cardiac Science Powerheart G5 AED', 'AED除顫器', 'Cardiac Science', 'G5', '全自動、RescueCoach技術', 5, 58000, '心臟科學', NOW());

-- 擔架設備
INSERT INTO inventory VALUES
('STR-001', 'Ferno 35-X ProFlexx 救護車擔架', '擔架設備', 'Ferno', '35-X', '電動升降、載重227kg、可折疊', 6, 85000, 'Ferno台灣', NOW()),
('STR-002', 'Spencer 403 鋁合金擔架', '擔架設備', 'Spencer', '403', '輕量化、可調頭部、載重150kg', 10, 35000, 'Spencer亞洲', NOW()),
('STR-003', 'Stryker Power-PRO XT 電動擔架', '擔架設備', 'Stryker', 'Power-PRO XT', '全電動、X型框架、載重318kg', 3, 125000, '史賽克醫療', NOW()),
('STR-004', '鏟式擔架（可分離式）', '擔架設備', 'Ferno', 'Scoop 65', '鋁合金、X光穿透、可分離', 8, 18000, 'Ferno台灣', NOW()),
('STR-005', '折疊式樓梯椅', '擔架設備', 'Ferno', 'Model 40', '折疊式、載重159kg、適合狹窄空間', 12, 15000, 'Ferno台灣', NOW());

-- 氧氣設備
INSERT INTO inventory VALUES
('OXY-001', 'Luxfer L6X 鋁合金氧氣瓶 680L', '氧氣設備', 'Luxfer', 'L6X', '680公升容量、鋁合金、含壓力表', 20, 8500, '氧氣設備行', NOW()),
('OXY-002', 'Precision Medical EasyPulse POC 攜帶式氧氣濃縮機', '氧氣設備', 'Precision Medical', 'EasyPulse', '5段流量、電池續航8小時', 4, 68000, '精密醫療', NOW()),
('OXY-003', 'BLS 氧氣調節器（0-15 LPM）', '氧氣設備', '一般品牌', 'BLS-R15', '流量0-15L/min、含流量計', 25, 3200, '醫療器材行', NOW()),
('OXY-004', '成人氧氣面罩（含儲氧袋）', '氧氣設備', '一般品牌', 'Adult-Mask', '拋棄式、含7呎導管', 100, 45, '醫療耗材', NOW());

-- 監視器
INSERT INTO inventory VALUES
('MON-001', 'Mindray BeneView T5 病患監視器', '監視器', 'Mindray', 'T5', '5參數、12.1吋彩色螢幕、含ECG/SpO2/NIBP', 5, 85000, '邁瑞醫療', NOW()),
('MON-002', 'Masimo Rad-97 脈搏血氧儀', '監視器', 'Masimo', 'Rad-97', '連續SpO2監測、含rainbow技術', 8, 95000, 'Masimo台灣', NOW()),
('MON-003', 'GE Carescape V100 生命徵象監視器', '監視器', 'GE Healthcare', 'V100', '基本生命徵象、可攜式', 6, 72000, 'GE醫療', NOW()),
('MON-004', 'Nonin 9560 手指式血氧計', '監視器', 'Nonin', '9560', '攜帶式、一鍵操作', 20, 8500, 'Nonin代理', NOW());

-- 抽吸設備
INSERT INTO inventory VALUES
('SUC-001', 'Laerdal LCSU 4 攜帶式抽吸機', '抽吸設備', 'Laerdal', 'LCSU 4', '電池供電、負壓可調、800ml容量', 7, 28000, 'Laerdal台灣', NOW()),
('SUC-002', 'Ambu Res-Cue Pump 手動抽吸器', '抽吸設備', 'Ambu', 'Res-Cue Pump', '手動式、免電池、300ml容量', 15, 3500, 'Ambu代理', NOW()),
('SUC-003', 'DeVilbiss 7305 系列抽吸機', '抽吸設備', 'DeVilbiss', '7305D-613', '車載式、1200ml收集瓶', 5, 32000, 'DeVilbiss醫療', NOW());

-- 呼吸設備
INSERT INTO inventory VALUES
('RES-001', 'Ambu Bag 成人手動甦醒球（含面罩）', '呼吸設備', 'Ambu', 'Mark IV', '1600ml、含氧氣接頭、可重複消毒', 25, 2800, 'Ambu代理', NOW()),
('RES-002', 'Ambu Bag 兒童手動甦醒球', '呼吸設備', 'Ambu', 'Mark IV Pediatric', '500ml、兒童專用', 20, 2600, 'Ambu代理', NOW()),
('RES-003', 'i-gel 聲門上呼吸道（成人#3/#4/#5）', '呼吸設備', 'Intersurgical', 'i-gel', '拋棄式、3種尺寸組合包', 50, 350, '呼吸道器材', NOW()),
('RES-004', 'ResMed Stellar 100 呼吸器', '呼吸設備', 'ResMed', 'Stellar 100', '非侵入性通氣、可攜式', 2, 185000, 'ResMed台灣', NOW());

-- 固定器材
INSERT INTO inventory VALUES
('IMM-001', 'Ferno KED 脊椎固定裝置', '固定器材', 'Ferno', 'KED', '坐姿脊椎固定、X光穿透', 10, 12000, 'Ferno台灣', NOW()),
('IMM-002', 'Ferno 長背板（含頭部固定器）', '固定器材', 'Ferno', 'Najo Lite', '塑膠材質、含頭部固定、X光穿透', 8, 8500, 'Ferno台灣', NOW()),
('IMM-003', 'SAM Splint II 萬用夾板組', '固定器材', 'SAM Medical', 'Splint II', '可塑形鋁板、3種尺寸', 30, 850, 'SAM代理', NOW()),
('IMM-004', 'Trac-3 頸圈組（4種尺寸）', '固定器材', 'Laerdal', 'Stifneck', '4種尺寸、可調式', 25, 450, 'Laerdal台灣', NOW());

-- 急救包
INSERT INTO inventory VALUES
('KIT-001', '創傷急救包（大型）', '急救包', '一般品牌', 'Trauma-L', '含繃帶/紗布/止血帶等', 15, 3500, '醫療耗材', NOW()),
('KIT-002', '燒燙傷急救包', '急救包', 'Water-Jel', 'Burn Kit', '含燒燙傷敷料、冷卻凝膠', 20, 2200, 'Water-Jel代理', NOW()),
('KIT-003', 'CPR 口罩組（拋棄式）', '急救包', 'Laerdal', 'Pocket Mask', '單向閥、氧氣接頭', 40, 280, 'Laerdal台灣', NOW());

-- 車內設備
INSERT INTO inventory VALUES
('VEH-001', '醫療冷藏箱（12V車用）', '車內設備', 'Dometic', 'CF-035', '35公升、-18°C~+10°C', 3, 22000, 'Dometic代理', NOW()),
('VEH-002', 'LED 車內照明燈組', '車內設備', '一般品牌', 'LED-Strip-5M', '5米防水燈條、12V', 8, 1800, '汽車配件', NOW()),
('VEH-003', '醫療設備固定架（多功能）', '車內設備', '客製品牌', 'Multi-Rack', '鋁合金、可調式', 5, 8500, '車用改裝', NOW());

-- 防護用品
INSERT INTO inventory VALUES
('PPE-001', 'N95 防護口罩（50入/盒）', '防護用品', '3M', '1860', 'NIOSH認證、呼吸阻抗低', 30, 1500, '3M台灣', NOW()),
('PPE-002', '拋棄式隔離衣（50件/箱）', '防護用品', '一般品牌', 'PP-Gown', 'PP材質、防潑水', 20, 2500, '醫療耗材', NOW()),
('PPE-003', '丁腈手套（100只/盒）', '防護用品', 'Ansell', 'TouchNTuff', '無粉、抗穿刺', 50, 450, 'Ansell代理', NOW()),
('PPE-004', '護目鏡（防霧型）', '防護用品', '3M', '1621AF', '防霧、防刮、可滅菌', 25, 280, '3M台灣', NOW());

-- 通訊設備
INSERT INTO inventory VALUES
('COM-001', 'Motorola DP4400 數位無線電', '通訊設備', 'Motorola', 'DP4400', 'DMR數位、IP67防護', 10, 15000, 'Motorola代理', NOW()),
('COM-002', 'Uniden BC75XLT 掃描器', '通訊設備', 'Uniden', 'BC75XLT', '300頻道、緊急頻道優先', 6, 4500, 'Uniden台灣', NOW());

-- 更新時間戳記
UPDATE inventory SET last_updated = NOW();

-- 顯示統計
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '資料庫初始化完成！';
    RAISE NOTICE '============================================';
    RAISE NOTICE '總商品數: %', (SELECT COUNT(*) FROM inventory);
    RAISE NOTICE '總分類數: %', (SELECT COUNT(DISTINCT category) FROM inventory);
    RAISE NOTICE '低庫存商品: %', (SELECT COUNT(*) FROM low_stock_alert);
    RAISE NOTICE '總庫存價值: NT$ %', (SELECT SUM(stock_quantity * unit_price) FROM inventory);
    RAISE NOTICE '============================================';
END $$;
