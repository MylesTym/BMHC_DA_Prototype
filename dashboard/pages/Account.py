import streamlit as st
st.set_page_config(layout="wide", page_title="Login")
import os
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component
import requests

st.write("DEBUG: query_params:", st.query_params)
st.write("DEBUG: session_state:", dict(st.session_state))


load_dotenv()
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

redirect_uri = "http://localhost:8501/Account"  # Note: points to login page
authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"

access_token_url = "https://oauth2.googleapis.com/token"
scope = "openid email profile"

oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint=authorize_url,
    token_endpoint=access_token_url,
)
if not st.session_state.get('authenticated'):
    st.title("Login Required")
    st.write(f"DEBUG: Session state = {st.session_state}")

    token = oauth2.authorize_button(
        "Login with Google",
        redirect_uri=redirect_uri,
        scope=scope
    )
    st.write(f"DEBUG: Token = {token}")  # DEBUG
    st.write(f"DEBUG: Query params = {st.query_params}")

    if token:
        st.write("DEBUG: Token received!")
        headers = {"Authorization": f"Bearer {token['token']['access_token']}"}
        response = requests.get("https://openidconnect.googleapis.com/v1/userinfo", headers=headers)
        user_info = response.json()
        email = user_info.get("email")
        given_name = user_info.get('given_name')

        st.write(f"DEBUG: Email = {email}")

        if email and email.endswith("@blackmenshealthclinic.org"):
            st.write("DEBUG: Setting session state...")
            st.session_state['authenticated'] = True
            st.session_state['email'] = email
            st.session_state['given_name'] = given_name
            st.success(f"Welcome, {given_name}! Redirecting...")
            st.switch_page("home.py")  # Redirect to home
        else:
            st.error("Access restricted to @blackmenshealthclinic.org emails.")
else:
    st.success(f"Logged in as {st.session_state.get('email')}")
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['email'] = None
        st.rerun()