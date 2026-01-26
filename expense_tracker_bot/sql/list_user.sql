SELECT username, card, amount, month_year, created_at
FROM spends WHERE user_id = ?
ORDER BY created_at DESC LIMIT 10
