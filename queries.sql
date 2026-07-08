SELECT c.city_name, MAX(w.temp_max) AS max_temperature
FROM weather_records w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name;

SELECT c.city_name, strftime('%m', w.record_date) AS month, SUM(w.precipitation) AS total_precipitation
FROM weather_records w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name, month;


SELECT c.city_name, strftime('%W', w.record_date) AS week_number, AVG(w.wind_speed_max) AS avg_wind_speed
FROM weather_records w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name, week_number
ORDER BY avg_wind_speed DESC
LIMIT 10;

WITH city_rainfall_agg AS (
    SELECT 
        city_id, 
        AVG(precipitation) AS raw_avg_precipitation
    FROM weather_records
    GROUP BY city_id
)
SELECT 
    c.city_name,
    ROUND(r.raw_avg_precipitation, 2) AS avg_daily_precipitation
FROM cities c
JOIN city_rainfall_agg r ON c.city_id = r.city_id;

SELECT c.city_name, COUNT(*) AS extreme_heat_days
FROM weather_records w
JOIN cities c ON w.city_id = c.city_id
WHERE w.temp_max > 40.0
GROUP BY c.city_name;

SELECT c.city_name, COUNT(*) AS extreme_cold_days
FROM weather_records w
JOIN cities c ON w.city_id = c.city_id
WHERE w.temp_min < 5.0
GROUP BY c.city_name;