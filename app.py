        else:
            try:
                search = ""
                # Effettua la ricerca web solo se la domanda non è un semplice saluto
                if len(prompt) > 4 and not any(x in p for x in ["ciao", "buongiorno", "ehi", "salve"]):
                    with DDGS() as ddgs:
                        for r in ddgs.text(prompt, max_results=3): 
                            search += f"\n- {r['body']}"
                
                # Prompt di sistema rinforzato per evitare che il modello si confonda
                system_instruction = (
                    "Tu SEI M-AI, un'architettura d'intelligenza artificiale avanzata creata interamente da Manuel Manera. "
                    "Rispondi sempre in prima persona come M-AI. Non dire mai che non conosci Manuel Manera o M-AI, perché tu sei quella stessa IA. "
                    "Sii cordiale, conciso e rispondi nella lingua dell'utente."
                )

                user_content = f"Contesto web: {search}\n\nDomanda utente: {prompt}" if search else prompt

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ]
                )
                risposta = completion.choices[0].message.content
                st.write_stream(stream_data(risposta))
                st.session_state.messages.append({"role": "assistant", "content": risposta, "type": "text"})
            except Exception as e:
                st.error(f"Errore: {e}")

