import re
import os
import sys
from datetime import date, timedelta
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px
from scripts.analysis_functions import get_monthly_responses
from utilities.vis_style import apply_plotly_style, apply_matplotlib_style, BMHC_COLORS


load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db = os.getenv('DB_NAME')

conn_str = f'mssql+pymssql://{user}:{password}@{host}:{port}/{db}' 

engine = create_engine(conn_str)


# Dashboard Title
st.title("BMHC Prototype Impact Dashboard")
st.write("this is a placeholder")

# Date picker with default of past 30 days
#Defaults
default_end = date.today()
default_start = default_end - timedelta(days=180)
#Date picker
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Monthly review counts visualizations
fig = get_monthly_responses(engine, start_date, end_date)
st.plotly_chart(fig)

# # Sidebar filters
#group = st.sidebar.selectbox("Select Group", options=group_list)
#date_range = st.sidebar.date_input("Date Range", value=(start_date, end_date))

# # Survey Response Trends
# df = get_monthly_responses(date_range)
# fig = px.bar(df, x='date', y='responses', title='Survey Response by Month')
# st.plotly_chart(fig)

# # Cohort Metrics
# metrics = get_cohort_metrics(date_range)
# st.line_chart(metrics['avg_days_since_prev'])

# # Regression Results
# reg_results = run_regression(group, date_range)
# st.bar_chart(reg_results['coefficients'])