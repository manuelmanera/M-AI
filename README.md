# M-AI ricostruito

Interfaccia web ispirata agli screenshot: barra laterale grigia, area chat scura, bolle arrotondate e compositore in basso.

## 1. Prima configurazione Firebase

1. In Firebase Console apri il progetto `m-ai-b9933`.
2. **Authentication → Sign-in method**: abilita Google ed Email/Password.
3. **Realtime Database**: crea il database se non esiste.
4. Copia l'URL esatto del database (Firebase Console → Realtime Database) e sostituisci `INSERISCI_QUI_L_URL_DEL_REALTIME_DATABASE` in `index.html`.
5. In Realtime Database → Rules, incolla `database.rules.json` e pubblica le regole.

La configurazione web Firebase contiene identificatori pubblici del progetto, non una chiave privata. Non mettere mai la chiave Groq nel browser.

## 2. Avviare il server

Richiede Python 3.10+.

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GROQ_API_KEY="LA_TUA_CHIAVE_GROQ"
python app.py
```
Apri `http://127.0.0.1:5000`.

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY="LA_TUA_CHIAVE_GROQ"
python app.py
```

## 3. Cosa salva

- Profilo e chat normali: `users/{uid}/profile` e `users/{uid}/chats`.
- Chat privata: resta solo nella memoria della scheda e non viene inviata al Realtime Database. Se ricarichi la pagina o chiudi la scheda, viene persa.
- La chat privata usa comunque il servizio AI via server: non viene salvata nel database, ma il messaggio viene trasmesso al provider AI per generare la risposta.

## 4. Sicurezza e limiti importanti

Le regole permettono a un utente autenticato di leggere/scrivere soltanto sotto il proprio UID. Le regole non possono verificare che una chat privata non venga salvata: questa garanzia è implementata nell'interfaccia. Per un sistema pubblico/produzione aggiungi App Check, limitazione richieste, gestione quote, policy privacy e controlli lato server.

La configurazione iniziale non abilita automaticamente l'autenticazione a più fattori con app Authenticator/TOTP: Google sign-in ed Email/Password sono metodi di accesso, mentre MFA va configurata separatamente nel progetto Firebase e richiede un flusso dedicato. Non promettere MFA finché non viene implementata e testata.
