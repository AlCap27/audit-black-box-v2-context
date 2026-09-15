# Protocollo confermativo — addendum Batch

Stato preparato, non congelato. Questo documento aggiorna quantità ed esecuzione
del protocollo in `source-protocol/PROTOCOL.md`, che conserva le definizioni,
analisi di missing e molteplicità. Nessun esito confermativo è stato osservato.

## Popolazione, interventi, stadi

Popolazione finita: 32 identità sintetiche del dominio vino e 24 query predefinite
(12 basi × due intenti), quattro template. Nessuna generalizzazione ad agenti di
acquisto completi, nuovi mercati o motori di ricerca pubblici.

S = JSON-LD presente/assente; L = llms.txt presente/assente;
T = stessa prosa del body ripetuta due volte/una volta. T misura ridondanza,
non qualità o completezza. llms e descrizione JSON-LD conservano sempre una sola
copia della prosa canonica: T non modifica questi due canali. S aggiunge proprietà
strutturate degli stessi fatti, senza vantaggi commerciali. Sitemap costante.

Discovery: W indica inclusione mediante manifest locale delle homepage e dei
file opzionali llms; W=1 per tutti i vendor. I 16 benchmark BFS separati verificano
topologie diretta/catena/orfana/ciclica × sitemap sì/no × ordine; non sono prove
di discovery da parte di Google. Il main experiment condiziona su W=1.

Retrieval: Z indica almeno un chunk del vendor nel top5 BM25. X indica presenza
effettiva nel contesto mostrato, registrato separatamente; max100 parole/chunk,
700 parole di contenuto, una occorrenza per vendor, BM25 k1=1,2 e b=0,75.
JSON-LD è serializzato e concatenato al body prima del chunking; llms è un
documento separato. Queste sono proprietà della pipeline sottoposta a studio.

Recommendation: Y indica vendor noto raccomandato nel JSON valido, anche quando
la citazione risulta non supportata (segnalata separatamente). Massimo tre vendor.
Astensione valida=zero; errore/troncamento/assenza di output=missing.
Nomi sconosciuti e citazioni non supportate si riportano, senza cancellare gli esiti.

Per F∈{S,L,T}, marginalizzando gli altri due fattori e le query, stimare:
1. differenza P(Z=1|F=1,W=1) − P(Z=1|F=0,W=1);
2. differenza P(Y=1|Z=1,F=1,W=1) − P(Y=1|Z=1,F=0,W=1), come rapporto
   dei totali, non media dei rapporti delle assegnazioni;
3. differenza P(Y=1|F=1,W=1) − P(Y=1|F=0,W=1).

Il secondo contrasto seleziona popolazioni diverse tramite Z: non identifica un
effetto causale diretto sul generatore. Riportare anche Y quando Z=0, senza imporre
un tasso nullo. Effetto solo su Z = evidenza retrieval; effetto su Y totale =
evidenza sull'intera pipeline fissata. Un contrasto condizionato non dimostra
mediazione o effetto diretto. Per quello servirebbe un nuovo esperimento a contesto
controllato, non incluso. La sensibilità BM25 del pilot resta diagnostica.

## Randomizzazione e analisi

367 assegnazioni nuove `c0000`–`c0366`, seme pubblicato 202609140367 non cercato
per massimizzare un risultato. Per assegnazione e template si permutano le otto
celle sulle otto identità: quattro vendor/cella, 16 per livello di ogni fattore.
Una replica per query. Unità indipendente proposta: assegnazione dell'intero pool;
vendor e query al suo interno non sono repliche indipendenti. Competizione e
interferenza tra vendor fanno parte dell'estimando in pool bilanciato.

Primaria proposta: effetto totale L, bilaterale α=0,025. Otto secondarie:
L retrieval/condizionato, S e T totale/retrieval/condizionato, ciascuna α=0,003125.
Somma degli alpha ≤0,05. Interazioni, intenti, template ed eventuali altre pipeline
sono esplorativi. Nessuna scelta della primaria o della soglia dopo i risultati.

Analisi primaria: differenza media tra livelli L calcolata su ogni assegnazione,
24 query e 16 vendor/livello. Supporto [−3/16,+3/16]. Test Hoeffding bilaterale
con ampiezza Lr=3/8 e soglia Lr·sqrt(log(2/α)/(2N)). Al Δ=0,05,
N≥ceil(Lr²(√log(2/α)+√log(1/0,1))²/(2Δ²))=367.
È una garanzia sufficiente **sotto indipendenza dei cluster e dati completi**,
non una garanzia incondizionata del servizio batch. Nulli, negativi e intervalli
ampi si riportano integralmente. Effetto statisticamente rilevato non equivale
automaticamente a effetto ≥5 pp.

Sensitivity già calcolata: a potenza90% Δ2 richiede2292 assegnazioni/55008
generazioni, Δ5 367/8808, Δ10 92/2208, più24controlli. A80% rispettivamente
1987/47688,318/7632,80/1920. Non si aumenta Δ per ottenere significatività.
Il retrieval, con ampiezza5/8 e α secondario, richiederebbe1288 assegnazioni
offline per la garanzia90% a5pp; questo pacchetto ne prepara367, senza attribuirgli
quella garanzia. Estensione retrieval-only eventualmente da approvare prima freeze.
Il condizionato non ha garanzia90%: denominatori bassi o zero danno intervalli
larghi o non informativi, come indicato nel protocollo precedente.

Il pilot serve solo a descrivere baseline, variabilità, template, dipendenze e
costi. Le sue stime D−A non sono una validazione della varianza del nuovo S×L×T.

## Adattamento al batch e dipendenze

24 controlli separati (12 fonti vendor pertinenti, 12 solo editoriali) precedono
qualunque main job. Tutti devono avere JSON valido, citazione coerente ed esito
atteso; un fallimento ferma l'ammissione della campagna, senza modificare i controlli
per farli passare. Un problema tecnico risolto richiede registrazione e nuovo freeze.

Dodici main job da734richieste, due query ciascuno per tutte le assegnazioni.
Ordine delle righe permutato; nessuna garanzia sull'ordine di esecuzione Google.
Proposta operativa: un job main alla volta, riconciliazione prima del successivo.
Questo evita di associare un'intera assegnazione a un unico job, ma non elimina
dipendenze condivise o deriva del provider. Registrare job, tempi disponibili,
modelVersion e usage per risposta. Modello fisso gemini-3.1-flash-lite,
temperature0,7, thinking minimal, maxOutputTokens1200, JSON, nessun tool/grounding.
Compatibilità di questi parametri va verificata nei controlli prima del freeze finale.

Riportare sensibilità per job e query; se emerge deriva o dipendenza trasversale
materiale, non mantenere il claim di potenza/validità Hoeffding senza giustificazione.
Non è possibile stimare robustamente una dipendenza arbitraria da12job e una replica.
Versioni miste: conservare tutto, interrompere ulteriori invii; analisi stratificate
descrittive, nessuna fusione automatica come singolo esperimento confermativo.

## Errori, missing, tentativi incerti e arresto

Nessuno stopping per efficacia, futilità o p-value. Target fisso367, nessuna campagna
extra scelta sui risultati. Stop tecnico all'osservazione di un'anomalia: impedire
nuovi job e chiedere cancellazione di quello attivo se appropriato. **Richieste già
accettate possono continuare ed essere fatturate**, anche dopo richiesta di cancel.
Conservare risultati tardivi, stato terminale e addebiti. Mai promettere stop immediato.

Prima della creazione futura: riservare costo e registrare tentativo. Se risposta
create non arriva, stato PREPARED_UNCERTAIN e riserva trattenuta; riconciliare
nome/display name, elenco job, hash e orari. Non dedurre fallimento da timeout/404.
Mai risottomettere richieste non riconciliate. Nessun retry automatico nel pacchetto.

Importazione per key, non posizione. Duplicati identici contati una volta e segnalati;
discordanti in quarantena, mai scegliere il più favorevole. Missing solo dopo stato
terminale; prima pending. Raw immutabile, errori e versioni conservati. Un output
non valido non è astensione. Usage assente non significa costo zero. Nessuna riserva
si libera automaticamente, nemmeno dopo cancellazione o importazione riuscita.

Prima freeze: escludere soltanto fixture tecnicamente non conformi, correggere e
rigenerare tutto in nuova versione. Dopo freeze nessuna esclusione per ranking,
esito negativo, bassa esposizione o errore. Analisi primaria inferenziale completa
solo con condizioni soddisfatte; con missing usare bounds su tutti gli slot previsti,
analisi complete-case soltanto supplementare e dichiarata. Sensibilità MAR/IPW
eventuale non sostituisce l'analisi worst-case senza assunzioni documentate.

## PC spento e conservazione

Dopo conferma e salvataggio del nome job, Google esegue senza il PC acceso.
Nessun demone, webhook o modifica VPS è predisposto. Riaccendere per controllare
e scaricare il job entro24ore, verificare expirationTime effettivo dei file e
salvare raw/hash prima di spegnere di nuovo. La disponibilità indefinita dei risultati
non è garantita. Se non è possibile questo breve rientro, serve un archiviatore cloud
separato da autorizzare; non usare i servizi VPS esistenti.
