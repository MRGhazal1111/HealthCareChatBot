import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from streamlit_float import *
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
load_dotenv("BotKKK.env")
float_init() 
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def log_to_server(name, query):
    """Saves user questions to a secret text file on the server with TR time"""
    # Fix: Forced Türkiye Time (UTC+3)
    tr_time = datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M:%S")
    with open("secret_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{tr_time} | User: {name} | Question: {query}\n")

# --- 2. UI STYLING ---
st.set_page_config(page_title="Medical Assistant", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 10px; width: 100%; }
    .stTextInput>div>div>input { border-color: #007bff; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE WELCOME GATE (NAME FIRST) ---
if "user_name" not in st.session_state:
    st.markdown("## ⚕️ Medical Assistant Portal")
    st.info("Welcome! Please enter your name to start the secure consultation.")
    name_input = st.text_input("Full Name:", placeholder="e.g. Mohamed Ghazal")
    
    if st.button("Enter Assistant"):
        if name_input:
            st.session_state.user_name = name_input
            st.rerun()
        else:
            st.warning("Please provide a name to continue.")
    st.stop() 

user_name = st.session_state.user_name

# --- 4. FLEXIBLE GREETING (TÜRKİYE TIME FIX) ---
# Calculate hour based on TR Time (UTC+3) to ensure it says Good Evening correctly
tr_hour = datetime.now(timezone(timedelta(hours=3))).hour

if 5 <= tr_hour < 12:
    greeting = "Good morning"
elif 12 <= tr_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

# --- 5. SIDEBAR & CHAT INTERFACE ---
with st.sidebar:
    st.title("⚕️ Support Center")
    st.write(f"Logged in as: **{user_name}**")
    st.error("🚨 **TURKIYE EMERGENCY**\n\n📞 General: 112\n\n📞 Health: 184")
    
    if st.button("🚪 Sign Out / Change Name"):
        del st.session_state.user_name
        st.rerun()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title(f" {greeting}, {user_name}!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a professional medical assistant."}]

# Display chat messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. INPUT & LOGGING LOGIC ---
footer_container = st.container()
with footer_container:
    audio_text = speech_to_text(start_prompt="🎤", stop_prompt="✅", language='en', key='mic')

footer_container.float("bottom: 2.1rem; right: 4rem; position: fixed;")
prompt = st.chat_input("Ask about your symptoms...")
user_query = prompt if prompt else audio_text

if user_query:
    # Trigger: Save data to the secret text file
    log_to_server(user_name, user_query)
    
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
        st.rerun() 
    except Exception as e:
        st.error(f"Error: {e}")

# --- 7. SECURE ADMIN VIEW ---
# Access this by typing Admin_Ghazal in the Welcome Gate
if user_name == "Admin_Ghazal":
    st.divider()
    st.subheader("🕵️ Secure Developer Portal")
    admin_pass = st.text_input("Admin Password:", type="password")
    
    if admin_pass == "2253":
        st.success("Access Granted")
        if os.path.exists("secret_logs.txt"):
            with open("secret_logs.txt", "r", encoding="utf-8") as f:
                logs = f.read()
            st.text_area("Live Data Log (All Users):", value=logs, height=400)
            st.download_button("Download Logs", logs, file_name="medical_logs.txt")
        else:
            st.info("No logs recorded yet.")
    elif admin_pass != "":
        st.error("Incorrect Password")