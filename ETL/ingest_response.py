import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import re

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
def get_or_create_profile(email, first_name, last_name, conn):
    ## Get existing profile by email or create new one with minimal info
    if pd.isna(email) or email.strip() == '':
        return None
    
    email = email.strip().lower()
    
    # Skip profile creation for none@none.com placeholder
    if email == 'none@none.com':
        return None
    
    email = email.replace("'", "''")
    
    # Check if profile exists
    query = f"SELECT profile_id FROM profiles WHERE email = '{email}'"
    result = pd.read_sql(query, conn)
    
    if len(result) > 0:
        return result.iloc[0]['profile_id']
    else:
        # Create new profile with just email and name
        first_name = str(first_name).replace("'", "''") if pd.notna(first_name) else 'NULL'
        last_name = str(last_name).replace("'", "''") if pd.notna(last_name) else 'NULL'
        
        insert_query = f"""
        INSERT INTO profiles (email, first_name, last_name)
        OUTPUT INSERTED.profile_id
        VALUES ('{email}', 
                {f"'{first_name}'" if first_name != 'NULL' else 'NULL'},
                {f"'{last_name}'" if last_name != 'NULL' else 'NULL'})
        """
        result = pd.read_sql(insert_query, conn)
        return result.iloc[0]['profile_id']
########################################################################################
########################################################################################
def split_services(text):
    if pd.isna(text):
        return []
    # Split on commas not inside parentheses
    return [cat.strip() for cat in re.split(r',(?![^(]*\))', text) if cat.strip()]
########################################################################################
########################################################################################
df = pd.read_csv('data/response.csv')
#columns
df.columns = (df.columns.str.strip()
              .str.lower() 
              .str.replace(' ', '_')
              .str.replace('(', '')
              .str.replace(')', ''))
df.reset_index(drop=True, inplace=True)

# Rename columns
df = df.rename(columns=
               {"prior_to_today's_visit,_when_was_the_last_time_you_visited_a_doctor?": 'date_previous_doctor_visit',
                "which_services_were_provided_to_you_today?": 'services_provided',
                "how_do_you_feel_about_the_health_issue_that_brought_you_to_bmhc?": "health_self_assessment",
                "please_explain_the_reason_for_your_answer:": "self_health_assessment_narrative",
                "what_is_your_overall_stress_level?": "stress_self_assessment",
                "explain_the_reason_for_your_answer:": "stress_self_assessment_narrative",
                "how_would_you_rate_your_overall_level_of_mental_health?": "mental_self_assessment",
                "please_explain_the_reason_for_your_answer:.1": "mental_self_assessment_narrative",
                "how_would_you_rate_your_overall_physical_health?": "physical_self_assessment",
                "please_explain_the_reason_for_your_answer:.2": "physical_self_assessment_narrative",
                "what_is_your_overall_impression_of_the_black_men's_health_clinic?": "overall_impression",
                "did_the_medical_provider_meet_your_expectations?": "provider_expectations",
                "please_explain_the_reason_for_your_answer:.3": "provider_expectations_narrative",
                "did_the_medical_care_meet_your_needs?": "medical_needs_met",
                "please_explain_the_reason_for_your_answer:.4": "medical_needs_met_narrative",
                "did_the_outreach_&_engagement_team_provide_a_strong_support_system?": "outreach_support",
                "please_explain_the_reason_for_your_answer:.5": "outreach_support_narrative",
                "are_you_a_member_of_the_healthycuts™_program?": "healthycuts_member",
                "are_you_a_movement_is_medicine_member?": "movement_medicine_member",
                "are_you_interested_in_potential_clinical_trial_opportunities?": "clinical_trial_interest",
                "are_you_willing_to_complete_a_brief_survey?": "survey_interest"})


# Split Name into first and last
df[['first_name', 'last_name']] = df['name:'].str.split(' ',n=1, expand=True)

# Drop column - can be adjusted
df = df.drop(columns={"column_1", "name:", 
                      "provider_expectations_narrative"
                      })


# Date and time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date_previous_doctor_visit'] = pd.to_datetime(df['date_previous_doctor_visit'], errors='coerce')

# single categoricals
catCols = [
    'healthycuts_member',
    'movement_medicine_member',   
]
for col in catCols:
    df[col] = df[col].astype('category')

# category fixing
# Category fixing: split on commas outside parentheses, then join as a string
df['services_provided'] = df['services_provided'].apply(split_services).apply(lambda x: ', '.join(x))

# Multiple categoricals
numCols = [
    'health_self_assessment',
    'stress_self_assessment',
    'mental_self_assessment',
    'physical_self_assessment',

]
for col in numCols:
    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# Bools
df['clinical_trial_interest'] = df['clinical_trial_interest'].str.lower().map({'maybe': True, 'not interested': False}).astype('boolean')
df['survey_interest'] = df['survey_interest'].str.lower().map({'yes': True, 'no': False})
df['provider_expectations'] = df['provider_expectations'].str.lower().map({'yes': True, 'no': False}).astype('boolean')
df['outreach_support'] = df['outreach_support'].str.lower().map({'yes': True, 'no': False}).astype('boolean')

df.info()

with engine.begin() as conn:
    # Map profile IDs inside transaction
    df['profile_id'] = df.apply(lambda row: get_or_create_profile(row['email_address'], row['first_name'], row['last_name'], conn), axis=1)
    
    # Drop personal info columns after profile mapping
    df = df.drop(columns=["email_address", "first_name", "last_name"])
    
    # Insert into database
    df.to_sql('client_satisfaction', conn, if_exists='append', index=False)