import streamlit as st
import os
import openai
from openai import OpenAI
from pathlib import Path

st.markdown("# Page 1: Feature 1")
st.sidebar.markdown("# Page 1: Feature 1")


openai.api_key = os.environ["OPENAI_API_KEY"]
