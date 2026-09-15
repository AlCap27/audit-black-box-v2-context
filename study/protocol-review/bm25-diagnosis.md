# Diagnosi BM25 riproducibile

14 settembre 2026. Nessuna nuova generazione. Esecuzione: dalla workspace, `python outputs/audit-black-box-v2/protocol-review/check_bm25.py`.

Lo script verifica 1479 file sigillati del primo pilot e 2152 dell'estensione, ricostruisce le 480 tracce originali e ne controlla l'identità. Ricostruisce poi quattro configurazioni per un totale di 1920 recuperi offline. Sorgenti e campagne originali non modificati. Dati dettagliati: `bm25-checks.json`.

| Configurazione globale | A recuperato | B | C | D | Query senza venditori |
|---|---:|---:|---:|---:|---:|
| Originale: schema e llms | 163 | 174 | 2 | 187 | 291/480 |
| Senza schema, con llms | 84 | 109 | 127 | 165 | 305/480 |
| Con schema, senza llms | 300 | 302 | 20 | 18 | 240/480 |
| Sola prosa HTML | 127 | 146 | 183 | 184 | 240/480 |

Sono conteggi venditore-query, non numeri di query esclusive: una query può recuperare più venditori. Per la probabilità per opportunità, dividere ciascuna cella dei bundle per 3840 (480 query × otto venditori per bundle).

Nella configurazione originale i 187 recuperi D sono tutti da llms.txt; i due C provengono da HTML+schema. Il file llms aggiunge un passaggio breve che compete con l'HTML arricchito. Il limite di un chunk per venditore viene applicato dopo il ranking e lascia passare il migliore.

L'estrattore conserva il JSON-LD e lo concatena alla prosa. I chunk C hanno mediamente circa 102 token, contro circa 37 dei chunk A/B. La dimensione di chunking è espressa in parole separate da spazi, mentre BM25 tokenizza punteggiatura e Unicode: non confondere le due lunghezze. BM25 applica frequenza dei termini, frequenza documentale e normalizzazione della lunghezza. Le variazioni osservate sono compatibili con l'interazione fra rappresentazione e ranking, ma questo controllo non isola il contributo numerico di ogni termine della formula.

Le ablation cambiano l'intero indice, comprese IDF, lunghezza media e numero di chunk. Il recupero C da 2 a 127 non è l'effetto diretto della sola rimozione individuale di schema a concorrenti invariati. Né possiamo calcolare le raccomandazioni delle configurazioni alternative riutilizzando le vecchie risposte Gemini: cambierebbero i prompt.

Nella sola prosa i bundle non alterano il testo indicizzato di una data identità. I conteggi aggregati restano diversi perché le identità hanno template e tie-break diversi e le etichette casuali non sono perfettamente controbilanciate nell'insieme finito. Una differenza aggregata A/B non dimostra un effetto della sitemap.

Controlli da incorporare nel nuovo sviluppo: A/B invarianti a identità fissata; token e numero di chunk per sorgente; stesso testo mostrato per il braccio a contesto controllato; ordine controbilanciato; log separato di recuperato, nome effettivamente esposto e raccomandato. Conservare una configurazione originale come baseline dichiarata: non scegliere il preprocessing che favorisce D.

La diagnosi non dimostra che BM25 sia sbagliato o che schema sia dannoso sul web. Dimostra la dipendenza del risultato da una pipeline specifica. Il riferimento metodologico di BM25 è Robertson e Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*: https://www.nowpublishers.com/article/DownloadEBook/INR-019.
