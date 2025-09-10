# app.py
import streamlit as st
from detection_ui import run_detection_ui
from chatbot_ui import run_chatbot_ui
from reports_ui import run_reports_ui

# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="SafeRideAI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚦 SafeRideAI - Professional Dashboard")
st.markdown("""
Welcome to **SafeRideAI**!  
Use the tabs below to access detection, chatbot assistant, and email reports.
""")

# ==============================
# Tabs for Different Modules
# ==============================
tabs = st.tabs(["🛠️ Detection", "💬 Chatbot Assistant", "📧 Reports"])

with tabs[0]:
    st.header("🛠️ Detection")
    detection_ui()

with tabs[1]:
    st.header("💬 Chatbot Assistant")
    chatbot_ui()

with tabs[2]:
    st.header("📧 Reports")
    reports_ui()
