import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time
import requests
import base64
import numpy as np

st.set_page_config(page_title="M-BR0WS3R | AI Architecture", layout="wide")

st.markdown("""
    <style>
    :root {
        --bg-color: #f5f5f7;
        --card-bg: rgba(255, 255, 255, 0.7);
        --text-main: #1d1d1f;
        --text-secondary: #86868b;
        --gradient-1: #ff00cc;
        --gradient-2: #3333ff;
        --gradient-3: #00ffcc;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0b0b0d;
            --card-bg: rgba(28, 28, 32, 0.6);
            --text-main: #f5f5f7;
            --text-secondary: #9a9a9f;
        }
    }

    /* Reset e Body Identici */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        line-height: 1.5;
    }

    [data-testid="stHeader"], [data-testid="stFooterBlock"] {
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 900px !important;
    }

    /* Elementi HTML Originali */
    .brand-title {
        font-size: 4rem !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        margin-bottom: 10px !important;
        text-align: center;
        background: linear-gradient(90deg, var(--gradient-1), var(--gradient-2), var(--gradient-3));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: var(--text-secondary);
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 40px;
    }

    /* Container 3D Perspective & Card Concept */
    .card-container {
        position: relative;
        padding: 4px;
        border-radius: 40px;
        background: conic-gradient(from 45deg, var(--gradient-1), var(--gradient-2), var(--gradient-3), var(--gradient-1));
        animation: hue-shift 8s linear infinite;
        width: 100%;
        margin-bottom: 35px;
        box-shadow: 0 30px 60px -20px rgba(0, 0, 0, 0.28), 0 10px 25px -12px rgba(0, 0, 0, 0.18);
    }

    @media (prefers-color-scheme: dark) {
        .card-container {
            box-shadow: 0 30px 70px -20px rgba(0, 0, 0, 0.7), 0 10px 25px -12px rgba(0, 0, 0, 0.5);
        }
    }

    @keyframes hue-shift {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }

    .card {
        position: relative;
        z-index: 1;
        background: var(--card-bg);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-radius: 36px;
        padding: 40px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
    }

    @media (prefers-color-scheme: dark) {
        .card {
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }
    }

    /* Customizzazione Chat Streamlit per nascondere i default */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Titoli e testi allineati */
    h2 { font-size: 2.2rem !important; font-weight: 700; margin-bottom: 15px; color: var(--text-main); }
    p { color: var(--text-secondary) !important; font-size: 1.15rem; }

    /* Fix Input Box in fondo */
    [data-testid="stChatInput"] {
        background-color: var(--card-bg) !important;
        border: 1px solid rgba(134, 134, 139, 0.3) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(20px);
    }

    .visual-box {
        background: rgba(255,255,255,0.3);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
    }
    @media (prefers-color-scheme: dark) {
        .visual-box { background: rgba(255, 255, 255, 0.08); }
    }

    img, video {
        border-radius: 20px;
        max-width: 100%;
        height: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# Header Premium Apple-Style identico
st.markdown('<h1 class="brand-title">M-BR0WS3R</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">L\'intelligence artificiale, ridefinita.</p>', unsafe_allow_html=True)

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Configura GROQ_API_KEY nei Secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

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

# Renderizzazione della cronologia dentro le Card con Bordo Arcobaleno Animato
for message in st.session_state.messages:
    role_title = "Tu" if message["role"] == "user" else "M-BR0WS3R"
    
    st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <h2>{role_title}</h2>
            <div id="content-anchor">
    """, unsafe_allow_html=True)
    
    if message["type"] == "image": 
        st.image(message["content"])
    elif message["type"] == "video": 
        st.html(message["content"])
    else: 
        st.markdown(f"<p>{message['content']}</p>", unsafe_allow_html=True)
        
    st.markdown("</div></div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color:var(--text-main);'>Sistema Biometrico</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Carica volto per estrazione matrice", type=["jpg", "jpeg", "png"])

if prompt := st.chat_input("Chiedi qualcosa o analizza una foto..."):
    # Messaggio Utente
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    st.markdown(f"""
    <div class="card-container">
        <div class="card">
            <h2>Tu</h2>
            <p>{prompt}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Risposta Assistente dentro la Card con stile esatto
    p = prompt.lower()
    
    st.markdown("""
    <div class="card-container">
        <div class="card">
            <h2>M-BR0WS3R</h2>
    """, unsafe_allow_html=True)
    
    # 1. BIOMETRIA
    if uploaded_file is not None and any(x in p for x in ["matrice", "cerca", "analizza", "identifica"]):
        matrice = generate_mock_matrix()
        st.markdown(f"""
        <div class="visual-box" style="margin-bottom:20px;">
            <p style="font-size:0.9rem; font-family:monospace; word-break:break-all;">Vector_Matrix: {str(matrice[:6])}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        base64_image = encode_image(uploaded_file)
        try:
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": [{"type": "text", "text": f"Dato l'embedding, identifica la persona (nome e social finti). Profilo finto. Domanda: {prompt}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            )
            risposta = response.choices[0].message.content
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
        except Exception as e:
            st.error(f"Errore: {e}")
            
    # 2. IDENTITÀ CRONOLOGICA
    elif any(x in p for x in ["creato", "progettato", "manuel", "chi ti ha fatto"]):
        risposta = "Sono stata progettata da Manuel Manera."
        st.write_stream(stream_data(risposta))
        st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

    # 3. IMMAGINI
    elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
        clean_p = prompt.replace(" ", "%20")
        img_url = f"https://image.pollinations.ai/p/{clean_p}?width=1024&height=1024&seed={random.randint(1,99999)}&model=flux"
        success = False
        for _ in range(3):
            if is_valid_image(img_url):
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                success = True
                break
            time.sleep(2)
        if not success: 
            st.write("Server lento. Riprova.")

    # 4. VIDEO
    elif "video" in p:
        clean_p = prompt.replace(" ", "%20")
        video_html = f'<div class="visual-box"><video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video></div>'
        st.html(video_html)
        st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

    # 5. DIALOGO GENERALE + SEARCH
    else:
        try:
            search = ""
            with DDGS() as ddgs:
                for r in ddgs.text(prompt, max_results=3): search += f"\n- {r['body']}"
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Sei l'architettura AI M-BR0WS3R creata da Manuel Manera."},
                    {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                ]
            )
            risposta = completion.choices[0].message.content
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
        except Exception as e:
            st.error(f"Errore: {e}")

    st.markdown("</div></div>", unsafe_allow_html=True)
