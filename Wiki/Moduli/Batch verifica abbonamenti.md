---
tipo: modulo
titolo: Batch verifica abbonamenti
alias: [VerificaAbbonamentiBatch, batch giornaliero, degrado]
tag: [dominio/batch]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-16
stato: stabile
---

# Batch verifica abbonamenti

L'unico job schedulato attivo del sistema. Gira **una volta al giorno** e fa quattro cose: backup,
promemoria di rinnovo, degrado dei ruoli scaduti, disattivazione delle promo finite.

## Quando gira

```java
@Scheduled(cron = "0 0 22 * * *")
```

Le **22:00** del fuso della JVM. Il commento nel codice spiega la scelta: «22 perché esiste un fuso
di 2 ore», cioè la mezzanotte italiana con JVM in UTC. ⚠️ Se la JVM girasse già in `Europe/Rome`, il
batch partirebbe alle 22:00 locali: il valore va riletto insieme al fuso del server.

Il resto del codice usa invece esplicitamente `DateValidator.oreItaliane()`
(`LocalDateTime.now(ZoneId.of("Europe/Rome"))`).

## Tre attività, tre interruttori

Il batch fa tre cose indipendenti, ognuna con la propria chiave in [[Tabella cfg_server]]:

| Chiave | Governa | Si spegne con | Se manca |
|---|---|---|---|
| `BACKUP_DB_ABILITATO` | il backup del database | `false` | attiva |
| `LOG_CONSERVAZIONE_GIORNI` | la pulizia del [[Log operativo]] | `0` | **non cancella** |
| `BATCH_VERIFICA_ABBONAMENTI` | promemoria, scadenze e degradi | `false` | attiva |

Sono separate perché il backup è l'unica rete di sicurezza sui dati: deve poter continuare anche
quando si ferma la gestione degli abbonamenti — il caso tipico è un ambiente di collaudo che lavora
su una copia dei dati di produzione, dove i degradi colpirebbero utenti veri.

Le due chiavi booleane, se mancano, si assumono abilitate: il comportamento storico resta
invariato. `LOG_CONSERVAZIONE_GIORNI` fa il contrario, perché lì la scelta prudente è non
cancellare nulla.

## Cosa fa, nell'ordine

1. **Backup del database** — `databaseBackupService.executeBackup()`, se `BACKUP_DB_ABILITATO`. Se
   fallisce il batch **prosegue**, con un warning ([[Backup del database]]).
2. **Pulizia del [[Log operativo]]** — via le righe più vecchie di `LOG_CONSERVAZIONE_GIORNI`.
   Viene **dopo il backup** di proposito: così le righe cancellate restano recuperabili
   dall'ultimo backup. Anche qui un errore non ferma il resto.
3. **Esclusione dei lifetime** — gli ID in `utenti_lifetime` vengono tolti dalla lista prima di ogni
   controllo ([[Utente lifetime]]).
4. **Disattivazione delle promo scadute** — ogni promo attiva con `data_fine` passata va a
   `attivo = false` ([[Promozioni temporali]]).
5. **Ciclo su tutti gli utenti**, con `dataScadenzaIscrizione` non nulla:

| Condizione | Azione |
|---|---|
| scadenza **oggi** | DM «scade oggi» |
| scadenza fra **8 giorni** esatti | DM «mancano 8 giorni» |
| scadenza fra **4 giorni** esatti | DM «mancano 4 giorni» |
| scadenza + `N_GIORNI_DOPO_SCADENZA` passata | **degrado** |

## Il degrado

Quando il periodo di tolleranza (`N_GIORNI_DOPO_SCADENZA`, oggi **3**) è trascorso:

```java
cambiaRuolo(discordId, SUPPORTER_MEMBER, GUEST);
utente.setMembroPioniere(false);
utente.setPianoApplicato(BASIC);
utente.setDataScadenzaIscrizione(null);
```

più una notifica agli admin: «L'utente **X** è stato degradato e non è più SUPPORTER_MEMBER».

Due conseguenze importanti:

- lo status di [[Membri pionieri]] è perso, ma **il posto no**: `pioniere_storico` non viene toccato
  e `PIONIERI_ASSEGNATI` non scende. Se l'utente rientra quando ci sono ancora posti liberi
  riottiene il prezzo agevolato senza consumarne un altro; a tetto pieno paga il prezzo pieno;
- il campo `abilitato` è stato eliminato il 2026-08-13: proprio perché il degrado non lo toccava, non era un indicatore affidabile ([[Utente]]).

## Il promemoria è a giorno esatto

I controlli usano `equals` sulla data, non `isBefore`: se il batch **non gira** in un certo giorno
(app ferma, deploy in corso), quel promemoria **è perso per sempre**. Il degrado invece usa
`isBefore`, quindi recupera da solo al primo giro utile.

Nota: una volta effettuato il degrado, `dataScadenzaIscrizione` diventa `null` e l'utente esce dai
controlli successivi — non viene mai degradato due volte.

## La parte disattivata

Il blocco che avrebbe rimosso il ruolo `GOLD_SUPPORTER_MEMBER` dopo 30 giorni dall'ultima donazione
è **commentato**, con la nota «Da sviluppare meglio». Vedi [[Sostegno libero]].

## Voci correlate
- [[Abbonamento Supporter Member]]
- [[Ruoli Discord]]
- [[Tabella cfg_server]]
- [[Backup del database]]
