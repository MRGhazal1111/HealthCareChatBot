import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from streamlit_float import *
from datetime import datetime
import os
from dotenv import load_dotenv
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

def log_to_server(name, query):
    # This reads your private sheet, adds a row, and updates it
    existing_data = conn.read(worksheet="Sheet1")
    new_row = {"User": name, "Question": query}
    updated_data = existing_data.append(new_row, ignore_index=True)
    conn.update(worksheet="Sheet1", data=updated_data)

# --- 1. INITIALIZATION & POSITIONING ---
load_dotenv("BotKKK.env")
float_init() # Required for pinning the mic button
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# --- 2. ADVANCED UI STYLING (THE DESIGN) ---
# Add this near the top of Main.py
st.set_page_config(page_title="Medical Assistant", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
    }
    .stTextInput>div>div>input {
        border-color: #007bff;
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

 # Instead of user_name = "MOHAMED GHAZAL"
user_name = st.sidebar.text_input("Assistant for:", value="Guest")
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
# Combine inputs: Trigger if user types OR speaks
user_query = prompt if prompt else audio_text

if user_query:
    # 1. SECRET LOGGING: This sends the data to your Google Sheet
    try:
        log_to_server(user_name, user_query)
    except Exception as e:
        st.sidebar.error(f"Logging Error: {e}")

    # 2. CHAT DISPLAY
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 3. AI RESPONSE
    try:
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.1-8b-instant",
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() 
    except Exception as e:
        st.error(f"AI Error: {e}")

# --- 5. SECRET ADMIN VIEW ---
# This stays at the bottom and only shows for you
if user_name == "Admin_Ghazal":
    st.divider()  
    st.subheader("🕵️ Secret Developer Logs")
    try:
        data = conn.read(worksheet="Sheet1")
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error("Could not load logs. Check your Sheet URL in Secrets.")