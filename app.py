import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time
import requests

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    img {border-radius: 10px; max-width: 100%; height: auto;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

# Recupero chiave corretta
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("ERRORE: Inserisci la chiave GROQ_API_KEY nei Secrets di Streamlit.")
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image": st.image(message["content"])
        elif message["type"] == "video": st.html(message["content"])
        else: st.markdown(message["content"])

if prompt := st.chat_input("Chiedimi una foto o un'info..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        
        if any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Sto dipingendo..."):
                clean_p = prompt.replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/p/{clean_p}?width=1024&height=1024&seed={random.randint(1,99999)}&model=flux"
                
                success = False
                for _ in range(5):
                    if is_valid_image(img_url):
                        st.image(img_url)
                        st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                        success = True
                        break
                    time.sleep(2)
                
                if not success:
                    st.write("Il server immagini è lento, riprova tra un attimo.")

        elif "video" in p:
            clean_p = prompt.replace(" ", "%20")
            video_html = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
            st.html(video_html)
            st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        else:
            try:
                search = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3): search += f"\n- {r['body']}"
                
                # MODELLO AGGIORNATO QUI
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente web."},
                        {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore API: {e}")
