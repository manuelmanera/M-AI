import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time
import requests

st.set_page_config(page_title="M-AI", layout="centered")

# --- CSS PER INTERFACCIA STILE GEMINI ---
st.markdown("""
    <style>
    /* Nasconde header e icone standard */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Spazio per non far coprire i messaggi dal footer fisso */
    .main .block-container {
        padding-bottom: 150px;
    }

    /* Stile per il contenitore di input fisso in basso */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    
    /* Rende il caricatore file più simile a un tasto '+' */
    .stFileUploader section {
        padding: 0;
        min-height: 0;
        border: none;
    }
    .stFileUploader label {
        display: none;
    }
    
    /* Arrotondamento immagini */
    img {border-radius: 15px;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")

# --- INIZIALIZZAZIONE ---
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VISUALIZZAZIONE CRONOLOGIA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        elif message["type"] == "video":
            st.html(message["content"])
        else:
            st.markdown(message["content"])

# --- ZONA INPUT IN BASSO (STRUTTURA GEMINI) ---
# Usiamo un container fisso o posizionato in fondo
with st.container():
    # Creiamo una riga per simulare i tasti a sinistra e la barra di testo
    col_plus, col_text = st.columns([0.1, 0.9])
    
    with col_plus:
        # Il tasto "+" per caricare i file
        uploaded_file = st.file_uploader("+", type=["jpg", "jpeg", "png"], key="upload_gemini")
    
    with col_text:
        # La barra di testo principale
        prompt = st.chat_input("Chiedi a M-AI...")

# --- LOGICA DI RISPOSTA ---
if prompt:
    # Mostra messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    st.rerun() # Forza il refresh per mostrare il messaggio subito

# Se l'ultimo messaggio è dell'utente, genera risposta
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        p_lower = last_prompt.lower()
        
        # Logica Generativa (Immagini/Video)
        if any(kw in p_lower for kw in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Sto creando..."):
                seed = random.randint(1, 999999)
                clean_prompt = p_lower.replace("genera", "").strip()
                img_url = f"https://image.pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&model=flux"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
        
        # Logica Testuale
        else:
            if client:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "Sei M-AI. Rispondi in modo conciso."},
                              {"role": "user", "content": last_prompt}]
                )
                risposta = completion.choices[0].message.content
                st.markdown(risposta)
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

# Toast di conferma per file caricato
if uploaded_file:
    st.toast(f"Immagine caricata: {uploaded_file.name}", icon="🖼️")
