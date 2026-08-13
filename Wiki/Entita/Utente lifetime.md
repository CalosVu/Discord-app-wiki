---
tipo: entita
titolo: Utente lifetime
alias: [utenti_lifetime, UtentiLifetime, lifetime]
tag: [dominio/utenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Utente lifetime

Un utente con **accesso permanente**, esente da scadenze e rinnovi. Tabella `utenti_lifetime`,
entità `UtentiLifetime`.

## Struttura

Tabella minimale, tre colonne: `id`, `discord_id` (`UNIQUE`), `username`. Nessuna FK verso `utenti`:
è un elenco autonomo di Discord ID.

Popolata **a mano via SQL**. Nei dati iniziali del repo contiene 12 righe (staff e primi
sostenitori).

## I due effetti concreti

Essere in questa tabella cambia due comportamenti, e solo due:

1. **Il batch di verifica lo salta.** `VerificaAbbonamentiBatch` carica gli ID lifetime e li
   **esclude dalla lista** prima di ogni controllo: nessun promemoria di rinnovo, nessun degrado di
   ruolo, indipendentemente da `dataScadenzaIscrizione` ([[Batch verifica abbonamenti]]).
2. **La verifica di accesso lo promuove.** `VerificaAccessoService` controlla la tabella **per
   prima**: se il Discord ID è presente, risponde `supporterAttivo = true` con ruolo `LIFETIME` e
   `scadenza = null`, senza nemmeno leggere `utenti` ([[Integrazione VuTracker]]).

## Cosa NON fa

- **Non assegna il ruolo Discord.** L'appartenenza alla tabella non innesca nessun
  `assegnaRuolo`: il ruolo `SUPPORTER_MEMBER` va assegnato manualmente sul server, altrimenti
  l'utente resta lifetime "sulla carta" ma senza accesso ai canali.
- **Non esenta dai pagamenti.** Un lifetime che usa `!Donazione` percorre il flusso normale e paga
  come chiunque altro.
- **Non è collegato a `utenti`.** Un ID può stare qui senza avere una riga in `utenti`; in quel caso
  la verifica accesso risponde `LIFETIME` con `username = null`.

## Voci correlate
- [[Utente]]
- [[Batch verifica abbonamenti]]
- [[Integrazione VuTracker]]
