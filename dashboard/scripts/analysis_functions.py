# Messy imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
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
from vis_style import apply_plotly_style, apply_matplotlib_style, BMHC_COLORS
import plotly.graph_objects as go

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
    fig.update_traces(texttemplate='%{y}', textposition='outside', marker_color='#4A0E4E')
    apply_plotly_style(fig)
    return fig
#####################################################################################
#####################################################################################
def get_review_averages(engine, start_date=None, end_date=None, metric="health_assessment"):
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
        rating = df[metric].iloc[0]
        if rating < 2.5:
            bar_color = "red"
        elif rating < 3.5:
            bar_color = "yellow"
        else:
            bar_color = "green"
        fig = go.Figure(go.Indicator(mode = "gauge+number", value= rating, domain = {'x': [0, 1], 'y': [0,1]},
            gauge = {'axis': {'range': [1, 5]}, 'bar': {'color': bar_color},'bgcolor': 'white'}
        ))
        apply_plotly_style(fig)
        fig.update_layout(
        showlegend=False,
        title=None,
        title_text='',  # Add this
        annotations=[]  # Add this to remove any annotations
        )
        return fig
#####################################################################################
def get_binary_metric(engine, metric, display_name=None, start_date=None, end_date=None):
    where_clause = ""
    if start_date and end_date:
        where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"
    query = f"""
    SELECT
        SUM(CASE WHEN {metric} = 1 THEN 1 ELSE 0 END) AS true_count,
        SUM(CASE WHEN {metric} = 0 THEN 1 ELSE 0 END) AS false_count
    FROM client_satisfaction
    {where_clause}
    """
    df = pd.read_sql(query, engine)
    true_count = df['true_count'][0]
    false_count = df['false_count'][0]
    fig = go.Figure(data=[
        go.Pie(
            labels=['True', 'False'],
            values=[true_count, false_count],
            marker=dict(colors=['green', 'red'])
        )
    ])
    fig.update_layout(
         title=f"{display_name or metric} (True vs False)",
         margin=dict(l=10, r=10, t=40, b=10),
         height=200,
         showlegend=False
         )
    apply_plotly_style(fig)
    return fig
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
        metrics = ['Medical Needs Met', 'Provider Expectations', 'Trial Interest', 'Survey Interest']
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
#####################################################################################
#####################################################################################
def get_health_delta(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
        WITH total_records AS (
        SELECT COUNT(*) AS total FROM client_satisfaction
        ),
        monthly_counts AS (
            SELECT
                YEAR([timestamp]) AS year,
                MONTH([timestamp]) AS month,
                COUNT(*) AS month_count,
                AVG(DATEDIFF(day, date_previous_doctor_visit, [timestamp])) AS avg_days_since_prev
            FROM client_satisfaction
            {where_clause}
            GROUP BY YEAR([timestamp]), MONTH([timestamp])
        )
        SELECT
            m.year,
            m.month,
            m.month_count,
            t.total,
            CAST(m.month_count AS FLOAT) / t.total AS per_capita,
            m.avg_days_since_prev AS "Average span in days since previous doctor visit"
        FROM monthly_counts m
        CROSS JOIN total_records t
        ORDER BY m.year, m.month
        """
        df = pd.read_sql(query, engine)

        # Date column
        df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')

        # Matplotlib plotting
        fig = px.line(
            df,
            x='date',
            y='Average span in days since previous doctor visit',
            title='BMHC First Medical Interaction in X Days',
            labels={'date': 'Date', 'Average span in days since previous doctor visit': 'Avg Days Since Previous Visit'}
        )
        fig.update_traces(mode='lines+markers', marker=dict(size=8, color='blue'))
        fig.update_layout(
            width=1000,   # wide
            height=300,   # short
            margin=dict(l=40, r=40, t=60, b=40)
        )
        apply_plotly_style(fig)
        return fig
#####################################################################################
#####################################################################################
def get_services_provided(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
        SELECT [timestamp], services_provided
        FROM client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        def split_services(s):
            if pd.isna(s):
                return []
            return [x.strip() for x in re.split(r',\s*(?![^()]*\))', s)]

        df['service_list'] = df['services_provided'].apply(split_services)

        exploded = df.explode('service_list')
        exploded = exploded[exploded['service_list'].notna() & (exploded['service_list'] != '')]

        exploded['date'] = exploded['timestamp'].dt.normalize()

        daily_counts = exploded.groupby(['date', 'service_list']).size().reset_index(name='count')

        full_dates = pd.date_range(
            df['timestamp'].min().normalize(), 
            df['timestamp'].max().normalize(), 
            freq='D'
        )

        services = exploded['service_list'].unique()
        full_index = pd.MultiIndex.from_product([full_dates, services], names=['date', 'service_list'])

        full_daily = daily_counts.set_index(['date', 'service_list']).reindex(full_index, fill_value=0).reset_index()
        full_daily = full_daily.sort_values(['service_list', 'date'])
        full_daily['cumulative_count'] = full_daily.groupby('service_list')['count'].cumsum()
        fig = go.Figure()

        unique_services = full_daily['service_list'].unique()

        for service in unique_services:
            service_data = full_daily[full_daily['service_list'] == service]
            fig.add_trace(go.Scatter(
                x=service_data['date'],
                y=service_data['cumulative_count'],
                mode='lines',
                name=service
            ))

        fig.update_layout(
            title='Cumulative Count of Services Provided Over Time',
            xaxis_title='Date',
            yaxis_title='Cumulative Count',
            showlegend=False,
            font_color= "#000000"
        )
        apply_plotly_style(fig)
        return fig
#####################################################################################
#####################################################################################
def get_fig_no_count(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
        SELECT
            SUM(CASE WHEN survey_interest = 0 THEN 1 ELSE 0 END) AS no_count
        FROM client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0])
#####################################################################################
#####################################################################################
def get_fig_yes_count(engine, start_date=None, end_date=None):
        where_clause = ""
        if start_date and end_date:
            where_clause = f"WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'"     
        query = f"""
        SELECT
            SUM(CASE WHEN survey_interest = 1 THEN 1 ELSE 0 END) AS yes_count
        FROM client_satisfaction
        {where_clause}
        """
        df = pd.read_sql(query, engine)
        return int(df.iloc[0, 0])

