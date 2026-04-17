import streamlit as st
from groq import Groq
import random
import time

st.set_page_config(page_title="M-AI", layout="centered")

# --- CSS AVANZATO PER POSIZIONAMENTO FISSO IN BASSO ---
st.markdown("""
    <style>
    /* Nasconde elementi superflui */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}

    /* Crea spazio in fondo alla pagina per non coprire i messaggi */
    .main .block-container {
        padding-bottom: 180px;
    }

    /* Contenitore per la barra di input e il tasto upload */
    div.stChatInputContainer {
        padding: 0px;
    }

    /* Rende il caricatore file compatto e lo allinea */
    [data-testid="stFileUploader"] {
        padding: 0;
        margin-bottom: -50px; /* Allineamento millimetrico con la barra */
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0;
        min-height: 45px;
    }

    [data-testid="stFileUploader"] label {
        display: none;
    }

    /* Stile per le immagini */
    img {border-radius: 15px;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")

# --- INIZIALIZZAZIONE SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VISUALIZZAZIONE MESSAGGI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        else:
            st.markdown(message["content"])

# --- IL "FOOTER" STILE GEMINI ---
# Usiamo un contenitore che Streamlit renderizza in fondo
with st.container():
    # Creiamo due colonne: una piccolissima per il '+' e una grande per il testo
    col_upload, col_input = st.columns([0.15, 0.85])
    
    with col_upload:
        # Il caricatore file (apparirà come un tasto "+" o "Upload" compatto)
        uploaded_file = st.file_uploader("+", type=["jpg", "jpeg", "png"], key="gemini_upload")
    
    with col_input:
        # La chat input nativa che Streamlit mette SEMPRE in fondo
        prompt = st.chat_input("Chiedi a M-AI...")

# --- LOGICA DI RISPOSTA ---
if prompt:
    # Aggiungi messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    
    # Esempio risposta (sostituisci con la tua logica Groq)
    with st.chat_message("assistant"):
        if any(x in prompt.lower() for x in ["foto", "genera"]):
            st.spinner("Generazione...")
            img_url = f"https://image.pollinations.ai/p/{prompt.lower()}?width=1024&height=1024&seed={random.randint(1,100)}&model=flux"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
        else:
            risposta = "Ecco la tua risposta!" # Qui chiameresti Groq
            st.markdown(risposta)
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
    
    st.rerun()

if uploaded_file:
    st.sidebar.image(uploaded_file, caption="Immagine pronta per l'uso")
