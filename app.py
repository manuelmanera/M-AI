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

# Utilizzo di Gemini 2.0 Flash (il modello più avanzato e compatibile attualmente)
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    tools=[{"google_search": {}}]
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
            
            # Estrazione universale del testo
            answer = ""
            if hasattr(response, 'text'):
                answer = response.text
            elif response.candidates:
                parts = response.candidates[0].content.parts
                answer = "".join([p.text for p in parts if hasattr(p, 'text')])
            
            if answer:
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.write("Generazione completata senza output testuale.")
                
        except Exception as e:
            st.error(f"Dettaglio tecnico: {str(e)}")
