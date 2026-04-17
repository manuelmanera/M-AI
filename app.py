import streamlit as st
import numpy as np
from PIL import Image
import os
import json
import insightface
from insightface.app import FaceAnalysis
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import cv2

st.set_page_config(page_title="FaceMatrix - Riconoscimento Volti Locale", layout="wide")
st.title("🧬 FaceMatrix")
st.markdown("**Software locale per estrazione matrice volto + ricerca nel tuo database**")

# ====================== INIZIALIZZAZIONE ======================
if "face_app" not in st.session_state:
    with st.spinner("Caricamento modello InsightFace (prima volta può richiedere 10-20 secondi)..."):
        st.session_state.face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        st.session_state.face_app.prepare(ctx_id=0, det_size=(640, 640))

if "database" not in st.session_state:
    st.session_state.database = []  # lista di dict: {"name": , "embedding": , "filename": }

DB_FOLDER = "database_volti"
os.makedirs(DB_FOLDER, exist_ok=True)

# Carica database esistente
if os.path.exists("database.pkl"):
    with open("database.pkl", "rb") as f:
        st.session_state.database = pickle.load(f)

# ====================== SIDEBAR ======================
st.sidebar.header("Menu")
pagina = st.sidebar.radio("Scegli funzione", ["📸 Aggiungi al Database", "🔍 Riconosci Volto", "📊 Visualizza Database"])

# ====================== FUNZIONE ESTRAZIONE EMBEDDING ======================
def get_embedding(image):
    img = np.array(image)
    faces = st.session_state.face_app.get(img)
    if len(faces) == 0:
        return None
    # Prendiamo il volto con la confidenza più alta
    face = max(faces, key=lambda x: x.det_score)
    return face.embedding  # vettore 512 dimensioni

# ====================== PAGINA 1: AGGIUNGI AL DATABASE ======================
if pagina == "📸 Aggiungi al Database":
    st.header("Aggiungi una persona al database")
    nome = st.text_input("Nome e Cognome")
    uploaded = st.file_uploader("Carica foto del volto (fronte, buona luce)", type=["jpg", "jpeg", "png"])

    if uploaded and nome:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Foto caricata", use_column_width=True)

        if st.button("💾 Salva nel Database"):
            embedding = get_embedding(image)
            if embedding is None:
                st.error("❌ Nessun volto rilevato nella foto")
            else:
                filename = f"{nome.replace(' ', '_')}_{len(st.session_state.database)}.npy"
                np.save(os.path.join(DB_FOLDER, filename), embedding)
                
                st.session_state.database.append({
                    "name": nome,
                    "embedding": embedding,
                    "filename": filename
                })
                
                # Salva database
                with open("database.pkl", "wb") as f:
                    pickle.dump(st.session_state.database, f)
                
                st.success(f"✅ {nome} aggiunto al database!")
                st.rerun()

# ====================== PAGINA 2: RICONOSCI VOLTO ======================
elif pagina == "🔍 Riconosci Volto":
    st.header("Riconoscimento volto")
    uploaded = st.file_uploader("Carica la foto da analizzare", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Foto da analizzare", use_column_width=True)

        if st.button("🔍 Analizza e confronta con il database"):
            with st.spinner("Estrazione matrice volto e confronto..."):
                embedding_query = get_embedding(image)
                
                if embedding_query is None:
                    st.error("❌ Nessun volto rilevato")
                else:
                    st.success("✅ Volto rilevato - Matrice 512 dimensioni generata")
                    
                    # Mostra estratto matrice
                    st.write("**Estratto della matrice (primi 20 valori)**")
                    st.code(embedding_query[:20])

                    if len(st.session_state.database) == 0:
                        st.warning("Il database è vuoto. Aggiungi prima delle foto!")
                    else:
                        similarities = []
                        for entry in st.session_state.database:
                            sim = cosine_similarity([embedding_query], [entry["embedding"]])[0][0]
                            similarities.append((entry["name"], sim * 100))
                        
                        # Ordina per somiglianza
                        similarities.sort(key=lambda x: x[1], reverse=True)
                        
                        st.subheader("Risultati di corrispondenza")
                        for name, score in similarities[:10]:
                            color = "🟢" if score > 70 else "🟡" if score > 50 else "🔴"
                            st.write(f"{color} **{name}** → **{score:.2f}%** di somiglianza")

# ====================== PAGINA 3: VISUALIZZA DATABASE ======================
elif pagina == "📊 Visualizza Database":
    st.header(f"Database attuale: {len(st.session_state.database)} volti")
    
    if st.session_state.database:
        for i, entry in enumerate(st.session_state.database):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{entry['name']}**")
            with col2:
                if st.button("Elimina", key=i):
                    # Elimina file e dal database
                    os.remove(os.path.join(DB_FOLDER, entry['filename']))
                    st.session_state.database.pop(i)
                    with open("database.pkl", "wb") as f:
                        pickle.dump(st.session_state.database, f)
                    st.rerun()
    else:
        st.info("Database vuoto. Aggiungi volti dalla prima pagina.")

st.caption("FaceMatrix v1.0 - Tutto in locale • Progetto scolastico Cybersecurity")                                    "text": f"Dato il seguente embedding vettoriale, identifica la persona nel database di test fornendo nome e profili social finti. Domanda utente: {prompt}"
                                },
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ]
                )
                risposta = response.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore: {e}")
        
        elif any(x in p for x in ["creato", "progettato", "manuel", "chi ti ha fatto"]):
            risposta = "Sono stata progettata da Manuel Manera."
            st.write_stream(stream_data(risposta))
            st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})

        elif any(x in p for x in ["foto", "immagine", "disegna", "genera"]):
            with st.spinner("Generazione..."):
                clean_p = prompt.replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/p/{clean_p}?width=1024&height=1024&seed={random.randint(1,99999)}&model=flux"
                success = False
                for _ in range(3):
                    if is_valid_image(img_url):
                        st.image(img_url)
                        st.session_state.messages.append({"role": "assistant", "content": img_url, "type": "image"})
                        success = True
                        break
                    time.sleep(2)
                if not success: st.write("Server lento.")

        elif "video" in p:
            clean_p = prompt.replace(" ", "%20")
            video_html = f'<video width="100%" controls autoplay loop><source src="https://pollinations.ai/p/{clean_p}?model=video" type="video/mp4"></video>'
            st.html(video_html)
            st.session_state.messages.append({"role": "assistant", "content": video_html, "type": "video"})

        else:
            try:
                search = ""
                with DDGS() as ddgs:
                    for r in ddgs.text(prompt, max_results=3): search += f"\n- {r['body']}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "Sei un assistente creato da Manuel Manera."},
                        {"role": "user", "content": f"Contesto: {search}\n\nDomanda: {prompt}"}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore API: {e}")
