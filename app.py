import streamlit as st
import numpy as np
from PIL import Image
import os
import pickle
import insightface
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="FaceMatrix", layout="wide")

st.title("🧬 FaceMatrix")
st.markdown("**Software locale per estrazione matrice volto + ricerca nel tuo database**")

# ====================== INIZIALIZZAZIONE ======================
if "face_app" not in st.session_state:
    with st.spinner("Caricamento modello InsightFace..."):
        st.session_state.face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        st.session_state.face_app.prepare(ctx_id=0, det_size=(640, 640))

if "database" not in st.session_state:
    st.session_state.database = []

DB_FOLDER = "database_volti"
os.makedirs(DB_FOLDER, exist_ok=True)

# Carica database se esiste
if os.path.exists("database.pkl"):
    with open("database.pkl", "rb") as f:
        st.session_state.database = pickle.load(f)

# ====================== SIDEBAR ======================
st.sidebar.header("Menu")
pagina = st.sidebar.radio("Scegli funzione", ["📸 Aggiungi al Database", "🔍 Riconosci Volto", "📊 Visualizza Database"])

# ====================== ESTRAZIONE EMBEDDING ======================
def get_embedding(image):
    img = np.array(image)
    faces = st.session_state.face_app.get(img)
    if len(faces) == 0:
        return None
    face = max(faces, key=lambda x: x.det_score)
    return face.embedding

# ====================== PAGINA 1: AGGIUNGI AL DATABASE ======================
if pagina == "📸 Aggiungi al Database":
    st.header("Aggiungi una persona al database")
    nome = st.text_input("Nome e Cognome")
    uploaded = st.file_uploader("Carica foto del volto", type=["jpg", "jpeg", "png"])

    if uploaded and nome:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, use_column_width=True)

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
                
                with open("database.pkl", "wb") as f:
                    pickle.dump(st.session_state.database, f)
                
                st.success(f"✅ {nome} aggiunto correttamente!")
                st.rerun()

# ====================== PAGINA 2: RICONOSCI VOLTO ======================
elif pagina == "🔍 Riconosci Volto":
    st.header("Riconoscimento volto")
    uploaded = st.file_uploader("Carica la foto da analizzare", type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, use_column_width=True)

        if st.button("🔍 Analizza e confronta"):
            with st.spinner("Analisi in corso..."):
                embedding_query = get_embedding(image)
                
                if embedding_query is None:
                    st.error("❌ Nessun volto rilevato")
                else:
                    if len(st.session_state.database) == 0:
                        st.warning("Il database è vuoto!")
                    else:
                        results = []
                        for entry in st.session_state.database:
                            sim = cosine_similarity([embedding_query], [entry["embedding"]])[0][0] * 100
                            results.append((entry["name"], sim))
                        
                        results.sort(key=lambda x: x[1], reverse=True)
                        
                        st.subheader("Risultati")
                        for name, score in results[:10]:
                            emoji = "🟢" if score > 70 else "🟡" if score > 50 else "🔴"
                            st.write(f"{emoji} **{name}** → **{score:.2f}%** somiglianza")

# ====================== PAGINA 3: VISUALIZZA DATABASE ======================
elif pagina == "📊 Visualizza Database":
    st.header(f"Database: {len(st.session_state.database)} volti")
    
    if st.session_state.database:
        for i, entry in enumerate(st.session_state.database):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{entry['name']}**")
            with col2:
                if st.button("Elimina", key=f"del_{i}"):
                    os.remove(os.path.join(DB_FOLDER, entry['filename']))
                    st.session_state.database.pop(i)
                    with open("database.pkl", "wb") as f:
                        pickle.dump(st.session_state.database, f)
                    st.rerun()
    else:
        st.info("Il database è ancora vuoto.")

st.caption("FaceMatrix v1.0 - Tutto eseguito in locale")
