CREATE TABLE mim (
    activity_id INT IDENTITY(1,1) PRIMARY KEY,
    profile_id INT FOREIGN KEY REFERENCES profiles(profile_id),
    organization_id INT FOREIGN KEY REFERENCES organizations(org_id),
    timestamp DATETIME2,
    date_of_activity DATE,
    systolic_blood_pressure DECIMAL(5,2),
    diastolic_blood_pressure DECIMAL(5,2),
    heart_rate DECIMAL(5,2),
    weight DECIMAL(6,2),
    topics_of_interest NVARCHAR(MAX),
    learning_outcome NVARCHAR(255),
    interested_in_continuing BIT,
    bmhc_enrollment NVARCHAR(100),
    created_date DATETIME2 DEFAULT GETDATE()
);