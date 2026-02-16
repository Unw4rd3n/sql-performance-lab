-- AFTER:
-- Индекс под фильтр + сортировку.
CREATE INDEX IF NOT EXISTS idx_orders_paid_created_id
ON orders (status, created_at DESC, id DESC);

-- Берем якорь на границе нужной страницы и двигаемся keyset-подходом.
WITH anchor AS (
  SELECT created_at, id
  FROM orders
  WHERE status = 'paid'
  ORDER BY created_at DESC, id DESC
  OFFSET 20000
  LIMIT 1
)
SELECT o.id, o.user_id, o.total_amount, o.created_at
FROM orders o
CROSS JOIN anchor a
WHERE o.status = 'paid'
  AND (o.created_at, o.id) <= (a.created_at, a.id)
ORDER BY o.created_at DESC, o.id DESC
LIMIT 100;
