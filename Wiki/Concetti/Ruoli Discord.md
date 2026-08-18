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
Discord senza aggiornare la riga rompe l'assegnazione — che però dal 2026-08-18 **non è più
silenziosa**: gli admin ricevono un avviso (vedi sotto).

## Le tre operazioni

- **`assegnaRuolo`** — aggiunge, senza togliere nulla. Usata dai pagamenti.
- **`cambiaRuolo`** — rimuove il vecchio e aggiunge il nuovo. Usata dal degrado
  (`SUPPORTER_MEMBER` → `GUEST`).
- **`rimuoviRuolo`** — toglie e basta, se il membro ce l'ha davvero. Definita ma **mai invocata**:
  era pensata per la scadenza del badge GOLD, oggi non attiva.

Tutte falliscono in modo **non bloccante**: se il ruolo non esiste, o il bot non ha i permessi, o
l'utente ha un ruolo più alto del bot, il pagamento resta comunque registrato a database. Un utente
può quindi avere l'abbonamento valido nel DB e **nessun ruolo** su Discord.

## Quando un ruolo non viene assegnato, gli admin lo sanno

Fino al 2026-08-18 quel fallimento era **silenzioso**: finiva in un `log.error` che nessuno legge, e
l'utente che aveva pagato senza ottenere l'accesso se ne accorgeva prima del sistema. Ora
`assegnaRuolo` avvisa gli admin in DM con utente, ruolo e motivo, ricordando che se c'è stato un
pagamento l'incasso è registrato ma l'accesso no.

Sono coperti tutti i modi di fallire: server irraggiungibile, ruolo inesistente (tipico dopo un
rename su Discord), utente non trovato perché uscito dal server, e il rifiuto di Discord
sull'aggiunta — permessi insufficienti o gerarchia dei ruoli — che prima non aveva nemmeno un
gestore d'errore.

> [!warning] `assegnaRuolo` restituisce `true` prima che il ruolo esista
> JDA lavora in asincrono (`queue`): il valore di ritorno dice che la **richiesta è partita**, non
> che sia andata a buon fine. Nessun chiamante dovrebbe trattarlo come conferma; l'esito reale
> arriva dopo, ed è quello che genera l'avviso agli admin.

## Il ruolo arriva solo a pagamento confermato

Nel flusso crypto l'assegnazione avviene **dopo il commit** della transazione, non prima
(`assegnaRuoloDopoIlCommit`). Discord non partecipa alla transazione: assegnare il ruolo prima
significava che un rollback riportava indietro il database ma non il server Discord, lasciando
l'utente abbonato con `data_scadenza_iscrizione` a `null`.

Quel dettaglio è peggiore di come suona, perché [[Batch verifica abbonamenti|il batch delle 22:00]]
inizia con `if (utente.getDataScadenzaIscrizione() != null)`: **salta proprio le scadenze nulle**.
Un utente finito in quello stato avrebbe avuto accesso permanente e gratuito, invisibile a ogni
controllo automatico.

Il flusso Stripe non è transazionale: lì la chiamata parte subito, perché non c'è nessun commit da
attendere.

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
