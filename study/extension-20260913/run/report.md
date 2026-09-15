# Audit Black Box V2

Esperimento con generatore API

| Bundle | P(recuperato) | P(nome nel contesto) | P(raccomandato), risposte valide |
|---|---:|---:|---:|
| A | 0.043 | 0.043 | 0.033854166666666664 |
| B | 0.044 | 0.044 | 0.04123263888888889 |
| C | 0.000 | 0.000 | 0 |
| D | 0.050 | 0.050 | 0.04210069444444445 |

Stati risposte: {'valid': 288, 'not_run': 0}.

Il retrieval è realmente eseguito sul corpus artificiale. La sitemap non interviene nella scoperta: tutti i file sono caricati da manifest.
I punteggi Agentabile non sono ancora calibrati. I bundle non equivalgono a dosi 20/40/60/80.
Le probabilità condizionate sono descrittive; non quantificano mediazione causale.
