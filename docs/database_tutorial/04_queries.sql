-- Example queries for tutorial
-- 範例查詢（可直接貼到 psql）

-- 1) Stock on hand by product and location
-- 1) 依品項與位置的即時庫存
SELECT s.product_id, p.name, l.name AS location_name, s.qty_on_hand
FROM stock_on_hand s
JOIN product p ON p.product_id = s.product_id
JOIN location l ON l.location_id = s.location_id
ORDER BY p.product_id, l.name;

-- 2) Low stock items (threshold 10)
-- 2) 低庫存清單（門檻 10）
SELECT p.product_id, p.name, l.name AS location_name, ls.qty_on_hand
FROM low_stock ls
JOIN product p ON p.product_id = ls.product_id
JOIN location l ON l.location_id = ls.location_id
ORDER BY ls.qty_on_hand ASC;

-- 3) Category summary (count, total stock, total value)
-- 3) 分類彙總（品項數、總庫存、總價值）
SELECT
  c.name AS category,
  COUNT(DISTINCT p.product_id) AS product_count,
  SUM(s.qty_on_hand) AS total_stock,
  SUM(s.qty_on_hand * pp.price) AS total_value
FROM product p
JOIN category c ON c.category_id = p.category_id
JOIN stock_on_hand s ON s.product_id = p.product_id
LEFT JOIN LATERAL (
  SELECT price
  FROM product_price
  WHERE product_id = p.product_id AND price_type = 'list'
  ORDER BY valid_from DESC
  LIMIT 1
) pp ON TRUE
GROUP BY c.name
ORDER BY total_value DESC NULLS LAST;

-- 4) Movement history for a product
-- 4) 指定品項的交易歷史
SELECT txn_time, txn_type, qty, unit_cost, note
FROM inventory_txn
WHERE product_id = 'AED-001'
ORDER BY txn_time DESC;

-- 5) Stock by location type (warehouse vs vehicle)
-- 5) 依位置類型彙總庫存
SELECT l.type, SUM(s.qty_on_hand) AS total_qty
FROM stock_on_hand s
JOIN location l ON l.location_id = s.location_id
GROUP BY l.type
ORDER BY l.type;
