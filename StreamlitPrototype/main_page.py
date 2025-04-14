import streamlit as st
import pandas as pd
import numpy as np
import time



# Set page configuration
st.set_page_config(page_title="Button-Based Navigation", layout="centered")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar button navigation
with st.sidebar:
    st.title("Navigation")

    if st.button("Home"):
        st.session_state.page = "Home"
    if st.button("Guidelines"):
        st.session_state.page = "Guidelines"
    if st.button("Live Transcription"):
        st.session_state.page = "Live Transcription"

# Define page functions
def home():
    st.title("RescueAI")
    st.write("Every second counts in an emergency.")

def page1():
    st.title("911 Operator Guidelines")

    # User input textbox
    user_input = st.text_input("What would you like to know?")

def page2():
    st.title("Live Call Transciption")
    st.write("This page allows a user to transcribe a call LIVE!")
    st.success("You're viewing Page 2!")

# Display current page
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Guidelines":
    page1()
elif st.session_state.page == "Live Transcription":
    page2()
