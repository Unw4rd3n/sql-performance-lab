-- AFTER:
-- Partial covering index: оптимизируем именно paid-заказы,
-- не раздувая индекс под все статусы.
CREATE INDEX IF NOT EXISTS idx_orders_paid_user_created
ON orders (user_id, created_at DESC)
INCLUDE (total_amount)
WHERE status = 'paid';

WITH paid_recent AS (
  SELECT user_id, total_amount
  FROM orders
  WHERE status = 'paid'
    AND created_at >= NOW() - INTERVAL '180 days'
)
SELECT
  u.id,
  u.email,
  COUNT(*) AS paid_orders,
  SUM(pr.total_amount) AS paid_sum
FROM paid_recent pr
JOIN users u ON u.id = pr.user_id
GROUP BY u.id, u.email
HAVING COUNT(*) >= 5
ORDER BY paid_sum DESC
LIMIT 200;
