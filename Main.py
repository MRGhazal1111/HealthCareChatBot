import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from streamlit_float import *
from datetime import datetime
import os
from dotenv import load_dotenv

# --- 1. INITIALIZATION & POSITIONING ---
load_dotenv("BotKKK.env")
float_init() # Required for pinning the mic button
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# --- 2. ADVANCED UI STYLING (THE DESIGN) ---
st.set_page_config(page_title="AI Health Assistant Pro", layout="wide")

st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        margin-bottom: 10px !important;
    }

    /* THE MAGIC: Adjusting the Chat Input to leave room for the mic */
    .stChatInputContainer {
        padding-right: 50px !important;
        border-radius: 25px !important;
        border: 1px solid #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR & GREETING ---
with st.sidebar:
    st.title("⚕️ Support Center")
    st.error("🚨 **TURKIYE EMERGENCY**\n\n📞 General: 112\n\n📞 Health: 184")
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

user_name = "MOHAMED GHAZAL"
st.title(f"Good morning, {user_name}!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a professional medical assistant."}]

# Display history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. THE INLINE MIC & INPUT ---
# Create a container that will "float" the mic into the chat box
footer_container = st.container()

with footer_container:
    # This button returns text directly from your voice
    audio_text = speech_to_text(
        start_prompt="🎤", 
        stop_prompt="✅", 
        language='en', 
        use_container_width=False, 
        key='mic'
    )

# Floating Logic: Moves the mic button into the chat bar area
footer_container.float("bottom: 2.1rem; right: 4rem; position: fixed;")

# Main Chat Input
prompt = st.chat_input("Ask about your symptoms...")

# Combine inputs: Trigger if user types OR speaks
user_query = prompt if prompt else audio_text

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    try:
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.1-8b-instant",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() # Refresh to clear the mic state
    except Exception as e:
        st.error(f"Error: {e}")