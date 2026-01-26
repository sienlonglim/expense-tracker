SELECT username, card, SUM(amount) as total, COUNT(*) as transactions
FROM spends WHERE user_id = ?
GROUP BY username, card
