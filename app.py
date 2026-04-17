import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time

st.set_page_config(page_title="M-AI", layout="centered")

# --- CSS DEFINITIVO PER FIXARE LA BARRA IN BASSO ---
st.markdown("""
    <style>
    /* Nasconde tutto ciò che è superfluo */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}

    /* Crea un margine in fondo per evitare che la chat copra i messaggi */
    .main .block-container {
        padding-bottom: 120px;
    }

    /* Forza il contenitore dell'input a stare fisso in basso */
    [data-testid="stBottom"] > div {
        background-color: transparent;
    }

    /* Stile compatto per il caricatore di file */
    [data-testid="stFileUploader"] {
        position: fixed;
        bottom: 85px; /* Posizionato sopra la barra di testo */
        left: 20px;
        z-index: 1000;
        width: 50px;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0;
        min-height: 40px;
        border: 1px solid #444;
        border-radius: 50%;
        background: #262730;
    }

    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] div {
        display: none;
    }

    /* La barra di testo di Streamlit è già fissa in basso di default */
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")

# --- LOGICA API ---
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VISUALIZZAZIONE MESSAGGI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

# --- ZONA INPUT ---
# In Streamlit, st.chat_input() viene AUTOMATICAMENTE messo in basso. 
# Se lo vedi in alto, è perché c'erano altri elementi che lo spingevano.

# 1. Caricatore file (apparirà come un piccolo tasto sopra la barra grazie al CSS)
uploaded_file = st.file_uploader("+", type=["jpg", "png", "jpeg"])

# 2. Barra di testo (Streamlit la ancora al fondo della finestra)
prompt = st.chat_input("Scrivi a M-AI...")

# --- LOGICA DI RISPOSTA ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    
    with st.chat_message("assistant"):
        if client:
            try:
                # Se l'utente vuole un'immagine
                if any(x in prompt.lower() for x in ["foto", "disegna", "genera"]):
                    img_url = f"https://image.pollinations.ai/p/{prompt.lower()}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
                    st.image(img_url)
                    st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                
                # Altrimenti risposta testuale
                else:
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": "Sei M-AI, un assistente utile."},
                                  {"role": "user", "content": prompt}]
                    )
                    risposta = completion.choices[0].message.content
                    st.markdown(risposta)
                    st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore: {e}")
    
    st.rerun()
