import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="M-AI", layout="centered")

st.title("M-AI")
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Configurazione mancante.")
    st.stop()

genai.configure(api_key=api_key)

# Inizializziamo il modello senza strumenti complessi per ora, per testare la connessione
model = genai.GenerativeModel('gemini-1.5-flash')

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
        try:
            # Generazione semplice per testare se la chiave funziona
            response = model.generate_content(prompt)
            testo_risposta = response.text
            st.write(testo_risposta)
            st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
        except Exception as e:
            st.error(f"Errore tecnico: {str(e)}")
