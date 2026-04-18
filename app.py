import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}

    [data-testid="stBottom"] {
        background-color: transparent;
    }

    .main .block-container {
        padding-bottom: 100px;
    }

    div[data-testid="stPopover"] > button {
        border-radius: 50%;
        width: 40px;
        height: 40px;
        padding: 0;
        border: 1px solid #444;
        background-color: #1e1e1e;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")

api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

with st.container():
    with st.sidebar:
        st.write("### Allegati")
        uploaded_file = st.file_uploader("Carica foto", type=["jpg", "png", "jpeg"])

    prompt = st.chat_input("Chiedi a M-AI...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    
    with st.chat_message("assistant"):
        if client:
            # Caso Immagini
            if any(x in prompt.lower() for x in ["foto", "disegna", "genera"]):
                with st.spinner("Sto creando..."):
                    img_url = f"https://image.pollinations.ai/p/{prompt.lower()}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
                    st.image(img_url)
                    st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
            
            else:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "Sei M-AI, un assistente utile creato da Manuel Manera."},
                              {"role": "user", "content": prompt}]
                )
                risposta = completion.choices[0].message.content
                st.markdown(risposta)
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
    
    st.rerun()
