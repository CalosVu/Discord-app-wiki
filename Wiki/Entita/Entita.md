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

- [[Utente]] — l'utente Discord censito, con abbonamento e referral. Tabella `utenti`.
- [[Utente lifetime]] — accesso permanente, esente da scadenze. Tabella `utenti_lifetime`.
- [[Accettazione disclaimer]] — chi ha accettato le regole. Tabella `utenti_disclaimer`.
- [[Agente]] — chi porta iscritti e percepisce commissioni. Tabella `referral_agenti`.
- [[Relatore]] — chi pubblica masterclass. Tabella `masterclass_relatori`.

## Offerta e prezzi

- [[Catalogo servizi]] — piani BASIC / PIONIERE e promozioni. Tabella `cfg_catalogo_servizi`.
- [[Masterclass]] — il singolo contenuto video in vendita. Tabella `masterclass`.

## Movimenti di denaro

- [[Pagamento]] — incasso Supporter Member o donazione. Tabella `pagamenti`.
- [[Pagamento masterclass]] — acquisto di una masterclass. Tabella `masterclass_pagamenti`.
- [[Commissione pagamento]] — riga di commissione maturata da un agente. Tabella `referral_commissioni`.
- [[Prelievo]] — uscita registrata da un admin. Tabella `pagamenti_prelievi`.
- [[Snapshot bilancio]] — fotografia periodica del bilancio. Tabella `snapshot_bilancio` (**non alimentata**).

## Tracciamento

- [[Referral agent]] — il codice invito Discord e chi l'ha creato. Tabella `referral_utenti`.
- [[Referral pendente]] — utente in attesa di attribuzione del referral. Tabella `referral_pendenti`.
- [[Tentativo di verifica transazione]] — ogni tentativo di verifica crypto. Tabella `pagamenti_utenti_verifiche`.
- [[Configurazione di server]] — parametro runtime chiave/valore. Tabella `cfg_server`.

## Voci correlate
- [[Schema del database]]
- [[Enum di dominio]]
- [[Panoramica]]
