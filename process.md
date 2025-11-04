# BMHC Analysis Pipeline Process

## Overview
This document tracks the process and progress of the BMHC Analysis Pipeline project.
SQL database artcitecture in an incomplete stage. Full implementation would require more thought and stakeholder input (data relationships/reporting requirements/visualization needs).

## ETL Process Notes



### Data Sources

- **Client Satisfaction**: 
- **Clockify**: 
- **MiM (Motivational Interviewing Module)**: 
- **PSH (Permanent Supportive Housing)**: 

### Ingestion Process
#### Client Satisfaction
- **Script**: `ETL/ingest_client_satisfaction.py`
- **Status**: WORKING
- **Notes**: 'none@none.com' complicates data cleaning and analysis unnecesarily. Column names require renaming across the board.

#### Clockify
- **Script**: `ETL/ingest_clockify.py`
- **Status**: COMPLETE
- **Notes**: organization of information makes data cleaning difficult

#### MiM (Motivational Interviewing Module)
- **Script**: `ETL/ingest_MiM.py`
- **Status**: COMPLETE
- **Notes**: Questionable data quality (data entry errors, inconsitent formatting, poor null handling)

#### PSH (Permanent Supportive Housing)
- **Script**: `ETL/ingest_PSH.py`
- **Status**: 
- **Notes**: 

### Data Quality Issues
- Across all datasets exists data entry errors, poor null (no response) planning, inconsistent data formats and types.
- Large amounts of incomplete/missing data.
- data collection needs refinement
- Inconsistent name entry (full name vs. first name, last name)
- several columns across all datasets left empty

### Transformation Steps
- 

### Loading & Output
- 

## Analysis Notes

### Key Metrics
- 

### Findings
- 

### Visualizations
- 

## Next Steps
- 

## Issues & Blockers
- partial relationships between datasets

## Meeting Notes
### [Date] - Meeting Title
- 

---
*Prepared By: Myles M *
*Last Updated: [Date]*