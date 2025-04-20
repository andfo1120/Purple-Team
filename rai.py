import os
import openai
from openai import OpenAI
import streamlit as st

# Set up OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

# Create the assistant
assistant = client.beta.assistants.create(
    name="911 Operator Assistant",
    instructions='You are a 911 operator assistant. Answer questions using information only from the provided file. \
                    Your response must be in an informative, yet concise list format. If there is no information in \
                    the file that can answer a question, answer with "Sorry, I am unable to answer this question, as \
                    it is not covered by protocol."',
    model="gpt-4o",
    tools=[{"type": "file_search"}], # Use file_search tool type
)

# Create a vector store called "911 Operator Protocol"
vector_store = client.vector_stores.create(name="911 Operator Protocol")

# Ready the files for upload to OpenAI
file_paths = ["C:\\vsc\\rai\\RescueAI_Synthetic_911_Scenarios.pdf", "C:\\vsc\\rai\\RescueAI_Traffic_Accidents dialogue transcript.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# Update the assistant to use the new vector store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

def assistant_chatbot(message, assistant=assistant, vector_store=vector_store):
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ]
    )

    # Use the create and poll SDK helper to create a run and poll the status of
    # the run until it's in a terminal state.

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(
        client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
    )

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(
            annotation.text, f"[{index}]"
        )
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    print(citations)
    return message_content.value

def transcribe_audio(audio_data):
    # Send the audio data to OpenAI for transcription
    response = openai.audio.transcriptions.create(
        model="whisper-1",  # Specify the Whisper model
        file=audio_data,
        language="en",
    )
    return response.text

st.write("Run the 911 call through here...")

def extract_keywords(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"You are a 911 operator assistant. Extract keywords from {text} that would be important \
                for a 911 operator to use. Your response should be in a comma-separated list format. Avoid filler \
                and irrelevant information.",
            }
        ],
    )
    return response.choices[0].message.content

# Audio input capture
audio_file = st.audio_input("Record your audio:")

if audio_file:

    # Transcribe the audio using OpenAI Whisper
    transcription = transcribe_audio(audio_file)

    # Display the transcribed text in a text box
    st.text_area("Transcribed Text", extract_keywords(transcription), height=200)

def chat():
    user_input = st.chat_input(
        "I'm Rai, your 911 operator assistant. How can I help you?"
    )
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        response = assistant_chatbot(user_input)
        response = response.replace(" [0]", "")
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Create a sidebar for chatbot interactions
with st.sidebar:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
        # Input at the bottom of sidebar
    chat()