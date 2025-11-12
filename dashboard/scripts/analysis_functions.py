# Messy imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
from wordcloud import WordCloud
from tqdm import tqdm
import re
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from nltk.tokenize import word_tokenize
from plotly.subplots import make_subplots
from nltk.util import ngrams
from nltk.corpus import stopwords
from collections import Counter
sys.path.append(os.path.join('..', 'utilities'))  # Navigate to utilities folder
from utilities.vis_style import apply_plotly_style, apply_matplotlib_style, BMHC_COLORS

#####################################################################################
#####################################################################################
# .Env variables and DB Connection
load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db = os.getenv('DB_NAME')

conn_str = f'mssql+pymssql://{user}:{password}@{host}:{port}/{db}' 

engine = create_engine(conn_str)
#####################################################################################
#####################################################################################
######## Need to rename method to something that makes sense for what it does #######
def get_monthly_responses(engine, start_date=None, end_date=None):
    where_clause = ""
    if start_date and end_date:
        where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"      
    query = f"""
    SELECT 
        YEAR(timestamp) as year,
        MONTH(timestamp) as month,
        COUNT(*) as responses
    FROM client_satisfaction
    {where_clause}
    GROUP BY YEAR(timestamp), MONTH(timestamp)
    ORDER BY year, month
    """
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    fig = px.bar(df, x='date', y='responses',title='Survey Response by Month',
                labels={'date': 'Month', 'responses': 'Number of Responses'},
                hover_data={'year': True, 'month': True})
    fig.add_hline(y=df['responses'].mean(), 
                line_dash="dash", 
                line_color=BMHC_COLORS['gold'],
                annotation_text=f"2025 Average: {df['responses'].mean():.1f}")
    fig.update_layout(xaxis_title='Month',yaxis_title='Number of Responses',
        hovermode='x unified',height=600,showlegend=True)
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    apply_plotly_style(fig)
    return fig
#####################################################################################
#####################################################################################
def get_review_averages(engine, start_date=None, end_date=None):
    where_clause = ""
    if start_date and end_date:
        where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"
        query = f"""
        SELECT
            CAST(AVG(health_self_assessment * 1.0) AS DECIMAL(10,2)) as health_assessment,
            CAST(AVG(stress_self_assessment * 1.0) AS DECIMAL(10,2)) as stress_self_assessment,
            CAST(AVG(mental_self_assessment * 1.0) AS DECIMAL(10,2)) as mental_assessment,
            CAST(AVG(physical_self_assessment * 1.0) AS DECIMAL(10,2)) as physical_assessment
        FROM client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        rating = df['health_assessment'].iloc[0]
        if rating < 2.5:
            bar_color = "red"
        elif rating < 3.5:
            bar_color = "yellow"
        else:
            bar_color = "green"
        fig = go.Figure(go.Indicator(mode = "gauge+number", value= rating, domain = {'x': [0, 1], 'y': [0,1]},
            title = {'text': "Health Assessment"},
            gauge = {'axis': {'range': [1, 5]}, 'bar': {'color': bar_color},'bgcolor': 'white'}
        ))
        apply_plotly_style(fig)
        return fig
#####################################################################################
#####################################################################################
def get_binary_metrics(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
        SELECT
            SUM(CASE WHEN medical_needs_met = 1 THEN 1 ELSE 0 END) AS medical_needs_met_true,
            SUM(CASE WHEN medical_needs_met = 0 THEN 1 ELSE 0 END) AS medical_needs_met_false,
            SUM(CASE WHEN provider_expectations = 1 THEN 1 ELSE 0 END) AS provider_expectations_true,
            SUM(CASE WHEN provider_expectations = 0 THEN 1 ELSE 0 END) AS provider_expectations_false,
            SUM(CASE WHEN clinical_trial_interest = 1 THEN 1 ELSE 0 END) AS trial_interest_true,
            SUM(CASE WHEN clinical_trial_interest = 0 THEN 1 ELSE 0 END) AS trial_interest_false,
            SUM(CASE WHEN survey_interest = 1 THEN 1 ELSE 0 END) AS survey_interest_true,
            SUM(CASE WHEN survey_interest = 0 THEN 1 ELSE 0 END) AS survey_interest_false
        FROM client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        metrics = ['Medical Needs Met', 'Provider Expectations']
        true_counts = [
            df['medical_needs_met_true'][0],
            df['provider_expectations_true'][0],
            df['trial_interest_true'][0],
            df['survey_interest_true'][0]
        ]
        false_counts = [
            df['medical_needs_met_false'][0],
            df['provider_expectations_false'][0],
            df['trial_interest_false'][0],
            df['survey_interest_false'][0]
        ]
        for i, metric in enumerate(metrics):
            fig = go.Figure(data=[
                go.Pie(
                    labels=['True', 'False'],
                    values=[true_counts[i], false_counts[i]],
                    marker=dict(colors=['green', 'red'])
                )
            ])
            fig.update_layout(title=f"{metric} (True vs False)")
            apply_plotly_style(fig)
        return fig
#####################################################################################
#####################################################################################
def get_survey_count(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
       SELECT
        COUNT(*)
        FROM
        client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0])
