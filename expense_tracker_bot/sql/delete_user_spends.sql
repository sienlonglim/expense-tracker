DELETE FROM spends
WHERE (user_id, created_at, amount, card) IN (
    SELECT user_id, created_at, amount, card
    FROM spends
    WHERE user_id = ?
    ORDER BY created_at DESC
    LIMIT ?
)