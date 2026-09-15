# Pilot esteso V2 — conclusione 13 settembre 2026

Tentativi complessivi: 224/224. Probe: {'valid': 31, 'api_error': 1}. Pilot: {'valid': 192}. Modello risolto: ['gemini-3.1-flash-lite'].

Astensioni: 117; risposte con nomi sconosciuti: 0; raccomandazioni non supportate: 0.

| Bundle | Recuperato | Raccomandato, sole risposte valide |
|---|---:|---:|
| A | 4.10% | 3.45% |
| B | 4.69% | 3.52% |
| C | 0.07% | 0.00% |
| D | 4.69% | 4.56% |

Limiti peggior caso D−A su tutti gli slot pianificati: [1.1068%, 1.1068%]. Sono limiti di identificazione per i mancanti, non intervalli di confidenza.

La differenza osservata D−A è +1,11 punti percentuali. L'intervallo t esplorativo
al 95% è da −1,61 a +3,83 punti: include zero e non dimostra un vantaggio di D.
La sua copertura non è validata per lo studio confermativo (vedere sotto).
Le percentuali in tabella sono per opportunità venditore-query, non per risposta.

Assegnazioni complete: 8/8; SD dei contrasti: 0.03251858395335426. Nessun errore
nelle generazioni di questo pilot; non c'è selezione di assegnazioni per mancanti.
La stima della variabilità resta incerta per il campione di otto assegnazioni.

## Dimensionamento e robustezza

Per un effetto ipotizzato di due punti percentuali, il modello normale propone
23 assegnazioni (552 chiamate) usando la SD osservata, oppure 88 (2112 chiamate)
usando il suo limite superiore al 95% sotto normalità. Sono scenari, non un budget
autorizzato o una numerosità confermativa già validata. Vedere power_followup.json.

La sensibilità empirica con 10000 ricampionamenti dei contrasti centrati evidenzia
un problema del test t con otto assegnazioni: 10,92% di rifiuti sotto l'ipotesi nulla
simulata, contro il 5% nominale (errore Monte Carlo circa 0,31 punti). Con 88
assegnazioni scende a 5,11%. È una distribuzione ricostruita da appena otto valori,
non la distribuzione vera; l'alternativa additiva non simula il meccanismo top-3.
Il gate statistico rimane quindi aperto: non avviare raccolta confermativa con
la sola giustificazione dell'intervallo t o di queste proiezioni.

I probe validi non dichiarano familiarità; v019 resta non verificato per HTTP 503. Lo screening web/V1 non aveva rilevato collisioni esatte. Nessuna prova di assenza dai dati di addestramento.

Il corpus e il modello sono controllati. I risultati non generalizzano a Google Search, Tavily o altri assistenti. Sitemap esclusa dal meccanismo di scoperta. Nessuna percentuale di mediazione causale.

Integrità verificata in un nuovo processo; prompt, risposte, indici, ledger e sorgenti conservati. Nessuna modifica a VPS/Cloudflare. Chiave esclusa dal pacchetto.

Token dichiarati (probe e pilot): {'promptTokenCount': 103491, 'candidatesTokenCount': 15602, 'thoughtsTokenCount': 0, 'totalTokenCount': 119093}. Nessuna fatturazione verificata.

Prima dello studio confermativo restano dimensionamento validato, politica sui mancanti, screening residuo e preregistrazione pubblica. Il budget autorizzato di questa campagna non va superato.
