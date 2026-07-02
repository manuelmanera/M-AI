import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time
import requests
import base64
import numpy as np

st.set_page_config(page_title="M-AI", layout="centered")

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

    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none;
    }

    .stChatMessage {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(134, 134, 139, 0.2) !important;
        padding: 20px 0 !important;
    }

    h1.brand-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -2px !important;
        margin-bottom: 5px !important;
        text-align: center;
        background: linear-gradient(90deg, var(--gradient-1), var(--gradient-2), var(--gradient-3));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: var(--text-secondary);
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
    }

    img {
        border-radius: 20px !important;
        max-width: 100%;
        height: auto;
    }

    .stCodeBlock {
        background-color: var(--card-bg) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(134, 134, 139, 0.2) !important;
    }

    /* Card Biometrica Premium con Bordo Animato */
    .biometric-card-container {
        position: relative;
        padding: 3px;
        border-radius: 24px;
        background: conic-gradient(from 45deg, var(--gradient-1), var(--gradient-2), var(--gradient-3), var(--gradient-1));
        animation: hue-shift 8s linear infinite;
        width: 100%;
        margin: 20px 0;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.3);
    }

    @keyframes hue-shift {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }

    .biometric-card {
        background: var(--card-bg);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-radius: 21px;
        padding: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">M-AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">L\'interfaccia neurale, ridefinita.</p>', unsafe_allow_html=True)
st.markdown("---")

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("ERRORE: Inserisci la chiave GROQ_API_KEY nei Secrets.")
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image": st.image(message["content"])
        elif message["type"] == "video": st.html(message["content"])
        else: st.markdown(message["content"])

with st.sidebar:
    st.subheader("Sistema Biometrico")
    uploaded_file = st.file_uploader("Carica volto per estrazione matrice", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.info("Immagine caricata. In attesa di comando in chat.")

if prompt := st.chat_input("Analizza la foto o scrivi..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        
        if uploaded_file is not None and any(x in p for x in ["matrice", "cerca", "analizza", "identifica"]):
            with st.status("Elaborazione biometria...") as status:
                st.write("Estrazione punti focali...")
                time.sleep(1)
                st.write("Generazione matrice del volto (Face Embedding)...")
                matrice = generate_mock_matrix()
                time.sleep(1)
                st.write("Ricerca nel database sintetico...")
                time.sleep(1)
                status.update(label="Analisi completata!", state="complete")

            # Rendering della card in stile Premium M-BR0WS3R
            st.markdown(f"""
            <div class="biometric-card-container">
                <div class="biometric-card">
                    <h3 style='margin-top:0;'>Risultato Analisi Matrice</h3>
                    <p style='font-size:0.9rem; color:var(--text-secondary);'>I tratti somatici sono stati convertiti in coordinate spaziali allineate al database.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.code(f"Vector_Matrix: {str(matrice[:8])}...")
            
            base64_image = encode_image(uploaded_file)
            try:
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": f"Dato il seguente embedding vettoriale, identifica la persona nel database di test fornendo nome e profili social finti. Domanda utente: {prompt}"
                                },
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ]
                )
                risposta = response.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore: {e}")
        
        elif any(x in p for x in ["creato", "progettato", "manuel", "chi ti ha fatto"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Generazione..."):
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
                if not success: st.write("Server lento.")

        elif "video" in p:
            clean_p = prompt.replace(" ", "%20")
            video_html = f'<video width="100%" controls autoplay loop style="border-radius:20px;"><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
            st.html(video_html)
            st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        else:
            try:
                search = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3): search += f"\n- {r['body']}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente creato da Manuel Manera."},
                        {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore API: {e}")
