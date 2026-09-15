# Ripresa operativa e decisioni

14 settembre 2026. Completati i quattro deliverable della revisione offline. Nessuna chiamata Gemini o altra API a consumo; nessun uso di chiavi, deploy o modifica alle campagne. Solo Astra, verificato nel registro di sessione. Il repository resta rimandato alla sessione concordata.

## Ordine proposto

1. Leggere objectives-matrix.md e delimitare il contributo: raccomandazione principale, RAG controllato con diagnosi del recupero; scoperta e notorietà simulata come moduli separati, non promesse implicite.
2. Scegliere effetto minimo rilevante e ambito di generalizzazione. Proposta da discutere: risultato condizionato al dominio vino e a pool/query definiti; nessuna pretesa su tutti gli agenti.
3. Implementare in cartella nuova i controlli a contesto fissato e la simulazione che rispetta la competizione. Mantenere la pipeline originale come baseline, senza riscrivere risultati passati. Validare prima di stabilire numerosità.
4. Preparare repository di contesto privato quando l'utente riprende tale attività; esportare soltanto cronologia visibile e materiali non sensibili. Non pubblicare automaticamente.
5. Sottoporre protocollo a revisione, completare confronto con letteratura primaria, registrare il piano; soltanto dopo autorizzare una nuova raccolta con budget esplicito.

## Decisioni dell'utente, senza bloccare la documentazione già completata

- Domanda principale: RAG controllato o scoperta web? La seconda richiede un modulo aggiuntivo.
- Effetto minimo utile: per esempio 1, 2 o 3 punti assoluti, con giustificazione sostanziale.
- Generalizzazione: pool/query fissi oppure nuove identità e formulazioni campionate?
- Budget e cadenza della futura raccolta, da stabilire dopo simulazione, non in base al solo credito disponibile.
- Collaborazione metodologica e destinazione editoriale, ancora da scegliere; nessun contatto esterno autorizzato.

## Stato verificato

480 risposte valide su 20 assegnazioni. D–A combinato +0,9375 punti; intervallo t esplorativo [-0,3896; +2,2646], non conclusivo. I controlli offline della revisione ricostruiscono i recuperi originali e verificano entrambi i sigilli. Il recupero C quasi nullo e il recupero D esclusivamente da llms.txt sono caratteristiche misurate della pipeline. Le ablation modificano l'indice globale e non sono una decomposizione causale né nuovi risultati LLM.

File: objectives-matrix.md, bm25-diagnosis.md, protocol-draft.md, next-steps.md; supporto eseguibile check_bm25.py e bm25-checks.json. Non rilanciare i runner live per riprodurre questa revisione.
