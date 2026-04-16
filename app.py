import streamlit as st
import google.generativeai as genai
import os

# Interfaccia pulita senza elementi grafici superflui
st.set_page_config(page_title="M-AI", layout="centered")

st.title("M-AI")
st.markdown("---")

# Recupero della chiave API dai Secrets del server
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Configurazione mancante: inserire la chiave API nei Secrets.")
    st.stop()

# Configurazione del modello Gemini 2.0 con ricerca web
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    tools=[{"google_search": {}}]
)

# Gestione della memoria della conversazione
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Area di input
if prompt := st.chat_input("Inserire il messaggio"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # L'IA cerca sul web se necessario grazie al tool google_search
            response = model.generate_content(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.write("Si e verificato un errore nella generazione della risposta.")