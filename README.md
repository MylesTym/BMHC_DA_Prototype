# BMHC Analysis Pipeline

A data integration and analysis pipeline for Black Mental Health Collective (BMHC) program evaluation and reporting.

## Overview

This ETL pipeline consolidates data from multiple sources into a normalized SQL Server database, enabling cross-dataset analysis of participant outcomes, service delivery, and organizational impact.

### Data Sources
- **Client Satisfaction Survey**: Service quality assessments with mental/physical health self-ratings
- **Movement is Medicine (MiM)**: Health activity tracking with demographic profiles
- **Clockify**: Staff timesheet data with organization and tag associations
- **Permanent Supportive Housing (PSH)**: Housing program data (pending)

### Database Schema
The pipeline creates a star schema with:
- **Profiles**: Unified participant dimension (358 unique profiles) with progressive enrichment
- **Organizations**: Unified organization dimension (43 organizations)
- **Fact Tables**: client_satisfaction (868), mim (220), clockify_main (6,474)
- **Bridge Tables**: clockify_tags (11,914), clockify_entities (6,974)

**Total Records**: 26,000+

## Features

### Cross-Dataset Profile Tracking
- Participants tracked across datasets using email as natural key
- Minimal profile creation (email + name) from survey responses
- Progressive enrichment: Demographics from MiM can update minimal profiles
- NULL profile handling for anonymous/placeholder submissions (`none@none.com`)

### Data Integrity
- Foreign key constraints maintain referential integrity
- Transaction management prevents partial loads
- NULL profile_id support for anonymous data
- Organization dimension unifies partner agencies and church affiliations

### Dtype Optimization
- **Int64**: Nullable integers for Likert scale ratings
- **boolean**: Nullable booleans for Yes/No questions
- **category**: Low-cardinality fields (gender, race, membership)
- **datetime64[ns]**: Timestamps with error handling

## Technology Stack

- **Python 3.13**: Core ETL logic
- **pandas**: Data transformation and cleaning
- **SQLAlchemy**: Database connection and transaction management
- **pymssql**: SQL Server driver
- **SQL Server**: Database backend (Docker container)
- **python-dotenv**: Environment variable management

## Project Structure

```
BMHC-Analysis-pipeline/
├── ETL/
│   ├── ingest_response.py      # Client satisfaction survey ETL
│   ├── ingest_MiM.py            # Movement is Medicine ETL
│   ├── ingest_clockify.py       # Timesheet data ETL
│   └── ingest_PSH.py            # Housing data ETL (pending)
├── schemas/
│   ├── profiles/
│   │   └── profiles.sql
│   ├── organizations/
│   │   └── Organizations.sql
│   ├── survey_response/
│   │   └── client_satisfaction.sql
│   ├── clockify/
│   │   ├── clockify_main.sql
│   │   ├── clockify_tags.sql
│   │   └── clockify_entities.sql
│   └── mim/
│       └── mim.sql
├── data/                         # Source CSV files (not in git)
├── .env                          # Database credentials (not in git)
└── README.md
```

## Setup

### Prerequisites
- Python 3.13+
- SQL Server (Docker or local instance)
- Source data files in CSV format

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/BMHC-Analysis-pipeline
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install pandas sqlalchemy pymssql python-dotenv
   ```

4. **Configure database connection**
   
   Create `.env` file in project root:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=1433
   DB_NAME=BMHC_DB
   ```

5. **Create database schema**
   
   Execute SQL scripts in this order:
   ```bash
   # 1. Dimension tables
   schemas/profiles/profiles.sql
   schemas/organizations/Organizations.sql
   
   # 2. Fact tables
   schemas/survey_response/client_satisfaction.sql
   schemas/mim/mim.sql
   schemas/clockify/clockify_main.sql
   schemas/clockify/clockify_tags.sql
   schemas/clockify/clockify_entities.sql
   ```

6. **Place source data**
   
   Add CSV files to `data/` directory:
   - Client Satisfaction Survey.csv
   - Movement is Medicine (MiM) Data.csv
   - Clockify_Time_Report_Summary.csv

## Usage

### Running ETL Scripts

Execute scripts in this order to maintain referential integrity:

```bash
# Activate virtual environment
source .venv/bin/activate

# 1. Load Clockify (creates organizations)
python ETL/ingest_clockify.py

# 2. Load MiM (creates profiles with demographics)
python ETL/ingest_MiM.py

# 3. Load Client Satisfaction (creates minimal profiles, enriches existing)
python ETL/ingest_response.py

# 4. Load PSH (when data available)
python ETL/ingest_PSH.py
```

### Verification Queries

```sql
-- Check table counts
SELECT 'profiles' as table_name, COUNT(*) as count FROM profiles
UNION ALL
SELECT 'organizations', COUNT(*) FROM organizations
UNION ALL
SELECT 'client_satisfaction', COUNT(*) FROM client_satisfaction
UNION ALL
SELECT 'mim', COUNT(*) FROM mim
UNION ALL
SELECT 'clockify_main', COUNT(*) FROM clockify_main;

-- Check profile linkage
SELECT 
    COUNT(CASE WHEN profile_id IS NOT NULL THEN 1 END) as linked_responses,
    COUNT(CASE WHEN profile_id IS NULL THEN 1 END) as anonymous_responses
FROM client_satisfaction;

-- Cross-dataset participant analysis
SELECT 
    p.email,
    p.first_name,
    p.last_name,
    COUNT(DISTINCT cs.response_id) as satisfaction_surveys,
    COUNT(DISTINCT m.activity_id) as mim_activities
FROM profiles p
LEFT JOIN client_satisfaction cs ON p.profile_id = cs.profile_id
LEFT JOIN mim m ON p.profile_id = m.profile_id
GROUP BY p.email, p.first_name, p.last_name
HAVING COUNT(DISTINCT cs.response_id) > 0 OR COUNT(DISTINCT m.activity_id) > 0;
```

## Key Design Patterns

### Profile Management
```python
def get_or_create_profile(email, first_name=None, last_name=None, ...):
    """
    Creates minimal profiles or enriches existing ones.
    Returns None for placeholder email 'none@none.com'.
    """
    if email == 'none@none.com':
        return None
    
    # Check if profile exists
    existing = pd.read_sql(f"SELECT profile_id FROM profiles WHERE email = '{email}'", engine)
    
    if not existing.empty:
        # COALESCE-based UPDATE to enrich with new data
        return existing.iloc[0]['profile_id']
    else:
        # INSERT minimal profile
        return new_profile_id
```

### Transaction Management
```python
with engine.begin() as conn:
    # All operations in single transaction
    # Automatic rollback on error
    conn.execute(text("INSERT INTO ..."))
    conn.commit()
```

## Data Quality Notes

### Known Limitations
- **Anonymous Responses**: 120 client satisfaction records with `profile_id = NULL` (used `none@none.com`)
- **Incomplete Demographics**: Some profiles lack age, gender, race, zip_code
- **Upstream Data Quality**: Placeholder emails, missing fields in source data

### Profile Enrichment
The pipeline supports progressive profile enrichment:
1. Survey creates minimal profile (email + name)
2. MiM participation updates with demographics (age, gender, race, zip)
3. Future datasets can continue enriching profiles

## Analysis Readiness

✅ **Ready for analysis** with current datasets (Client Satisfaction, MiM, Clockify)

### Recommended First Analyses
1. **Client satisfaction trends**: Rating distributions, service quality metrics
2. **MiM health outcomes**: Activity participation, demographic breakdowns
3. **Workforce allocation**: Staff time by organization, project, task
4. **Cross-participation patterns**: Participants in multiple programs
5. **Demographic insights**: Service utilization by race, gender, age, location

### Limitations
- PSH data not yet available
- Some anonymous responses not linkable to profiles
- Upstream data quality issues (placeholder emails, missing fields)

## Contributing

When adding new datasets:
1. Create SQL schema in `schemas/` directory
2. Create ETL script in `ETL/` directory
3. Follow established patterns:
   - Use `get_or_create_profile()` for participant tracking
   - Use `get_or_create_organization()` for organization dimension
   - Apply appropriate dtypes (Int64, boolean, category)
   - Use transaction management (`engine.begin()`)
   - Handle NULL values appropriately
4. Update this README with new dataset information

## License

Internal use by Black Mental Health Collective.

## Contact

For questions about the pipeline or data access, contact the BMHC data team.
