select 
CAST(cm.start_datetime AS date) as date,
cm."group",
SUM(cm.billable_amount_usd) as billable_amount,
COUNT(cs.response_id) as daily_review_count
FROM
clockify_main as cm
JOIN
client_satisfaction as cs
ON
CAST(cs.[timestamp] AS date) = CAST(cm.start_datetime AS date)
GROUP BY
cm."group",
CAST(cm.start_datetime AS date) 