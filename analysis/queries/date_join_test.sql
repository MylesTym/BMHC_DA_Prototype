SELECT
COUNT(cs.response_id) as review_count,
YEAR(cs.timestamp) as year_,
MONTH(cs.timestamp) as month_,
AVG(cm.billable_amount_usd) as avg_billable
FROM
client_satisfaction as cs
JOIN
clockify_main as cm
ON
YEAR(cm.start_datetime) = YEAR(cs.timestamp)
AND
MONTH(cm.start_datetime) = MONTH(cs.timestamp)
GROUP BY
MONTH(cs.timestamp),
YEAR(cs.timestamp)
ORDER BY
avg_billable
