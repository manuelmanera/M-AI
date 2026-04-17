import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    img {border-radius: 10px;}
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

# Funzione per l'effetto scrittura progressiva
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

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
        
        # 1. CASI SPECIALI (MANUEL / CHI CERCATE)
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

        # 2. GENERAZIONE IMMAGINI
        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            clean_prompt = prompt.replace(" ", "%20")
            img_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={random.randint(1,1000)}&nologo=true&t={ts}"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})

        # 3. GENERAZIONE VIDEO
        elif "video" in p:
            clean_prompt = prompt.replace(" ", "%20")
            video_html = f'<div style="text-align:center"><video width="100%" controls autoplay loop style="border-radius:10px;"><source src="https://pollinations.ai/p/{clean_prompt}?model=video&t={ts}" type="video/mp4"></video></div>'
            st.html(video_html)
            st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        # 4. RICERCA WEB E RISPOSTA AI
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
