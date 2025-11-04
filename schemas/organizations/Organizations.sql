CREATE TABLE organizations (
    org_id INT IDENTITY(1,1) PRIMARY KEY,
    org_name NVARCHAR(255) NOT NULL,
    org_type NVARCHAR(50), -- 'Church', 'Community Partner', 'Healthcare', etc.
    org_status NVARCHAR(20) DEFAULT 'Active',
    created_date DATETIME2 DEFAULT GETDATE(),
    UNIQUE(org_name)
);