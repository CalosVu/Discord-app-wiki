---
tipo: hub
titolo: Indice
creato: 2026-07-25
aggiornato: 2026-07-31
stato: stabile
---

# Indice — Wiki di VuPass

Catalogo di tutto ciò che c'è nella wiki, per categoria. Ogni voce: link alla pagina + riassunto
in una riga. L'agente aggiorna questo file ad ogni creazione/rinomina di pagina (CLAUDE.md §6).

Punto di partenza consigliato: [[Panoramica]].

## Entita

- [[Entita]] — hub delle entità del dominio.
- [[Utente]] — l'utente Discord censito: abbonamento, referral, piano, ciclo di vita.
- [[Utente lifetime]] — accesso permanente, escluso dal batch e promosso dalla verifica accesso.
- [[Accettazione disclaimer]] — il gate che abilita ogni operazione sensibile.
- [[Agente]] — chi porta iscritti e percepisce commissioni; si crea via SQL.
- [[Relatore]] — chi pubblica masterclass; il suo id deve combaciare in tre punti.
- [[Catalogo servizi]] — listino BASIC / PIONIERE / PROMO, in EUR e USD.
- [[Masterclass]] — il video in vendita e la catena che porta al file giusto.
- [[Pagamento]] — incasso supporter o donazione, crypto o Stripe.
- [[Pagamento masterclass]] — acquisto di una masterclass; importi in parte teorici.
- [[Commissione pagamento]] — la riga di commissione, con importo calcolato on-demand.
- [[Prelievo]] — uscita registrata da un admin, con verifica on-chain.
- [[Snapshot bilancio]] — fotografia del bilancio: **funzionalità non attiva**.
- [[Referral agent]] — il codice invito Discord; la sua percentuale non conta, ma il contatore `utilizzi` sì.
- [[Referral pendente]] — utente in attesa di attribuzione; la coda di `!SyncReferral`.
- [[Tentativo di verifica transazione]] — registro dei tentativi crypto e rate limiting.
- [[Configurazione di server]] — il meccanismo dei parametri runtime.

## Concetti

- [[Concetti]] — hub dei meccanismi trasversali.
- [[Ruoli Discord]] — i quattro ruoli; ADMIN è l'unica autorizzazione applicativa.
- [[Abbonamento Supporter Member]] — calcolo della scadenza e premio al rinnovo anticipato.
- [[Sostegno libero]] — donazione libera e badge GOLD, di fatto permanente.
- [[Membri pionieri]] — prezzo agevolato, perso definitivamente al degrado.
- [[Promozioni temporali]] — promo a tempo, con referral e mesi forzati.
- [[Sistema referral e commissioni]] — dalla creazione dell'invito alla commissione, e perché i contatori non si riallineano sui fallimenti.
- [[Blocco dei pagamenti]] — i tre flag cross-canale e la difesa su tre livelli.
- [[Bilanciamento degli account Stripe]] — due conti, scelta per saldo netto minore.
- [[Riconciliazione della fee Stripe]] — il pattern A+B e `fee_pending`.
- [[Idempotenza dei webhook]] — protezioni contro il doppio accredito, e il punto debole noto.

## Moduli

- [[Moduli]] — hub dei flussi e delle aree funzionali.
- [[Bot Discord]] — avvio, due istanze JDA, cinque listener, disclaimer pinnato.
- [[Onboarding e disclaimer]] — dall'ingresso al censimento dell'utente.
- [[Comandi utente]] — tutti i comandi disponibili a un utente normale.
- [[Comandi admin]] — il menu `!Admin`, le sue otto voci e `!SyncReferral`.
- [[Comandi agenti]] — `!mieiref`: link attivi e report commissioni.
- [[Comandi relatori]] — `!miemasterclass`: report vendite, con numeri in parte teorici.
- [[Pagamenti Stripe]] — checkout, due endpoint webhook, controllo importo bloccante.
- [[Pagamenti crypto Arbitrum]] — verifica on-chain USDT/USDC con doppia strategia.
- [[Sistema masterclass]] — modello attivo "chiave per relatore" e Connect congelato.
- [[Storage R2]] — bucket privato, HEAD pre-checkout, presigned URL.
- [[Batch verifica abbonamenti]] — l'unico job schedulato attivo.
- [[Backup del database]] — `mysqldump` con rotazione, dentro il batch.
- [[Reportistica]] — formule dei saldi e limiti dei report.
- [[Integrazione VuTracker]] — l'endpoint con API key e la logica di verifica.
- [[Sicurezza e autenticazione]] — Spring Security, firma webhook, JWT non attivo.
- [[Architettura dei moduli Maven]] — i cinque moduli e dove stanno davvero le cose.
- [[Deploy e CI-CD]] — push su `main` = produzione.

## Tassonomie

- [[Tassonomie]] — hub degli elenchi codificati.
- [[Tabella server_config]] — i nove parametri runtime, con valori e chi li legge.
- [[Enum di dominio]] — i valori ammessi e quali sono realmente usati.
- [[Endpoint REST]] — la superficie HTTP completa e la protezione di ciascun percorso.
- [[Schema del database]] — le tabelle, le relazioni e le regole di migrazione.

## Config-Credenziali

- [[Config-Credenziali]] — hub; regola: solo riferimenti, mai valori.
- [[Variabili d'ambiente]] — inventario completo delle variabili lette dall'app.
- [[Chiavi Stripe]] — le chiavi dei due account supporter e quelle per-relatore.
- [[Credenziali R2]] — accesso al bucket privato dei video.
- [[Ambienti e profili Spring]] — `dev`, `docker`, `prod` e le loro differenze.

## Interventi

- [[Interventi]] — hub del tracciamento lavori, con i punti caldi noti del progetto.
- [[2026-07-25 Referral non attribuito e Fix Referral inefficace]] — i tre difetti dell'attribuzione
  referral e il rimedio in tre fasi; implementato.

## Fonti

- [[Fonti]] — gerarchia di attendibilità e elenco delle fonti ingerite.
- [[Codice Discord-access-app]] — il repo applicativo, fonte di rango 1.
- [[DOC_PROGETTO]] — documentazione iniziale, largamente superata.
- [[Integrazione sistema pagamenti]] — specifica iniziale dei pagamenti, superata nei dettagli.
- [[Piano sviluppo masterclass]] — architettura e decisioni del sistema masterclass.
- [[Piano sviluppo doppio Stripe]] — doppio account, flag di blocco, fix notifiche.
- [[Guida di deployment]] — deploy su Hetzner da zero.
- [[Runbook cambio dominio]] — i 5 fronti da allineare, la fonte più recente sull'infrastruttura.
- [[Guida SSL e DNS]] — nginx, certbot, DNS, webhook.
- [[Guida Stripe CLI]] — testing dei webhook in locale.
