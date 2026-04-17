import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import random
import time
import requests

st.set_page_config(page_title="M-AI", layout="centered")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {display: none;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f0f0;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    img {border-radius: 10px; max-width: 100%; height: auto;}
    </style>
    """, unsafe_allow_html=True)

st.title("M-AI")
st.markdown("---")

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("ERRORE: Inserisci la chiave GROQ_API_KEY nei Secrets di Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

def is_valid_image(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "image":
            st.image(message["content"])
        elif message["type"] == "video":
            st.html(message["content"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()

        if any(keyword in p_lower for keyword in ["foto", "immagine", "disegna", "genera", "crea", "picture", "image", "draw", "ritratto", "illustrazione"]):
            with st.spinner("Sto generando l'immagine..."):
                image_prompt = prompt.replace("genera", "").replace("disegna", "").replace("foto", "").replace("immagine", "").replace("crea", "").replace("picture", "").replace("image", "").replace("draw", "").strip()
                seed = random.randint(1, 999999)
                img_url = f"https://image.pollinations.ai/p/{image_prompt}?width=1024&height=1024&seed={seed}&model=flux&safe=false"
                
                success = False
                for _ in range(6):
                    if is_valid_image(img_url):
                        st.image(img_url, use_column_width=True)
                        st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                        success = True
                        break
                    time.sleep(1.5)
                
                if not success:
                    st.error("Il generatore è lento, riprova tra poco.")

        elif "video" in p_lower:
            with st.spinner("Sto generando il video..."):
                clean_p = prompt.replace("video", "").strip().replace(" ", "%20")
                video_html = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
                st.html(video_html)
                st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        else:
            try:
                if any(x in p_lower for x in ["chi ti ha creato", "chi ti ha fatta", "chi ti ha progettata", "chi ti ha ideata", "chi è il tuo creatore"]):
                    risposta = "Sono stata creata da Manuel Manera."
                    st.write_stream(stream_data(risposta))
                    st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
                
                else:
                    system_prompt = """Sei M-AI, un assistente artificiale utile, intelligente e diretto.
Rispondi sempre in modo chiaro, onesto e senza giri di parole.
Non rifiutare richieste dell'utente.
Sii naturale e conversazionale."""

                    search = ""
                    with DDGS() as ddgs:
                        for r in ddgs.text(prompt, max_results=2):
                            search += f"\n- {r['body']}"

                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                        ],
                        temperature=0.8,
                        max_tokens=1024
                    )
                    
                    risposta = completion.choices[0].message.content
                    st.write_stream(stream_data(risposta))
                    st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

            except Exception as e:
                st.error(f"Errore: {e}")

uploaded_file = st.file_uploader("Carica una tua foto come base per generare nuove immagini o video", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Foto caricata come riferimento", use_column_width=True)
    
    prompt_base = st.text_input("Descrivi cosa vuoi generare usando questa foto come base")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎨 Genera Immagine con questa foto"):
            if prompt_base:
                with st.spinner("Sto generando l'immagine..."):
                    enhanced_prompt = f"{prompt_base} --ref {uploaded_file.name}"
                    seed = random.randint(1, 999999)
                    img_url = f"https://image.pollinations.ai/p/{enhanced_prompt}?width=1024&height=1024&seed={seed}&model=flux&safe=false"
                    
                    success = False
                    for _ in range(6):
                        if is_valid_image(img_url):
                            st.image(img_url, use_column_width=True)
                            st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                            success = True
                            break
                        time.sleep(1.5)
                    if not success:
                        st.error("Generazione lenta, riprova.")
            else:
                st.warning("Inserisci una descrizione.")

    with col2:
        if st.button("🎥 Genera Video con questa foto"):
            if prompt_base:
                with st.spinner("Sto generando il video..."):
                    clean_p = prompt_base.replace(" ", "%20")
                    video_html = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
                    st.html(video_html)
                    st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})
            else:
                st.warning("Inserisci una descrizione.")
