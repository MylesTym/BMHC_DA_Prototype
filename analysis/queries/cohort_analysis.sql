WITH total_records AS (
    SELECT COUNT(*) AS total FROM client_satisfaction
),
monthly_counts AS (
    SELECT
        YEAR([timestamp]) AS year,
        MONTH([timestamp]) AS month,
        COUNT(*) AS month_count,
        AVG(DATEDIFF(day, date_previous_doctor_visit, [timestamp])) AS avg_days_since_prev
    FROM client_satisfaction
    GROUP BY YEAR([timestamp]), MONTH([timestamp])
)
SELECT
    m.year,
    m.month,
    m.month_count,
    t.total,
    CAST(m.month_count AS FLOAT) / t.total AS per_capita,
    m.avg_days_since_prev AS "Average span in days since previous doctor visit"
FROM monthly_counts m
CROSS JOIN total_records t
ORDER BY m.year, m.month