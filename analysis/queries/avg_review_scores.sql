SELECT
CAST(AVG(health_self_assessment * 1.0) AS DECIMAL(10,2)) as health_assessment,
CAST(AVG(stress_self_assessment * 1.0) AS DECIMAL(10,2)) as stress_self_assessment,
CAST(AVG(mental_self_assessment * 1.0) AS DECIMAL(10,2)) as mental_assessment,
CAST(AVG(physical_self_assessment * 1.0) AS DECIMAL(10,2)) as physical_assessment
FROM client_satisfaction