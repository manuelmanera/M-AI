import streamlit as st
from Groq import Groq
import os

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0; border-radius: 0px;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Manca la chiave GROQ_API_KEY nei Secrets.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Inserire il messaggio"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        p = prompt.lower()
        if any(x in p for x in ["chi ti ha progettata", "chi ti ha creato", "creatore", "manuel manera"]):
            risposta = "Sono stata progettata da Manuel Manera."
        else:
            try:
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                )
                risposta = completion.choices[0].message.content
            except Exception as e:
                risposta = f"Errore: {str(e)}"
        
        st.write(risposta)
        st.session_state.messages.append({"role": "assistant", "content": risposta})
