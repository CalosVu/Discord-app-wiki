---
tipo: hub
titolo: Entita
alias: [Entità, oggetti del dominio]
tag: [dominio/entita]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Entita

Le "cose" del dominio: gli oggetti che l'applicazione persiste e manipola. Ogni pagina qui
corrisponde a un'entità JPA e alla sua tabella MySQL. Per la vista d'insieme delle tabelle e delle
relazioni, vedi [[Schema del database]].

## Persone e accessi

- [[Utente]] — l'utente Discord censito, con abbonamento e referral. Tabella `users`.
- [[Utente lifetime]] — accesso permanente, esente da scadenze. Tabella `utenti_lifetime`.
- [[Accettazione disclaimer]] — chi ha accettato le regole. Tabella `disclaimer_accept`.
- [[Agente]] — chi porta iscritti e percepisce commissioni. Tabella `agenti`.
- [[Relatore]] — chi pubblica masterclass. Tabella `relatori`.

## Offerta e prezzi

- [[Catalogo servizi]] — piani BASIC / PIONIERE e promozioni. Tabella `catalogo_servizi`.
- [[Masterclass]] — il singolo contenuto video in vendita. Tabella `masterclass`.

## Movimenti di denaro

- [[Pagamento]] — incasso Supporter Member o donazione. Tabella `payments`.
- [[Pagamento masterclass]] — acquisto di una masterclass. Tabella `pagamenti_masterclass`.
- [[Commissione pagamento]] — riga di commissione maturata da un agente. Tabella `commissioni_pagamento`.
- [[Prelievo]] — uscita registrata da un admin. Tabella `track_prelievi`.
- [[Snapshot bilancio]] — fotografia periodica del bilancio. Tabella `snapshot_bilancio` (**non alimentata**).

## Tracciamento

- [[Referral agent]] — il codice invito Discord e chi l'ha creato. Tabella `referral_agent`.
- [[Referral pendente]] — utente in attesa di attribuzione del referral. Tabella `referral_pendenti`.
- [[Tentativo di verifica transazione]] — ogni tentativo di verifica crypto. Tabella `user_verify_transaction`.
- [[Configurazione di server]] — parametro runtime chiave/valore. Tabella `server_config`.

## Voci correlate
- [[Schema del database]]
- [[Enum di dominio]]
- [[Panoramica]]
