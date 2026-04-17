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
    div.stImage {text-align: center;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

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
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return True
        return False
    except:
        return False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        elif message["type"] == "video":
            st.html(message["content"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        ts = int(time.time())
        
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            

        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Generazione immagine in corso..."):
                clean_prompt = prompt.replace(" ", "%20")
                seed = random.randint(1, 100000)
                img_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&nologo=true&t={ts}"
                
                successo = False
                for _ in range(5):
                    if is_valid_image(img_url):
                        st.image(img_url)
                        st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                        successo = True
                        break
                    time.sleep(2)
                
                if not successo:
                    risposta = "Il server è sovraccarico. Riprova tra un istante."
                    st.write_stream(stream_data(risposta))
                    st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

        elif "video" in p:
            with st.spinner("Preparazione video..."):
                clean_prompt = prompt.replace(" ", "%20")
                video_html = f'<div style="text-align:center"><video width="100%" controls autoplay loop style="border-radius:10px;"><source src="https://pollinations.ai/p/{clean_prompt}?model=video&t={ts}" type="video/mp4"></video></div>'
                st.html(video_html)
                st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        else:
            try:
                search_results = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3):
                        search_results += f"\n- {r['body']}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente aggiornato con accesso al web."},
                        {"role": "user", "content": f"Contesto web: {search_results}\n\nDomanda: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore: {e}")
