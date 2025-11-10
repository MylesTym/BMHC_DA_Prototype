WITH overall_health_rating AS (
SELECT
(health_self_assessment + stress_self_assessment 
+ mental_self_assessment+ physical_self_assessment) / 3 AS over_all
FROM
client_satisfaction)

SELECT
MONTH([timestamp])