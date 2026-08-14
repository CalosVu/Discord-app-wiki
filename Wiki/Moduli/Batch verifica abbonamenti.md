---
tipo: modulo
titolo: Batch verifica abbonamenti
alias: [VerificaAbbonamentiBatch, batch giornaliero, degrado]
tag: [dominio/batch]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-12
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

## Due interruttori, non uno

Da `V7`/`V8` il batch è governato da due chiavi indipendenti di [[Tabella cfg_server]]:

| `BACKUP_DB_ABILITATO` | `BATCH_VERIFICA_ABBONAMENTI` | Alle 22:00 |
|---|---|---|
| `false` | `false` | nulla: il metodo esce subito |
| `true` | `false` | solo il backup |
| `false` | `true` | solo promemoria, scadenze e degradi |
| `true` | `true` | backup, poi il resto |

Sono separati perché il backup è l'unica rete di sicurezza sui dati: deve poter continuare anche
quando si ferma la gestione degli abbonamenti — il caso tipico è un ambiente di collaudo che lavora
su una copia dei dati di produzione, dove i degradi colpirebbero utenti veri. Se una chiave manca
si assume abilitata, quindi il comportamento storico resta invariato.

## Cosa fa, nell'ordine

1. **Backup del database** — `databaseBackupService.executeBackup()`, se `BACKUP_DB_ABILITATO`. Se
   fallisce il batch **prosegue**, con un warning ([[Backup del database]]).
2. **Esclusione dei lifetime** — gli ID in `utenti_lifetime` vengono tolti dalla lista prima di ogni
   controllo ([[Utente lifetime]]).
3. **Disattivazione delle promo scadute** — ogni `PROMO` attiva con `data_fine` passata va a
   `attivo = false` ([[Promozioni temporali]]).
4. **Ciclo su tutti gli utenti**, con `dataScadenzaIscrizione` non nulla:

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

- lo status di [[Membri pionieri]] è perso **definitivamente**: nessun codice lo ripristina;
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
