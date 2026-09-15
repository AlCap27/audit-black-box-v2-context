# Verifica preliminare della novità — 14 settembre2026

Ricerca mirata, non revisione sistematica esaustiva. Query: GEO Generative Engine
Optimization; llms.txt retrieval; structured data generative optimization.
Sono stati letti abstract e testo del precedente più vicino; nessuna conclusione
di priorità assoluta deriva dall'assenza di altri risultati nella ricerca.

**Aggarwal et al., GEO: Generative Engine Optimization, arXiv2311.09735.**
Studia l'ottimizzazione della visibilità dei contenuti nelle risposte di motori
generativi, con benchmark e interventi sul contenuto. Il tema generale è quindi
già consolidato; il nostro studio non introduce per primo GEO o la possibilità
di influenzare la visibilità. [Paper](https://arxiv.org/abs/2311.09735).

**Volpini et al., Structured Linked Data as a Memory Layer for Agent-Orchestrated
Retrieval, arXiv2603.10700v1.** Precedente direttamente rilevante: confronta HTML,
JSON-LD e pagine arricchite in retrieval standard e agentico, includendo istruzioni
in stile llms.txt. Usa158entità e349query in quattro domini, con Vertex Vector
Search e ADK. Misura soprattutto accuratezza e completezza delle risposte.
I bundle arricchiti includono più interventi; non sono equivalenti al nostro
fattoriale isolato né all'esito binario vendor raccomandato. La discussione
riconosce sensibilità all'ingestione e troncamento dello structured data.
Non importiamo i suoi effect size per dimensionare il nostro studio.
[Testo primario](https://arxiv.org/html/2603.10700v1).

Il contributo difendibile proposto è: randomizzazione bilanciata S×L×T a fatti
costanti; tracce esatte discovery/retrieval/esposizione/recommendation; inferenza
predefinita sull'assegnazione del pool competitivo; gestione di missing e versioni;
rilascio riproducibile anche di esiti nulli/contrari. Questo è un posizionamento
metodologico, non prova che nessun altro abbia già fatto la stessa cosa.

Prima della sottomissione: aggiornare ricerca bibliografica e citazioni avanti/
indietro dei due lavori, verificare versioni e revisione paritaria, confrontare
benchmark e codice pubblicato. Evitare claim sul riconoscimento universale di
llms.txt: qui il file è intenzionalmente ingerito dalla pipeline locale.
Una futura generalizzazione richiederebbe altri retriever, query/vendor campionati
e generatori; non aggiungerli a posteriori per ottenere un risultato favorevole.
