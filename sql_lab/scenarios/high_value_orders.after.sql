-- AFTER:
-- Добавляем индекс под наш тип фильтра:
-- 1) сначала ограничение по периоду,
-- 2) потом отсечение по total_amount.
CREATE INDEX IF NOT EXISTS idx_orders_created_amount ON orders (created_at, total_amount);

WITH recent_high_value AS (
  SELECT user_id, total_amount
  FROM orders
  WHERE created_at >= NOW() - INTERVAL '90 days'
    AND total_amount >= 7000
)
SELECT user_id, COUNT(*) AS order_count, SUM(total_amount) AS total_sum
FROM recent_high_value
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY total_sum DESC
LIMIT 100;
