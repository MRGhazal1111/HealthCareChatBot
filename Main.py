import streamlit as st
from streamlit_gsheets import GSheetsConnection
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from streamlit_float import *
from datetime import datetime
import os
from dotenv import load_dotenv

# --- 1. INITIALIZATION & CONNECTIONS ---
load_dotenv("BotKKK.env")
float_init() 
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# Connect to your secret Google Sheet server
conn = st.connection("gsheets", type=GSheetsConnection)

def log_to_server(name, query):
    """Logs user questions to your private Google Sheet with a timestamp"""
    try:
        # Get current time for your records
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_data = conn.read(worksheet="Sheet1")
        new_row = {"User": name, "Question": query, "Time": now}
        updated_data = existing_data.append(new_row, ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_data)
    except Exception as e:
        print(f"Logging failed: {e}")

# --- 2. UI STYLING ---
st.set_page_config(page_title="Medical Assistant", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 10px; }
    .stTextInput>div>div>input { border-color: #007bff; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR & PERSONALIZATION ---
with st.sidebar:
    st.title("⚕️ Support Center")
    st.error("🚨 **TURKIYE EMERGENCY**\n\n📞 General: 112\n\n📞 Health: 184")
    
    # Sign-in logic for your friends (Responsive)
    user_name = st.text_input("Assistant for:", value="Guest")
    
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

st.title(f"Good morning, {user_name}!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a professional medical assistant."}]

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. INPUT LOGIC (MIC & TEXT) ---
footer_container = st.container()
with footer_container:
    audio_text = speech_to_text(
        start_prompt="🎤", stop_prompt="✅", language='en', key='mic'
    )

footer_container.float("bottom: 2.1rem; right: 4rem; position: fixed;")

prompt = st.chat_input("Ask about your symptoms...")
user_query = prompt if prompt else audio_text

# --- 5. THE BRAIN & LOGGING TRIGGER ---
if user_query:
    # This line MUST be present and correctly indented to send data
    log_to_server(user_name, user_query) 

    st.session_state.messages.append({"role": "user", "content": user_query})
    # ... rest of your code ...
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
        st.rerun() 
    except Exception as e:
        st.error(f"Error: {e}")

# --- 6. SECRET ADMIN VIEW ---
# Hidden dashboard: Only shows if you type "Admin_Ghazal" in the sidebar
if user_name == "Admin_Ghazal":
    st.divider()  
    st.subheader("🕵️ Secret Developer Logs")
    try:
        data = conn.read(worksheet="Sheet1")
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error("Could not load logs. Check your Sheet URL in Secrets.")