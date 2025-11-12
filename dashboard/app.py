import re
import os
import sys
from datetime import date, timedelta
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from plotly.subplots import make_subplots
import plotly.express as px
from scripts.analysis_functions import get_monthly_responses, get_review_averages, get_binary_metrics, get_survey_count, get_health_delta
from utilities.vis_style import apply_plotly_style, apply_matplotlib_style, BMHC_COLORS
#####################################################################################
#####################################################################################
# Move this to it's own .py in dashboard directory #
st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        margin-bottom: 0rem !important;
        background-color: #00000;

    }
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"]{
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        background-color: #ecf0f1;
        color: #000000;
    }
    section[data-testid="stAppViewContainer"]{
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] {
        min-width: 180px;
        max-width: 180px;
        width: 180px;
        background-color: #d0a53f;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#####################################################################################
#####################################################################################
load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db = os.getenv('DB_NAME')

conn_str = f'mssql+pymssql://{user}:{password}@{host}:{port}/{db}' 

engine = create_engine(conn_str)
st.set_page_config(layout="wide", page_title="Dashboard")
#####################################################################################
#####################################################################################
# Dashboard Title
st.title("BMHC Prototype Client Sat Dashboard")
st.write(f"Default Day Interval: 180")
#####################################################################################
#####################################################################################

# Date picker with default of past 180 days
#Defaults
default_end = date.today()
default_start = default_end - timedelta(days=180)
#Date picker
start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)
#####################################################################################
#####################################################################################
metrics = {
    "Total Reviews": get_survey_count(engine, start_date, end_date)
}

with st.container():
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label=label, value=value)
#####################################################################################
#####################################################################################


col1, col2, col3 = st.columns([1, 3, 1]) # window ratios

#####################################################################################
#####################################################################################
with col1:
    fig1 = get_review_averages(engine, start_date, end_date)
    fig1.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        height=150
    )
    st.plotly_chart(fig1, use_container_width=True)
#####################################################################################
#####################################################################################
with col2:
# Monthly review counts visualizations
    fig = get_monthly_responses(engine, start_date, end_date)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    fig.update_xaxes(range=[fig.data[0].x[0], fig.data[0].x[-1]])
    st.plotly_chart(fig, use_container_width=True)
#####################################################################################
#####################################################################################
with col3:
    fig3 = get_binary_metrics(engine, start_date, end_date)
    fig3.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        height=350
    )
    st.plotly_chart(fig3, use_container_width=True)
#####################################################################################
#####################################################################################
with st.container():
    col_left, col_right = st.columns(2)
    with col_left:
        fig4 = get_health_delta(engine, start_date, end_date)
        st.plotly_chart(fig4, use_container_width=True)
    #with col_right:
 
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