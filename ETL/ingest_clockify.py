import pandas as pd
from sqlalchemy import create_engine
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
    
    org_name = org_name.strip().replace("'", "''")  # Escape single quotes
    
    # Check if organization exists
    query = f"SELECT org_id FROM organizations WHERE org_name = '{org_name}'"
    result = pd.read_sql(query, conn)
    
    if len(result) > 0:
        return result.iloc[0]['org_id']
    else:
        # Create new organization
        org_type = org_type.replace("'", "''")  # Escape single quotes
        insert_query = f"""
        INSERT INTO organizations (org_name, org_type) 
        OUTPUT INSERTED.org_id
        VALUES ('{org_name}', '{org_type}')
        """
        result = pd.read_sql(insert_query, conn)
        return result.iloc[0]['org_id']

########################################################################################
########################################################################################

df = pd.read_csv('data/clockify.csv')
# Data prep for analysis

#columns
df.columns = (df.columns.str.strip()
              .str.lower() 
              .str.replace(' ', '_')
              .str.replace('(', '')
              .str.replace(')', ''))
df.reset_index(drop=True, inplace=True)
df['id'] = df.index + 1

#drop some columns
dropCols = [
    'duration_h',
    'invoice_id',
    'email',
    'user',
    'type',
    'client'
]
df.drop(columns=dropCols,inplace=True)

#date and time
df["start_datetime"] = pd.to_datetime(df["start_date"].astype(str) + ' ' + df["start_time"].astype(str))
df["end_datetime"] = pd.to_datetime(df["end_date"].astype(str) + ' ' + df["end_time"].astype(str))
df = df.drop(columns=["start_date", "start_time", "end_date", "end_time"])

#bools
for col in ["billable", "invoiced"]:
    df[col] = df[col].str.lower().map({"yes": True, "no": False})
df['approval'] = df['approval'].str.lower().map({"approved": True, "unapproved": False})

#single categoricals
catCols = [
    'project',
    'task',
    'group',
    '#_of_people_engaged',
    'approved_by'
]
for col in catCols:
    df[col] = df[col].astype('category')

#multiple categoricals
mulCols = [
    'tags',
    'collaborated_entity'
]
for col in mulCols:
    df[col] = df[col].apply(
        lambda x: [item.strip() for item in x] if isinstance(x, list)
        else [item.strip() for item in str(x).split(',')] if isinstance(x, str) and x
        else []
    )
# create bridge table for tags
tags_bridge = (
    df[['id','tags']]                # keep row id + tags
    .explode('tags')                  # one row per tag
    .dropna(subset=['tags'])          # drop empties
    .rename(columns={'id':'row_id','tags':'tag'})  # rename for clarity
)

# Get unique entities for organization creation
unique_entities = df['collaborated_entity'].explode().dropna().unique()
org_mapping = {}

#Null handling
df['#_of_people_engaged'] = df['#_of_people_engaged'].cat.add_categories(["Unknown"])
df['approved_by'] = df['approved_by'].cat.add_categories(["Unknown"])

df['#_of_people_engaged'] = df['#_of_people_engaged'].fillna("Unknown")
df['approved_by'] = df['approved_by'].fillna("Unknown")
#data split
main_df = df.drop(columns=['tags', 'collaborated_entity'])

with engine.begin() as conn:
    # Create organizations using the same connection
    for entity in unique_entities:
        org_id = get_or_create_organization(conn, entity, 'Community Partner')
        org_mapping[entity] = org_id
    
    # Create bridge table with org_ids after organizations are created
    entities_bridge = (
        df[['id','collaborated_entity']]
        .explode('collaborated_entity')
        .dropna(subset=['collaborated_entity'])
        .assign(org_id=lambda x: x['collaborated_entity'].map(org_mapping))
        .rename(columns={'id':'row_id'})
        [['row_id', 'org_id']]  # Only keep ID columns
    )
    
    # Insert all tables using the same connection
    main_df.to_sql("clockify_main", con=conn, if_exists="append", index=False)
    tags_bridge.to_sql("clockify_tags", con=conn, if_exists="append", index=False) 
    entities_bridge.to_sql("clockify_entities", con=conn, if_exists="append", index=False)



