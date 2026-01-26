CREATE TABLE IF NOT EXISTS spends (
    user_id BIGINT,
    username VARCHAR,
    card VARCHAR,
    amount DECIMAL(10,2),
    month_year VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
