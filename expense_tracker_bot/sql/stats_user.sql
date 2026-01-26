SELECT 
    month_year,
    SUM(amount) as total,
    COUNT(*) as transactions,
    AVG(amount) as avg_spend
FROM spends 
WHERE user_id = ?
GROUP BY month_year
ORDER BY month_year DESC
