import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none;
    }
    .stChatMessage {
        background-color: transparent !important;
        border-bottom: 1px solid #f0f0f0;
        border-radius: 0px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.stop()

genai.configure(api_key=api_key)

# Configurazione completa con Google Search attiva
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[{"google_search_retrieval": {}}]
)

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
            response = model.generate_content(prompt)
            
            # Gestione avanzata della risposta per modelli con tools attivi
            if response.candidates and response.candidates[0].content.parts:
                answer = response.candidates[0].content.parts[0].text
                if answer:
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.write("Ricerca completata, ma nessun testo generato.")
            else:
                st.write("L'IA non ha prodotto una risposta testuale.")
                
        except Exception as e:
            st.error(f"Errore: {str(e)}")
