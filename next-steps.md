# Prossime attività

Aggiornamento 16 settembre 2026: pubblicazione privata e trasferimento locale
completati e verificati al commit `2c4631ead0b0c19e4a3148e0000d27f93b691b60`.
Branch locale `main`, upstream `origin/main`; dettagli hash in current-state.md.
Fermarsi ora: i passaggi operativi sotto restano subordinati a nuova conferma,
senza chiamate Google, Batch, fatturazione o controlli reali in questa sessione.

1. Leggere REPORT.md inpreflight: conteggi8832completi, costo aggiornato. Non
   confondere countTokens con generazioni o con500RPD ordinari.
2. Verificare quota batch effettiva/abilitazione creazione e cap output fatturabile.
   Eventuale fatturazione: fermarsi per intervento utente, budget30USD invariato.
3. Usare iltrasporto Batch predisposto soltanto quando igates sono verificati;
   prenotazione atomica, jobid, stato incerto enessun retry sono implementati e
   testati conmock, non ancora collaudati sulprovider.
4. Congelare protocollo operativo, parametri, hashes e piano di recupero; registro
   timestamp privato iniziale, eventuale OSF solo dopo scelta/autorizzazione utente.
5. Eseguire24controlli reali come job separato, solo quando cap/quote sono verificati;
   riconciliare anche output tardivi. Non eseguire campagna se un controllo fallisce.
6. Pubblicazione privata e trasferimento al [rimosso] completati; non ripeterli.
   Il commit documentale di migrazione resta locale; push solo dopo conferma esplicita.
7. Fermarsi prima della campagna principale e attendere autorizzazione esplicita.

Non cambiaremodello, Δ, primaria, esclusioni o pipeline per ottenere significatività.
Non risottomettere richieste il cui tentativo precedente non sia riconciliato.
