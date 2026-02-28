create table if not exists spends (
    user_id bigint,
    username varchar,
    card varchar,
    amount decimal(10,2),
    month_year varchar,
    created_at timestamp default current_timestamp
)
