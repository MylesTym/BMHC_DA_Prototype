CREATE TABLE profiles (
    profile_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(100),
    last_name NVARCHAR(100),
    email NVARCHAR(255) UNIQUE NOT NULL,  -- Primary matching field
    phone_number NVARCHAR(20),
    age INT,
    gender NVARCHAR(50),
    race NVARCHAR(100),
    zip_code NVARCHAR(10),
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE()
);