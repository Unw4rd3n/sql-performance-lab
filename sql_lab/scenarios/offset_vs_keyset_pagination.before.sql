-- Case: получить "глубокую" страницу оплаченных заказов.
-- BEFORE:
-- OFFSET на больших смещениях обычно сильно тормозит.
SELECT id, user_id, total_amount, created_at
FROM orders
WHERE status = 'paid'
ORDER BY created_at DESC, id DESC
OFFSET 20000
LIMIT 100;
