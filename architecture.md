# Architettura

Fixture canoniche vendor×cella → assegnazione bloccata per template → discovery
locale dal manifest → estrazione body/JSON-LD/llms → chunk100parole → BM25
k1=1.2,b=.75 → top5,max1/vendor → contesto700parole → Gemini Batch → rawJSONL
immutabile → riconciliazione perkey → parsingrecommend/abstain → analisi percluster.

Schema concatenato al body; llms documento separato. T duplica soltanto il body.
Tracce indicano sia retrieval Z sia fonti effettivamente mostrate X. Y totale è
stimato su tutti i vendor assegnati; Y|Z è contrasto condizionato descrittivo,
non effetto diretto causale del generatore. Benchmark discovery separati senzaLLM.

13fileJSONL:24controlli e12main da734richieste. Ogni main comprende due query per
tutte367assegnazioni. Nessun ordine di esecuzione Google garantito. Nessun tool
GoogleSearch, URLcontext o accesso ai siti necessario; URL sintetiche.invalid.

Budget: ledger atomico prima dell'invio; tentativi incerti trattengono riserva;
nessuna risottomissione automatica. Importazione gestisce ordine, missing, duplicati,
errori, versioni. Cancel non equivale ad arresto immediato o rimborso.
Il trasporto live deve usare questi controlli senza reinserire credenziali nelrepo.
