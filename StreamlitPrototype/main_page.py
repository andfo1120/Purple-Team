import streamlit as st
import pandas as pd
import numpy as np
import time
from openai import OpenAI
import fitz


def load_pdf_text(file_path):
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


sj_ems_destination_text = load_pdf_text("C:/Users/Jared/Desktop/AI911OPERATOR/sjems.pdf")
sjpd_mobile_response_text = load_pdf_text("C:/Users/Jared/Desktop/AI911OPERATOR/sjmobile.pdf")


client = OpenAI(api_key="my-api-key") 


def get_completion(user_input, model="gpt-3.5-turbo"):
    # Concatenate reference materials
    reference_material = (
        f"SJ 911 EMS Destination:\n{sj_ems_destination_text}\n\n"
        f"SJPD Mobile Response Guide:\n{sjpd_mobile_response_text}\n\n"
    )

    system_prompt = (   
        f"Answer the following question using the reference materials provided below. "
        f"Assume the person asking is knowledgeable about emergency procedures:\n\n"
        f"QUESTION: {user_input}\n"
        f"{reference_material}"
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
    )
    return completion.choices[0].message.content




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
def homepage():
    st.title("RescueAI")
    st.write("Every second counts in an emergency.")

def guidelinespage():
    st.title("911 Operator Guidelines")
    
    with st.form(key="911_operator_guide"):
        prompt = st.text_input("Ask a question:")
        submitted = st.form_submit_button("Get Answer") 

    if submitted and prompt:
        with st.spinner("Generating insights..."):
         response_information = get_completion(prompt)


        st.write(response_information)
def transpage():
    st.title("Live Call Transciption")
    st.write("This page allows a user to transcribe a call LIVE!")
    st.success("You're viewing Page 2!")

    audio_value = st.audio_input("Pass the 911 call here:")

    if audio_value:
        st.audio(audio_value)

# Display current page
if st.session_state.page == "Home":
    homepage()
elif st.session_state.page == "Guidelines":
    guidelinespage()
elif st.session_state.page == "Live Transcription":
    transpage()
