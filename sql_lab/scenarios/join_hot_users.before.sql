-- Case: найти пользователей с наибольшей суммой оплаченных заказов за 180 дней.
-- BEFORE:
-- прямой join + агрегация по большой таблице orders.
SELECT
  u.id,
  u.email,
  COUNT(o.id) AS paid_orders,
  SUM(o.total_amount) AS paid_sum
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid'
  AND o.created_at >= NOW() - INTERVAL '180 days'
GROUP BY u.id, u.email
HAVING COUNT(o.id) >= 5
ORDER BY paid_sum DESC
LIMIT 200;
