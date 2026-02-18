-- Currency Exchange Rate Service - SQL Analytics Queries

-- 1. Request History with Currency Rates (Basic JOIN)
SELECT 
    r.id as request_id,
    r.timestamp as request_time,
    r.request_type,
    r.status,
    res.currency_code,
    res.rate,
    res.timestamp as rate_timestamp
FROM requests r
LEFT JOIN responses res ON r.id = res.request_id
ORDER BY r.timestamp DESC, res.currency_code;

-- 2. Aggregated Request Statistics with Rates
SELECT 
    r.id as request_id,
    r.timestamp as request_time,
    r.status,
    COUNT(res.id) as currency_count,
    STRING_AGG(
        res.currency_code || ': ' || res.rate::TEXT, 
        ', '
    ) as currency_rates
FROM requests r
LEFT JOIN responses res ON r.id = res.request_id
GROUP BY r.id, r.timestamp, r.status
ORDER BY r.timestamp DESC;

-- 3. Latest Rates for Each Currency
WITH latest_rates AS (
    SELECT DISTINCT ON (res.currency_code) 
        res.currency_code,
        res.rate,
        res.timestamp,
        r.status
    FROM responses res
    JOIN requests r ON res.request_id = r.id
    WHERE r.status = 'success'
    ORDER BY res.currency_code, res.timestamp DESC
)
SELECT * FROM latest_rates
ORDER BY currency_code;

-- 4. Currency Rate Trends Over Time
SELECT 
    res.currency_code,
    DATE(res.timestamp) as date,
    AVG(res.rate) as avg_rate,
    MIN(res.rate) as min_rate,
    MAX(res.rate) as max_rate,
    COUNT(*) as sample_count
FROM responses res
JOIN requests r ON res.request_id = r.id
WHERE r.status = 'success'
GROUP BY res.currency_code, DATE(res.timestamp)
ORDER BY res.currency_code, date DESC;

-- 5. Error Analysis and Request Success Rate
SELECT 
    DATE(r.timestamp) as date,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN r.status = 'success' THEN 1 END) as successful_requests,
    COUNT(CASE WHEN r.status = 'error' THEN 1 END) as failed_requests,
    ROUND(
        COUNT(CASE WHEN r.status = 'success' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as success_rate_percent
FROM requests r
GROUP BY DATE(r.timestamp)
ORDER BY date DESC;

-- 6. Currency Rate Comparison (Current vs Previous)
WITH current_rates AS (
    SELECT DISTINCT ON (res.currency_code)
        res.currency_code,
        res.rate as current_rate,
        res.timestamp as current_time
    FROM responses res
    JOIN requests r ON res.request_id = r.id
    WHERE r.status = 'success'
    ORDER BY res.currency_code, res.timestamp DESC
),
previous_rates AS (
    SELECT DISTINCT ON (res.currency_code)
        res.currency_code,
        res.rate as previous_rate,
        res.timestamp as previous_time
    FROM responses res
    JOIN requests r ON res.request_id = r.id
    WHERE r.status = 'success'
    ORDER BY res.currency_code, res.timestamp DESC
    OFFSET 1
)
SELECT 
    c.currency_code,
    c.current_rate,
    p.previous_rate,
    ROUND(((c.current_rate - p.previous_rate) / p.previous_rate * 100), 4) as percentage_change
FROM current_rates c
JOIN previous_rates p ON c.currency_code = p.currency_code
ORDER BY ABS((c.current_rate - p.previous_rate) / p.previous_rate) DESC;

-- 7. Hourly Request Distribution
SELECT 
    EXTRACT(HOUR FROM r.timestamp) as hour_of_day,
    COUNT(*) as request_count,
    COUNT(CASE WHEN r.status = 'success' THEN 1 END) as successful_count,
    COUNT(CASE WHEN r.status = 'error' THEN 1 END) as error_count
FROM requests r
GROUP BY EXTRACT(HOUR FROM r.timestamp)
ORDER BY hour_of_day;

-- 8. Top Performing Currencies (Most Stable)
SELECT 
    res.currency_code,
    COUNT(*) as data_points,
    ROUND(AVG(res.rate), 6) as average_rate,
    ROUND(STDDEV(res.rate), 6) as rate_volatility,
    ROUND(MIN(res.rate), 6) as min_rate,
    ROUND(MAX(res.rate), 6) as max_rate
FROM responses res
JOIN requests r ON res.request_id = r.id
WHERE r.status = 'success'
GROUP BY res.currency_code
ORDER BY rate_volatility ASC;

-- 9. Recent Activity Summary
SELECT 
    'Last 24 hours' as period,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'error' THEN 1 END) as failed,
    ROUND(AVG(CASE WHEN status = 'success' THEN 1.0 ELSE 0 END) * 100, 2) as success_rate
FROM requests 
WHERE timestamp >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'Last 7 days' as period,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'error' THEN 1 END) as failed,
    ROUND(AVG(CASE WHEN status = 'success' THEN 1.0 ELSE 0 END) * 100, 2) as success_rate
FROM requests 
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- 10. Currency Coverage Analysis
SELECT 
    r.id as request_id,
    r.timestamp,
    COUNT(res.currency_code) as currencies_collected,
    ARRAY_AGG(res.currency_code ORDER BY res.currency_code) as currency_list
FROM requests r
LEFT JOIN responses res ON r.id = res.request_id
GROUP BY r.id, r.timestamp
ORDER BY r.timestamp DESC;