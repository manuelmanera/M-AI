import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time
import requests
import base64
import numpy as np

st.set_page_config(page_title="M-AI | AI Architecture", layout="wide")

st.markdown("""
    <style>
    :root {
        --bg-color: #f5f5f7;
        --card-bg: rgba(255, 255, 255, 0.05);
        --text-main: #1d1d1f;
        --text-secondary: #86868b;
        --gradient-1: #ff00cc;
        --gradient-2: #3333ff;
        --gradient-3: #00ffcc;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0b0b0d;
            --card-bg: rgba(255, 255, 255, 0.05);
            --text-main: #f5f5f7;
            --text-secondary: #9a9a9f;
        }
    }

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        line-height: 1.4;
    }

    [data-testid="stHeader"], [data-testid="stFooterBlock"] {
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 700px !important;
    }

    .brand-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px !important;
        margin-bottom: 5px !important;
        text-align: center;
        background: linear-gradient(90deg, var(--gradient-1), var(--gradient-2), var(--gradient-3));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 30px;
    }

    .chat-role-label {
        font-size: 0.85rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        margin-bottom: 4px;
        margin-left: 8px;
    }

    .card-container {
        position: relative;
        padding: 3px;
        border-radius: 20px;
        background: conic-gradient(from 45deg, var(--gradient-1), var(--gradient-2), var(--gradient-3), var(--gradient-1));
        animation: hue-shift 8s linear infinite;
        width: 100%;
        margin-bottom: 25px;
        box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.15);
    }

    @keyframes hue-shift {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }

    .card {
        position: relative;
        z-index: 1;
        background: var(--bg-color);
        border-radius: 17px;
        padding: 18px 24px;
    }

    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .card p { 
        color: var(--text-main) !important; 
        font-size: 1.05rem; 
        margin-bottom: 0px !important;
        display: inline !important;
    }

    [data-testid="stChatInput"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(134, 134, 139, 0.3) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(20px);
    }

    .visual-box {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
    }

    img, video {
        border-radius: 16px;
        max-width: 100%;
        height: auto;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">M-AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">L\'intelligenza artificiale, ridefinita.</p>', unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Configura GROQ_API_KEY nei Secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def is_valid_image(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def generate_mock_matrix():
    matrix = np.random.uniform(-1, 1, (1, 128))
    return matrix.tolist()[0]

# Renderizzazione dello storico dei messaggi nelle caselle corrette
for message in st.session_state.messages:
    role_title = "Tu" if message["role"] == "user" else "M-AI"
    st.markdown(f'<div class="chat-role-label">{role_title}</div>', unsafe_allow_html=True)
    
    if message["type"] == "text":
        st.markdown(f"""
        <div class="card-container">
            <div class="card">
                <p>{message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif message["type"] == "image":
        st.markdown('<div class="card-container"><div class="card">', unsafe_allow_html=True)
        st.image(message["content"])
        st.markdown('</div></div>', unsafe_allow_html=True)
    elif message["type"] == "video":
        st.markdown('<div class="card-container"><div class="card">', unsafe_allow_html=True)
        st.html(message["content"])
        st.markdown('</div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color:var(--text-main);'>Sistema Biometrico</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Carica volto per estrazione matrice", type=["jpg", "jpeg", "png"])

if prompt := st.chat_input("Chiedi qualcosa o analizza una foto..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    
    # Messaggio Utente
    st.markdown('<div class="chat-role-label">Tu</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <p>{prompt}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p = prompt.lower()
    
    # Messaggio Assistente (Viene creato un box vuoto iniziale)
    st.markdown('<div class="chat-role-label">M-AI</div>', unsafe_allow_html=True)
    response_placeholder = st.empty()

    risposta = ""
    tipo_risposta = "text"
    
    if uploaded_file is not None and any(x in p for x in ["matrice", "cerca", "analizza", "identifica"]):
        matrice = generate_mock_matrix()
        base64_image = encode_image(uploaded_file)
        try:
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": [{"type": "text", "text": f"Dato l'embedding, identifica la persona (nome e social finti). Domanda: {prompt}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            )
            risposta = response.choices[0].message.content
        except Exception as e:
            risposta = f"Errore: {e}"
            
    elif any(x in p for x in ["creato", "progettato", "manuel", "chi ti ha fatto"]):
        risposta = "Sono stata progettata da Manuel Manera."

    elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
        clean_p = prompt.replace(" ", "%20")
        img_url = f"https://image.pollinations.ai/p/{clean_p}?width=1024&height=1024&seed={random.randint(1,99999)}&model=flux"
        if is_valid_image(img_url):
            risposta = img_url
            tipo_risposta = "image"
        else:
            risposta = "Errore durante la generazione dell'immagine."

    elif "video" in p:
        clean_p = prompt.replace(" ", "%20")
        risposta = f'<div class="visual-box"><video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video></div>'
        tipo_risposta = "video"

    else:
        try:
            search = ""
            with DDGS() as ddgs:
                for r in ddgs.text(prompt, max_results=3): search += f"\n- {r['body']}"
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Sei l'architettura AI M-AI creata da Manuel Manera."},
                    {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                ]
            )
            risposta = completion.choices[0].message.content
        except Exception as e:
            risposta = f"Errore: {e}"

    # Aggiorna il box inserendo l'HTML definitivo contenente il testo
    st.session_state.messages.append({"role": "assistant", "content": risposta, "type": tipo_risposta})
    
    if tipo_risposta == "text":
        response_placeholder.markdown(f"""
        <div class="card-container">
            <div class="card">
                <p>{risposta}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif tipo_risposta == "image":
        with response_placeholder.container():
            st.markdown('<div class="card-container"><div class="card">', unsafe_allow_html=True)
            st.image(risposta)
            st.markdown('</div></div>', unsafe_allow_html=True)
    elif tipo_risposta == "video":
        with response_placeholder.container():
            st.markdown('<div class="card-container"><div class="card">', unsafe_allow_html=True)
            st.html(risposta)
            st.markdown('</div></div>', unsafe_allow_html=True)
