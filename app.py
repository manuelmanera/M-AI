import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "![Immagine]" in message["content"]:
            st.markdown(message["content"])
        elif "<video" in message["content"]:
            st.html(message["content"])
        else:
            st.write(message["content"])

if prompt := st.chat_input("Chiedimi una foto, un video o un'info..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        
        # LOGICA PERSONALIZZATA MANUEL
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
        
        # GENERAZIONE IMMAGINI
        elif any(x in p for x in ["genera foto", "fai una foto", "disegna", "immagine di"]):
            seed = random.randint(0, 99999)
            prompt_img = prompt.replace(" ", "%20")
            risposta = f"Ecco l'immagine che hai chiesto:\n\n![Immagine](https://pollinations.ai/p/{prompt_img}?width=1024&height=1024&seed={seed}&nologo=true)"
            st.markdown(risposta)
        
        # GENERAZIONE VIDEO (ANIMAZIONI)
        elif any(x in p for x in ["genera video", "fai un video", "video di"]):
            prompt_vid = prompt.replace(" ", "%20")
            risposta = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{prompt_vid}?model=video" type="video/mp4"></video>'
            st.html(risposta)

        # RICERCA WEB E TESTO
        else:
            try:
                search_results = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3):
                        search_results += f"\n- {r['body']}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"Sei un assistente aggiornato. Usa queste info se utili: {search_results}"},
                        {"role": "user", "content": prompt}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write(risposta)
            except Exception as e:
                risposta = f"Errore: {e}"
                st.write(risposta)
        
        st.session_state.messages.append({"role": "assistant", "content": risposta})
