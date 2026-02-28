select username, card, amount, month_year, created_at
from spends where user_id = ?
order by created_at desc limit 10
