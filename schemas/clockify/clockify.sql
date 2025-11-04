
CREATE TABLE clockify_main (
    id INT PRIMARY KEY,                -- surrogate key from df['id']
    project NVARCHAR(255),
    description NVARCHAR(MAX),
    task NVARCHAR(255),
    [group] NVARCHAR(255),
    billable BIT,
    invoiced BIT,
    duration_decimal DECIMAL(10,2),
    billable_rate_usd DECIMAL(10,2),
    billable_amount_usd DECIMAL(10,2),
    approval BIT,
    approved_by NVARCHAR(255),
    #_of_people_engaged NVARCHAR(255),
    start_datetime DATETIME2,
    end_datetime DATETIME2
    -- note: tags and collaborated_entity are not here anymore
);