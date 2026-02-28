create table if not exists comments (
    user_id bigint,
    username varchar,
    comment varchar,
    month_year varchar,
    created_at timestamp default current_timestamp
)
