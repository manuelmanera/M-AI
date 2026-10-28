# M-AI multipagina
Pagine separate: `index.html` (accesso), `chat.html` (chat), `profile.html` (profilo); logica in `assets/`.

1. Abilita Google ed Email/Password in Firebase Authentication.
2. Crea Realtime Database e inserisci l'URL esatto in `assets/firebase.js` al posto di `INSERISCI_QUI_L_URL_DEL_REALTIME_DATABASE`.
3. Pubblica `database.rules.json` nelle Rules del database.
4. Avvio locale: `pip install -r requirements.txt`, imposta `GROQ_API_KEY` come variabile d'ambiente e `python app.py`.

Il CNAME `m-ai.meowgo.it` non esegue Python. Usa un hosting backend come Render, imposta lì `GROQ_API_KEY` e configura il dominio secondo i record DNS richiesti dal provider. GitHub Pages da solo non esegue Flask e l'endpoint `/api/chat`. Non mettere la chiave Groq nel repository. La chat privata non è salvata su Firebase, ma i messaggi sono inviati a Groq per generare risposte.
