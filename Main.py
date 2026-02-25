import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
from streamlit_float import *
from datetime import datetime
import os
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
load_dotenv("BotKKK.env")
float_init() 
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def log_to_server(name, query):
    """Saves user questions to a secret text file on the server"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # This writes directly to the server's hard drive
    with open("secret_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{now} | User: {name} | Question: {query}\n")

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
    
    # Sign-in logic for your friends
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
    # This triggers the secret text file log
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

# --- 6. SECURE ADMIN VIEW ---
if user_name == "Admin_Ghazal":
    st.divider()
    st.subheader("🕵️ Secure Developer Portal")
    
    # Password protection
    password = st.text_input("Enter Admin Password:", type="password")
    
    if password == "2253":  # You can change this to any password you want
        if os.path.exists("secret_logs.txt"):
            with open("secret_logs.txt", "r", encoding="utf-8") as f:
                logs = f.read()
            
            st.success("Access Granted")
            st.text_area("Live Logs:", value=logs, height=400)
            st.download_button("Download Logs", logs, file_name="medical_logs.txt")
        else:
            st.info("No logs recorded yet.")
    elif password != "":
        st.error("Incorrect Password")