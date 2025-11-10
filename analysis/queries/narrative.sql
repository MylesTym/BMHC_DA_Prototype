SELECT
  health_self_assessment,
  self_health_assessment_narrative + ' ' +
  stress_self_assessment_narrative + ' ' +
  mental_self_assessment_narrative + ' ' +
  physical_self_assessment_narrative AS patient_narrative
FROM client_satisfaction
WHERE self_health_assessment_narrative IS NOT NULL