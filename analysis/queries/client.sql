WITH clean_data AS (
    SELECT
        profile_id,
        gender     
    from profiles
        WHERE
            gender IS NOT NULL

)

SELECT
cl.profile_id,
cl.gender,
COUNT(cs.profile_id) as reviews
FROM
clean_data as cl
JOIN
client_satisfaction as cs
ON
cs.profile_id = cl.profile_id
GROUP BY
    cl.profile_id,
    cl.gender