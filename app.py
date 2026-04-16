import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="M-AI", layout="centered")

# CSS per interfaccia pulita e senza icone
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

# Recupero chiave
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.warning("Inserisci la chiave nei Secrets di Streamlit.")
    st.stop()

# Configurazione flessibile
try:
    genai.configure(api_key=api_key)
    # Usiamo il nome del modello più semplice possibile
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Errore configurazione: {e}")

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
        
        # Risposte personalizzate Manuel Manera
        if any(x in p for x in ["chi ti ha progettata", "chi ti ha creato", "creatore", "manuel manera"]):
            risposta = "Sono stata progettata da Manuel Manera."
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
        else:
            try:
                # Tentativo di generazione universale
                response = model.generate_content(prompt)
                # Verifichiamo se la risposta ha del testo
                if hasattr(response, 'text'):
                    risposta = response.text
                else:
                    # Se il modello restituisce blocchi diversi (es. per sicurezza)
                    risposta = response.candidates[0].content.parts[0].text
            except Exception as e:
                risposta = f"Errore di connessione a Google. Dettaglio: {str(e)}"
        
        st.write(risposta)
        st.session_state.messages.append({"role": "assistant", "content": risposta})
