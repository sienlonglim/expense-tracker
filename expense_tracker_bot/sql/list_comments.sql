select 
    month_year,
    comment
from comments
where user_id = ?
