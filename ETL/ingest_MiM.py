import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

########################################################################################
########################################################################################

load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")

conn_str = f"mssql+pymssql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(conn_str)

########################################################################################
########################################################################################
def get_or_create_organization(conn, org_name, org_type='Unknown'):
    if pd.isna(org_name) or org_name.strip() == '':
        return None
    
    org_name = org_name.strip().replace("'", "''")
    
    # Check if organization exists
    query = f"SELECT org_id FROM organizations WHERE org_name = '{org_name}'"
    result = pd.read_sql(query, conn)
    
    if len(result) > 0:
        return result.iloc[0]['org_id']
    else:
        # Create new organization
        org_type = org_type.replace("'", "''")
        insert_query = f"""
        INSERT INTO organizations (org_name, org_type) 
        OUTPUT INSERTED.org_id
        VALUES ('{org_name}', '{org_type}')
        """
        result = pd.read_sql(insert_query, conn)
        return result.iloc[0]['org_id']
########################################################################################
########################################################################################
def get_or_create_profile(conn, email, first_name, last_name, phone, age, gender, race, zip_code):
    """Get existing profile by email, update with new data, or create new one"""
    if pd.isna(email) or email.strip() == '':
        return None
    
    email = email.strip().lower().replace("'", "''")
    
    # Check if profile exists by email
    query = f"SELECT profile_id FROM profiles WHERE email = '{email}'"
    result = pd.read_sql(query, conn)
    
    if len(result) > 0:
        # Profile exists - update with new demographic data if available
        profile_id = result.iloc[0]['profile_id']
        
        # Prepare fields
        first_name_val = f"'{str(first_name).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(first_name) else 'NULL'
        last_name_val = f"'{str(last_name).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(last_name) else 'NULL'
        phone_val = f"'{str(phone).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(phone) else 'NULL'
        gender_val = f"'{str(gender).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(gender) else 'NULL'
        race_val = f"'{str(race).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(race) else 'NULL'
        zip_val = f"'{str(zip_code).replace(chr(39), chr(39)+chr(39))}'" if pd.notna(zip_code) else 'NULL'
        age_val = str(int(age)) if pd.notna(age) else 'NULL'
        
        # Update existing profile - COALESCE keeps existing value if new value is NULL
        update_query = f"""
        UPDATE profiles 
        SET first_name = COALESCE({first_name_val}, first_name),
            last_name = COALESCE({last_name_val}, last_name),
            phone_number = COALESCE({phone_val}, phone_number),
            age = COALESCE({age_val}, age),
            gender = COALESCE({gender_val}, gender),
            race = COALESCE({race_val}, race),
            zip_code = COALESCE({zip_val}, zip_code)
        WHERE profile_id = {profile_id}
        """
        conn.execute(text(update_query))
        return profile_id
    else:
        # Escape and prepare all string fields
        first_name = str(first_name).replace("'", "''") if pd.notna(first_name) else 'NULL'
        last_name = str(last_name).replace("'", "''") if pd.notna(last_name) else 'NULL'
        phone = str(phone).replace("'", "''") if pd.notna(phone) else 'NULL'
        gender = str(gender).replace("'", "''") if pd.notna(gender) else 'NULL'
        race = str(race).replace("'", "''") if pd.notna(race) else 'NULL'
        zip_code = str(zip_code).replace("'", "''") if pd.notna(zip_code) else 'NULL'
        age = int(age) if pd.notna(age) else 'NULL'
        
        # Build INSERT with proper NULL handling
        insert_query = f"""
        INSERT INTO profiles (email, first_name, last_name, phone_number, age, gender, race, zip_code)
        OUTPUT INSERTED.profile_id
        VALUES (
            '{email}',
            {f"'{first_name}'" if first_name != 'NULL' else 'NULL'},
            {f"'{last_name}'" if last_name != 'NULL' else 'NULL'},
            {f"'{phone}'" if phone != 'NULL' else 'NULL'},
            {age},
            {f"'{gender}'" if gender != 'NULL' else 'NULL'},
            {f"'{race}'" if race != 'NULL' else 'NULL'},
            {f"'{zip_code}'" if zip_code != 'NULL' else 'NULL'}
        )
        """
        result = pd.read_sql(insert_query, conn)
        return result.iloc[0]['profile_id']
########################################################################################
########################################################################################
df = pd.read_csv('data/MiM.csv')
# Data prep for analysis

# Columns
df.columns = (df.columns.str.strip()
              .str.lower() 
              .str.replace(' ', '_')
              .str.replace('(', '')
              .str.replace(')', ''))
df.reset_index(drop=True, inplace=True)
df = df.drop(columns="column_17") ## empty column
df = df.drop(columns='birthdate') ## mostly empty

# Date and time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date_of_activity'] = pd.to_datetime(df['date_of_activity'])


# Rename columns
df = df.rename(columns={'are_you_interested_in_continuing_mim?': 'interested_in_continuing'})

# Bools
df['interested_in_continuing'] = df['interested_in_continuing'].map({'Yes': True, 'No': False})


# Null/None handling 
null_indicators = ['', 'Not taken at this event', '0']
df = df.replace(null_indicators, None)

# Single categoricals
catCols = [
    'gender',
    'race',
    'topics_of_interest',
    'learning_outcome',
    'interested_in_continuing',
    'bmhc_enrollment',
]
for col in catCols:
    df[col] = df[col].astype('category')

# Numeric metrics
numCols = [
    'age',
    'systolic_blood_pressure',
    'diastolic_blood_pressure',
    'heart_rate',
    'weight'
]
for col in numCols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# After df.info(), when database connection is uncommented:
# Database operations - replace your entire "with engine.begin()" block with this:
with engine.begin() as conn:
    # Map organizations
    unique_orgs = df['church_/_organization_affiliation'].dropna().unique()
    org_mapping = {}
    
    for org in unique_orgs:
        org_id = get_or_create_organization(conn, org, 'Church')
        org_mapping[org] = org_id
    
    df['organization_id'] = df['church_/_organization_affiliation'].map(org_mapping)
    
    # Map profiles
    df['profile_id'] = df.apply(
        lambda row: get_or_create_profile(
            conn, 
            row['e-mail'],
            row['first_name'], 
            row['last_name'],
            row['phone_number'],
            row['age'],
            row['gender'],
            row['race'],
            row['zip_code']
        ), 
        axis=1
    )
    
    # Create main dataframe - drop all personal info and original org column
    main_df = df.drop(columns=[
        'first_name',
        'last_name',
        'e-mail',
        'phone_number',
        'age',
        'gender',
        'race',
        'zip_code',
        'church_/_organization_affiliation'
    ])
    
    # Insert into database
    main_df.to_sql("mim", con=conn, if_exists="append", index=False)