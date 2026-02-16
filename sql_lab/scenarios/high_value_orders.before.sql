-- Case: топ пользователей с дорогими заказами за последние 90 дней.
-- BEFORE:
-- запрос рабочий, но на больших объемах обычно уходит в seq scan.
SELECT user_id, COUNT(*) AS order_count, SUM(total_amount) AS total_sum
FROM orders
WHERE total_amount >= 7000
  AND created_at >= NOW() - INTERVAL '90 days'
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY total_sum DESC
LIMIT 100;
