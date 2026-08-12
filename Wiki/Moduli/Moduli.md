---
tipo: hub
titolo: Moduli
alias: [flussi, aree funzionali]
tag: [dominio/moduli]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Moduli

Le aree funzionali e i flussi del sistema: cosa fa l'applicazione, in che ordine e con quali
componenti.

## Il bot e i suoi comandi

- [[Bot Discord]] — avvio, intent, listener, routing degli eventi.
- [[Onboarding e disclaimer]] — dall'ingresso nel server al censimento dell'utente.
- [[Comandi utente]] — `!Comandi`, `!Donazione`, `!verifica-transazione`, `!Bacheca`, `!masterclass`…
- [[Comandi admin]] — il menu `!Admin` con report, prelievi, scadenze, fix referral.
- [[Comandi agenti]] — `!mieiref`.
- [[Comandi relatori]] — `!miemasterclass`.

## Incassi

- [[Pagamenti Stripe]] — link di checkout, webhook, due account.
- [[Pagamenti crypto Arbitrum]] — verifica on-chain di USDT/USDC via Web3j.
- [[Sistema masterclass]] — vendita dei video dei relatori.
- [[Storage R2]] — bucket privato e link firmati a scadenza.

## Automazioni e servizi

- [[Batch verifica abbonamenti]] — il batch giornaliero: promemoria, degrado, promo scadute, backup.
- [[Backup del database]] — `mysqldump` con rotazione.
- [[Reportistica]] — saldi, report periodo, scadenze.

## Confini del sistema

- [[Integrazione VuTracker]] — l'endpoint REST con API key.
- [[Sicurezza e autenticazione]] — Spring Security, filtri, il flusso JWT non attivo.
- [[Architettura dei moduli Maven]] — i 5 moduli e le loro dipendenze.
- [[Deploy e CI-CD]] — da `git push` alla produzione.

## Voci correlate
- [[Concetti]]
- [[Entita]]
- [[Panoramica]]
