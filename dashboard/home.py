import streamlit as st
st.set_page_config(layout="wide", page_title="Homepage")
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.switch_page("pages/login.py")
import os
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component


#####################################################################################
#####################################################################################
load_dotenv()
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

# Add these debug lines temporarily
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
#####################################################################################
#####################################################################################

redirect_uri = "http://localhost:8501/"
authorize_url = "https://accounts.google.com/o/oauth2/auth"
access_token_url = "https://oauth2.googleapis.com/token"
scope = "openid email profile"

oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint=authorize_url,
    token_endpoint=access_token_url)
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
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
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
        background: linear-gradient(to bottom, #d0a53f, #4A0E4E);
    }
    [data-testid="stMetric"] div, 
    [data-testid="stMetric"] span, 
    [data-testid="stMetricLabel"], 
    [data-testid="stMetricValue"] {
        color: black !important;
        text-align: center;
        justify-content: center;
        align-items: center;
        display: flex;
        flex-direction: column;
        }
    [data-testid="stVerticalBlock"]{
        margin-bottom: 0rem !important;
        padding-bottom: 0rem !important;
        padding-top: 0rem !important;
    }
    }
    """,
    unsafe_allow_html=True
)

#####################################################################################
#####################################################################################
# Title
st.title("BMHC Prototype Analytics App")
st.header("This is the landing page")
st.subheader("Information can be placed here")

st.markdown("""
### About Us
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed euismod, urna eu tincidunt consectetur, nisi nisl aliquam nunc, 
non posuere sapien neque a justo. Integer vel turpis nec nulla 
fermentum tincidunt vitae nec erat.
            
Vivamus eget ligula nec nulla facilisis accumsan. 
Mauris non orci nec justo gravida tincidunt. 
Etiam ac lorem at elit tincidunt ultricies. 
Sed sed risus vel lacus luctus fermentum. 
Phasellus euismod, velit at facilisis sagittis, 
nisi erat blandit magna, nec hendrerit nulla lorem nec sapien.
""")
