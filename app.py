import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time
import requests

st.set_page_config(page_title="M-AI", layout="centered")

# --- CSS PER DESIGN GEMINI (BARRA IN BASSO) ---
st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #333;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Spazio per la barra fissa */
    .main .block-container {padding-bottom: 150px;}

    /* Rende il caricatore file piccolo e allineato */
    [data-testid="stFileUploader"] {padding: 0; margin-bottom: -50px;}
    [data-testid="stFileUploader"] section {padding: 0; min-height: 40px; border: none;}
    [data-testid="stFileUploader"] label {display: none;}
    
    img {border-radius: 15px;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")

# --- CONNESSIONE API ---
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Inserisci GROQ_API_KEY nei Secrets.")
    st.stop()
client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

# --- VISUALIZZAZIONE CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

# --- INPUT AREA (BARRA IN BASSO) ---
with st.container():
    col_plus, col_txt = st.columns([0.15, 0.85])
    with col_plus:
        uploaded_file = st.file_uploader("+", type=["jpg", "png", "jpeg"], key="upload")
    with col_txt:
        prompt = st.chat_input("Chiedi a M-AI...")

# --- LOGICA DI RISPOSTA REALE ---
if prompt:
    # Aggiunge il messaggio dell'utente alla cronologia
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()

        # 1. Generazione Immagini/Video
        if any(k in p_lower for k in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Sto creando..."):
                seed = random.randint(1, 999999)
                img_url = f"https://image.pollinations.ai/p/{p_lower}?width=1024&height=1024&seed={seed}&model=flux"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})

        # 2. Risposta Testuale Reale con Groq
        else:
            try:
                # Ricerca web opzionale
                search_context = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=2):
                        search_context += f"\n- {r['body']}"

                # Chiamata a Llama tramite Groq
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei M-AI, un assistente utile creato da Manuel Manera. Rispondi in italiano."},
                        {"role": "user", "content": f"Contesto web: {search_context}\n\nDomanda: {prompt}"}
                    ],
                    temperature=0.7
                )
                
                risposta = completion.choices[0].message.content
                # Visualizzazione con effetto scrittura
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

            except Exception as e:
                st.error(f"Errore: {e}")

# Se carichi un file, avvisa l'utente
if uploaded_file:
    st.toast(f"Immagine ricevuta: {uploaded_file.name}")
