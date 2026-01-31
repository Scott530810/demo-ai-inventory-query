-- Minimal seed data for tutorial
-- 最小教學用資料，方便驗證查詢結果

INSERT INTO category (name) VALUES
('AED除顫器'),
('擔架設備'),
('氧氣設備')
ON CONFLICT (name) DO NOTHING;

INSERT INTO brand (name) VALUES
('Philips'),
('ZOLL'),
('Ferno'),
('Luxfer')
ON CONFLICT (name) DO NOTHING;

INSERT INTO supplier (name, contact, phone) VALUES
('飛利浦醫療', 'Amy', '02-0000-0001'),
('宙斯醫療', 'Ben', '02-0000-0002'),
('Ferno台灣', 'Cindy', '02-0000-0003'),
('氧氣設備行', 'David', '02-0000-0004')
ON CONFLICT (name) DO NOTHING;

-- 品項主檔
INSERT INTO product (product_id, name, category_id, brand_id, supplier_id, model)
VALUES
('AED-001', 'HeartStart HS1 半自動體外心臟除顫器',
 (SELECT category_id FROM category WHERE name='AED除顫器'),
 (SELECT brand_id FROM brand WHERE name='Philips'),
 (SELECT supplier_id FROM supplier WHERE name='飛利浦醫療'),
 'HS1'),
('AED-002', 'ZOLL AED Plus 半自動體外除顫器',
 (SELECT category_id FROM category WHERE name='AED除顫器'),
 (SELECT brand_id FROM brand WHERE name='ZOLL'),
 (SELECT supplier_id FROM supplier WHERE name='宙斯醫療'),
 'AED Plus'),
('STR-001', 'Ferno 35-X ProFlexx 擔架',
 (SELECT category_id FROM category WHERE name='擔架設備'),
 (SELECT brand_id FROM brand WHERE name='Ferno'),
 (SELECT supplier_id FROM supplier WHERE name='Ferno台灣'),
 '35-X'),
('OXY-001', 'Luxfer L6X 鋁合金氧氣瓶 680L',
 (SELECT category_id FROM category WHERE name='氧氣設備'),
 (SELECT brand_id FROM brand WHERE name='Luxfer'),
 (SELECT supplier_id FROM supplier WHERE name='氧氣設備行'),
 'L6X')
ON CONFLICT (product_id) DO NOTHING;

-- 位置：倉庫 + 車輛
INSERT INTO location (name, type) VALUES
('中央倉', 'warehouse'),
('救護車 A1', 'vehicle'),
('救護車 A2', 'vehicle')
ON CONFLICT DO NOTHING;

-- 庫存交易（入庫 / 出庫）
INSERT INTO inventory_txn (product_id, location_id, txn_type, qty, unit_cost, note)
VALUES
('AED-001', (SELECT location_id FROM location WHERE name='中央倉'), 'in', 5, 45000, '初始入庫'),
('AED-001', (SELECT location_id FROM location WHERE name='救護車 A1'), 'out', 1, 45000, '配發至 A1'),
('AED-002', (SELECT location_id FROM location WHERE name='中央倉'), 'in', 3, 52000, '初始入庫'),
('STR-001', (SELECT location_id FROM location WHERE name='中央倉'), 'in', 4, 85000, '初始入庫'),
('STR-001', (SELECT location_id FROM location WHERE name='救護車 A2'), 'out', 1, 85000, '配發至 A2'),
('OXY-001', (SELECT location_id FROM location WHERE name='中央倉'), 'in', 10, 8500, '初始入庫');

-- 規格
INSERT INTO product_spec (product_id, spec_key, spec_value) VALUES
('AED-001', '待機年限', '8年'),
('AED-001', '防護等級', 'IP55'),
('OXY-001', '容量', '680L')
ON CONFLICT DO NOTHING;

-- 價格（示範）
INSERT INTO product_price (product_id, price_type, price, valid_from) VALUES
('AED-001', 'list', 45000, CURRENT_DATE),
('AED-002', 'list', 52000, CURRENT_DATE),
('STR-001', 'list', 85000, CURRENT_DATE),
('OXY-001', 'list', 8500, CURRENT_DATE)
ON CONFLICT DO NOTHING;
