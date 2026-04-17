import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

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

api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Configura GROQ_API_KEY nei Secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Chiedimi qualsiasi cosa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
        else:
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(prompt, max_results=3)]
                
                context = "\n".join([f"- {res['body']}" for res in results])
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"Sei un assistente aggiornato. Usa queste info se utili: {context}"},
                        {"role": "user", "content": prompt}
                    ]
                )
                risposta = completion.choices[0].message.content
            except Exception as e:
                risposta = f"Errore ricerca: {e}"
        
        st.write(risposta)
        st.session_state.messages.append({"role": "assistant", "content": risposta})
