import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os
import random
import time
import requests # Nuova libreria per verificare i link

st.set_page_config(page_title="M-AI", layout="centered")

# Stile CSS per nascondere i loghi e arrotondare i media
st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    img {border-radius: 10px; max-width: 100%; height: auto;}
    div.stImage {text-align: center;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

# Recupero della chiave API Groq
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Configura GROQ_API_KEY nei Secrets di Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

# Inizializzazione della cronologia dei messaggi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Funzione per l'effetto scrittura progressiva del testo
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

# Funzione per verificare se un URL di un'immagine è valido
def is_valid_image(url):
    try:
        response = requests.head(url, timeout=5)
        # Verifica se il server risponde con successo (200) e se è un'immagine
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return True
        return False
    except:
        return False

# Visualizzazione dei messaggi precedenti dalla cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        elif message["type"] == "video":
            st.html(message["content"])
        else:
            st.markdown(message["content"])

# Gestione dell'input dell'utente
if prompt := st.chat_input("Scrivi qui..."):
    # Salva e mostra il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Genera la risposta dell'assistente
    with st.chat_message("assistant"):
        p = prompt.lower()
        ts = int(time.time()) # Timestamp unico
        
        # 1. RISPOSTE PERSONALIZZATE (MANUEL / CHI CERCATE)
        if any(x in p for x in ["creato", "progettato", "manuel"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            
        elif "chi cercate" in p:
            risposta = "Il tema è 'chi cercate'."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

        # 2. GENERAZIONE IMMAGINI (Con controllo di validità)
        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Sto creando la tua immagine..."):
                clean_prompt = prompt.replace(" ", "%20")
                # Genera un seed casuale per ogni richiesta
                seed = random.randint(1, 100000)
                img_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&nologo=true&t={ts}"
                
                # CONTROLLO CRUCIALE: Verifichiamo se l'immagine è stata generata
                if is_valid_image(img_url):
                    st.image(img_url)
                    st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                else:
                    # Alternativa (Fallback) se la generazione fallisce
                    risposta_errore = "Scusa, il server delle immagini è temporaneamente sovraccarico e non ha generato la foto. Riprova tra un momento con un prompt diverso."
                    st.write_stream(stream_data(risposta_errore))
                    st.session_state.messages.append({"role": "assistant", "content": risposta_errore, "type": "text"})

        # 3. GENERAZIONE VIDEO (Sperimentale)
        elif "video" in p:
            with st.spinner("Sto preparando il video..."):
                clean_prompt = prompt.replace(" ", "%20")
                # I video spesso non supportano il controllo Head, li mostriamo direttamente
                video_html = f'<div style="text-align:center"><video width="100%" controls autoplay loop style="border-radius:10px;"><source src="https://pollinations.ai/p/{clean_prompt}?model=video&t={ts}" type="video/mp4"></video></div>'
                st.html(video_html)
                # Aggiungiamo un testo descrittivo per la cronologia
                st.session_state.messages.append({"role": "assistant", "content": f"Video generato per: {prompt}", "type": "text"})
                st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        # 4. RICERCA WEB E RISPOSTA TESTUALE AI (Con effetto streaming)
        else:
            try:
                # Ricerca veloce su DuckDuckGo
                search_results = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3):
                        search_results += f"\n- {r['body']}"
                
                # Generazione risposta testuale con Groq (Llama 3)
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente aggiornato con accesso al web."},
                        {"role": "user", "content": f"Contesto web attuale: {search_results}\n\nDomanda dell'utente: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                # Mostra la risposta con l'effetto scrittura
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                # Gestione errori di ricerca/generazione testo
                st.error(f"Si è verificato un errore nella ricerca o nella generazione del testo: {e}")

