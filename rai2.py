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
    tools=[{"type": "file_search"}],
)

# Create vector store + upload docs
vector_store = client.vector_stores.create(name="911 Operator Protocol")
file_paths = [
    "c:\\Users\\leonn\\Prototype4\\RescueAI_Synthetic_911_Scenarios.pdf",
    "c:\\Users\\leonn\\Prototype4\\RescueAI_Traffic_Accidents dialogue transcript.pdf"
]
file_streams = [open(path, "rb") for path in file_paths]
client.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store.id, files=file_streams)

# Attach vector store to assistant
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

def assistant_chatbot(message):
    thread = client.beta.threads.create(messages=[{"role": "user", "content": message}])
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant.id)
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    return messages[0].content[0].text.value

def transcribe_audio(audio_data):
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_data,
        language="en",
    )
    return response.text

def extract_keywords(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"You are a 911 operator assistant. Extract keywords from {text} that would be important \
                for a 911 operator to use. Your response should be in a comma-separated list format. Avoid filler \
                and irrelevant information.",
            },
        ],
    )
    return response.choices[0].message.content

# ===== UI CUSTOM STYLES ===== 🔧 MODIFIED
st.markdown(
    """
    <style>
    /* Main background + text */
    .stApp {
        background-color: #183866;
        color: #fdf6e3;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #c2a611 !important;
        color: black !important;
    }

    /* Make sidebar title black */
    section[data-testid="stSidebar"] h2 {
        color: black !important;
    }

    /* Chat bubbles and input borders */
    .stTextArea, .stChatInput {
        border: 1px solid #c2a611;
        border-radius: 8px;
    }

    .stButton>button {
        background-color: #ffd700;
        color: black;
        border-radius: 8px;
    }

    /* Main header and description styling */
    h1 {
        color: #c2a611;
    }

    .description-text {
        color: #fdf6e3;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== MAIN UI ===== 🔧 MODIFIED
st.title("📞 Emergency Audio Transcription")
st.markdown(
    """
    <div class="description-text">
    <strong style="color:#ffd700;">Upload or record your 911 call audio below.</strong><br>
    The system will transcribe the message and highlight important keywords to assist emergency responders.
    </div>
    """,
    unsafe_allow_html=True
)

audio_file = st.audio_input("🎙️ Record your audio:")

if audio_file:
    transcription = transcribe_audio(audio_file)
    st.subheader("🔍 Extracted Emergency Keywords")
    st.text_area("Keywords:", extract_keywords(transcription), height=200)

# ===== CHATBOT SIDEBAR ===== 🔧 MODIFIED
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.sidebar:
    st.markdown("## 🧠 Rai – 911 Assistant Chatbot")
    st.markdown(
        "Ask Rai about emergency protocols, traffic accident procedures, or how dispatchers should respond to various scenarios. Responses are based on real dispatcher documents."
    )

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input field
    user_input = st.chat_input("💬 Ask Rai a question...")
    if user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.spinner("Rai is thinking..."):
            response = assistant_chatbot(user_input)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
