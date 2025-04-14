import streamlit as st
import os
import openai
from openai import OpenAI
from pathlib import Path

st.markdown("# Page 3: Feature 3")
st.sidebar.markdown("# Page 3: Feature 3")


openai.api_key = os.environ["OPENAI_API_KEY"]
