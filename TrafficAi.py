import streamlit as st
from openai import OpenAI

client = OpenAI(api_key="open-ai-key")  # Replace with your actual key

st.set_page_config(page_title="Traffic Cam AI", layout="centered")
#Title
st.markdown(
    """
    <h1 style='text-align: center;'>🚨 Traffic Cam AI</h1>
    <h4 style='text-align: center; color: gray;'>AI-generated images of reckless driving</h4>
    <hr>
    """,
    unsafe_allow_html=True
)

#Prompt builder for reckless driving from traffic cam POV
def build_image_prompt():
    return (
        "A high-resolution image from the point of view of a traffic camera showing reckless driving. "
        "The scene includes a speeding car running a red light, urban city background, and motion blur."
    )

#Generate 1 image
def image_generation():
    prompt = build_image_prompt()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return [img.url for img in response.data]

#Button to generate images
if st.button("Generate Traffic Camera Images"):
    with st.spinner("Generating images..."):
        image_urls = image_generation()
        for url in image_urls:
            st.image(url)
            st.markdown("---")
