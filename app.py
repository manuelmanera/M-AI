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
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Chiedimi una foto, un video o un'info..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        risposta = ""
        
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write(risposta)
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
            st.write(risposta)
        
        # GENERAZIONE IMMAGINI (FORZATA)
        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            seed = random.randint(0, 99999)
            clean_prompt = prompt.replace(" ", "%20")
            risposta = f"Ecco l'immagine richiesta:\n\n![Immagine](https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&nologo=true)"
            st.markdown(risposta)
        
        # GENERAZIONE VIDEO
        elif "video" in p:
            clean_prompt = prompt.replace(" ", "%20")
            risposta = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_prompt}?model=video" type="video/mp4"></video>'
            st.html(risposta)

        # RICERCA WEB
        else:
            try:
                search_results = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3):
                        search_results += f"\n- {r['body']}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente aggiornato. Se non trovi info recenti, usa la tua conoscenza."},
                        {"role": "user", "content": f"Contesto web: {search_results}\n\nDomanda: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write(risposta)
            except Exception as e:
                risposta = f"Errore: {e}"
                st.write(risposta)
        
        st.session_state.messages.append({"role": "assistant", "content": risposta})
