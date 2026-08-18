---
tipo: concetto
titolo: Ruoli Discord
alias: [ruoli, SUPPORTER_MEMBER, GUEST, GOLD_SUPPORTER_MEMBER]
tag: [dominio/accessi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Ruoli Discord

I ruoli sulla guild sono il **meccanismo di accesso vero**: sono loro a decidere quali canali un
utente vede. Il database registra lo stato, ma è l'assegnazione del ruolo a dare l'accesso.

## I quattro ruoli

| Ruolo | Chiave in `cfg_server` | Chi lo assegna | Quando |
|---|---|---|---|
| **GUEST** | `RUOLO_NEW_ENTRY` | `DisclaimerListener` | all'ingresso nel server, e di nuovo al degrado |
| **SUPPORTER_MEMBER** | `RUOLO_ABBONATO` | flusso di pagamento | a ogni pagamento di abbonamento andato a buon fine |
| **GOLD_SUPPORTER_MEMBER** | `RUOLO_DONAZIONE` | flusso di pagamento | a ogni [[Sostegno libero]] |
| **ADMIN** | `RUOLO_ADMIN` | manualmente sul server | mai toccato dall'app: è un **input**, non un output |

I nomi effettivi vivono **solo** in [[Tabella cfg_server]]: le variabili d'ambiente
`DISCORD_*_ROLE` sono state rimosse con `V29`, perché una seconda fonte poteva divergere da quella
vera.

Il codice cerca il ruolo **per nome** sulla guild (`getRolesByName`), quindi rinominare un ruolo su
Discord senza aggiornare la riga rompe l'assegnazione in silenzio: viene solo loggato «Ruolo non
trovato nel server».

## Le tre operazioni

- **`assegnaRuolo`** — aggiunge, senza togliere nulla. Usata dai pagamenti.
- **`cambiaRuolo`** — rimuove il vecchio e aggiunge il nuovo. Usata dal degrado
  (`SUPPORTER_MEMBER` → `GUEST`).
- **`rimuoviRuolo`** — toglie e basta, se il membro ce l'ha davvero. Definita ma **mai invocata**:
  era pensata per la scadenza del badge GOLD, oggi non attiva.

Tutte falliscono in modo **silenzioso e non bloccante**: se il ruolo non esiste, o il bot non ha i
permessi, o l'utente ha un ruolo più alto del bot, viene loggato un errore ma il pagamento risulta
comunque registrato a database. Un utente può quindi avere l'abbonamento valido nel DB e **nessun
ruolo** su Discord.

## Il ruolo ADMIN è la sola autorizzazione applicativa

Non esiste una tabella di amministratori: `isAdmin(discordId)` interroga Discord in tempo reale e
verifica che il membro abbia il ruolo il cui nome è in `cfg_server.RUOLO_ADMIN`. Chi ha quel ruolo può
usare tutti i [[Comandi admin]], registrare [[Prelievo|prelievi]] e leggere i report finanziari.

Conseguenza operativa: **assegnare il ruolo admin su Discord dà accesso immediato** a tutte le
funzioni amministrative, senza passare da alcun deploy o modifica al database.

## Voci correlate
- [[Abbonamento Supporter Member]]
- [[Batch verifica abbonamenti]]
- [[Comandi admin]]
