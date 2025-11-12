SELECT
    SUM(CASE WHEN medical_needs_met = 1 THEN 1 ELSE 0 END) AS medical_needs_met_true,
    SUM(CASE WHEN medical_needs_met = 0 THEN 1 ELSE 0 END) AS medical_needs_met_false,
    SUM(CASE WHEN provider_expectations = 1 THEN 1 ELSE 0 END) AS provider_expectations_true,
    SUM(CASE WHEN provider_expectations = 0 THEN 1 ELSE 0 END) AS provider_expectations_false,
    SUM(CASE WHEN clinical_trial_interest = 1 THEN 1 ELSE 0 END) AS trial_interest_true,
    SUM(CASE WHEN clinical_trial_interest = 0 THEN 1 ELSE 0 END) AS trial_interest_false,
    SUM(CASE WHEN survey_interest = 1 THEN 1 ELSE 0 END) AS survey_interest_true,
    SUM(CASE WHEN survey_interest = 0 THEN 1 ELSE 0 END) AS survey_interest_false
FROM client_satisfaction