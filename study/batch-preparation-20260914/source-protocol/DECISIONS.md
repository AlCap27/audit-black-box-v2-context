# Decisioni da approvare prima di procedere

14 settembre 2026. Già adottati per istruzione utente: ambito intermedio, tre stadi distinti, estimandi retrieval/condizionato/totale, Δ principale 5 pp e scenari 2/10, pilot separato, nessuna nuova API, campagne sigillate immutate. Non richiedono riconferma.

1. **Fattoriale 2×2×2 proposto.** Approvare JSON-LD, llms e duplicazione del body come tre fattori, otto celle da quattro vendor. Il terzo fattore misura ridondanza, non qualità semantica del contenuto. Alternativa più stretta: 2×2 senza T, con claim ridotto.
2. **Primaria e molteplicità.** Approvare effetto principale L sulla raccomandazione totale, bilaterale α=0,025; otto secondarie a α=0,003125 ciascuna. Cambiare primaria richiede riallineare piano e budget prima di osservare nuovi esiti.
3. **Livello di garanzia e budget.** Proposta robusta: 318 assegnazioni e 7656 API totali, con potenza ≥80% sotto le assunzioni specificate a Δ5. Alternativa efficiente da 984 API non ha garanzia equivalente ed esige validazione aggiuntiva del modello statistico. Nessun budget è autorizzato da questo documento.
4. **Esito condizionato.** Accettare che resti secondario con possibile scarsa precisione, oppure richiedere potenza dedicata (proxy 9120–36096 chiamate inferenziali per 5 pp; nessuna garanzia senza supporto). Se interessa l'effetto causale a valle, approvare un modulo distinto a esposizione controllata, da dimensionare.
5. **Retrieval ampliato offline.** Approvare 1135 assegnazioni totali per retrieval, condividendo le prime 318 con la generazione. Non consuma API; è comunque parte del piano da congelare.
6. **Dominio e generalizzazione.** Proposta: 32 identità e 24 query fisse del dominio vino, nuovo disegno di assegnazione. Per estendere a query/vendor nuovi serve un ulteriore livello di campionamento e una nuova valutazione di potenza.
7. **Generatore e periodo.** Confermare identificatore/parametri disponibili per la futura raccolta e calendario compatibile con quota e deriva. Nessun fallback automatico. Il vincolo sul lavoro dell'assistente resta solo Astra.
8. **Controlli e regole operative.** Approvare i 24 controlli generativi separati, nessun retry automatico, checkpoint al primo errore e analisi dei missing senza eliminazione selettiva. Approvare eventuale ripresa dopo un guasto sulla base dello stato documentato.
9. **Preregistrazione e pubblicazione.** Scegliere sede della registrazione e revisione metodologica; autorizzare esplicitamente eventuale pubblicazione/contatto esterno. Repository di contesto resta alla sessione concordata, nessuna creazione eseguita.

Nessuna proposta di ridurre Δ5: i dati mostrano che è grande rispetto alla baseline e che è costoso per l'esito condizionato, ma non ne dimostrano l'impossibilità per l'effetto totale. Eventuali alternative devono essere deliberate per ragioni sostanziali o di budget, non per favorire risultati già visti.

I quattro deliverable richiesti sono PROTOCOL.md, power-sensitivity.md (con power-results.json e script), DESIGN.md e questo elenco. La lavorazione si ferma qui, prima di implementare o lanciare una nuova campagna.
