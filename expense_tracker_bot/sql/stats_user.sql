select 
    month_year,
    sum(amount) as total,
    count(*) as transactions,
    avg(amount) as avg_spend
from spends
where user_id = ?
group by month_year
order by month_year desc
