import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time
import requests

st.set_page_config(page_title="M-AI", layout="centered")

# CSS personalizzato per integrare il caricamento e pulire l'interfaccia
st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    img {border-radius: 10px; max-width: 100%; height: auto;}
    
    /* Stile per compattare il caricatore file */
    .stFileUploader section {padding: 0; min-height: 0;}
    .stFileUploader label {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

# --- LOGICA API ---
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

# Visualizzazione Cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        elif message["type"] == "video":
            st.html(message["content"])
        else:
            st.markdown(message["content"])

# --- INPUT AREA (IL "PULSANTE INCORPORATO") ---
# Creiamo una colonna stretta per l'upload e una larga per il testo
input_col, upload_col = st.columns([0.85, 0.15])

with upload_col:
    # Il caricatore file appare come un piccolo tasto "+" grazie al CSS
    uploaded_file = st.file_uploader("📎", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

with input_col:
    prompt = st.chat_input("Scrivi qui o genera qualcosa...")

# --- LOGICA DI ELABORAZIONE ---
if prompt:
    # Se c'è un file caricato, lo aggiungiamo al contesto della generazione
    if uploaded_file:
        full_prompt = f"{prompt} (riferimento: {uploaded_file.name})"
    else:
        full_prompt = prompt

    st.session_state.messages.append({"role": "user", "content": full_prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(full_prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()

        # Caso Immagini/Video
        if any(keyword in p_lower for keyword in ["foto", "immagine", "disegna", "genera", "video"]):
            with st.spinner("Creazione in corso..."):
                if "video" in p_lower:
                    clean_p = prompt.replace("video", "").strip().replace(" ", "%20")
                    content_html = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
                    st.html(content_html)
                    st.session_state.messages.append({"role": "assistant", "content": content_html, "type": "video"})
                else:
                    image_prompt = p_lower.replace("genera", "").replace("foto", "").strip()
                    # Se c'è un file, pollinations può usare il nome come seed/riferimento testuale
                    seed = random.randint(1, 999999)
                    img_url = f"https://image.pollinations.ai/p/{image_prompt}?width=1024&height=1024&seed={seed}&model=flux"
                    
                    if is_valid_image(img_url):
                        st.image(img_url, use_column_width=True)
                        st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})

        # Caso Testo (Chat standard)
        else:
            try:
                search = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=2):
                        search += f"\n- {r['body']}"

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei M-AI, assistente creato da Manuel Manera. Sii diretto."},
                        {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                    ],
                    temperature=0.8
                )
                
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

            except Exception as e:
                st.error(f"Errore: {e}")

# Anteprima file caricato (opzionale, sotto la barra)
if uploaded_file:
    st.toast(f"File pronto: {uploaded_file.name}")
