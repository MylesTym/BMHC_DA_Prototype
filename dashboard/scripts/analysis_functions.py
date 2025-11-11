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