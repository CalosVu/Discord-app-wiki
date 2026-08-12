---
tipo: modulo
titolo: Backup del database
alias: [DatabaseBackupService, mysqldump]
tag: [dominio/infrastruttura]
fonti: [Codice Discord-access-app, Guida di deployment]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Backup del database

Il backup automatico del database MySQL, eseguito **dall'applicazione stessa** come primo passo del
[[Batch verifica abbonamenti]].

## Come funziona

1. Legge host, porta e nome del database **dal DataSource** (`DatabaseMetaData.getURL()`): non da
   configurazione duplicata. Se l'host è `localhost` lo converte in `127.0.0.1` per forzare TCP/IP.
2. Crea la sottocartella `backups/` sotto il percorso configurato, se manca.
3. Lancia `mysqldump` con `--routines --triggers --single-transaction --lock-tables=false
   --add-drop-table --extended-insert`, redirigendo lo stdout sul file
   `<database>_backup_yyyy-MM-dd_HH-mm-ss.sql`.
4. Attende con **timeout** (default 300 secondi); allo scadere uccide il processo e segnala il
   fallimento.
5. Se l'esito è positivo, elimina i backup più vecchi della **retention** (default 7 giorni),
   deducendo la data dal nome del file.

## La password non finisce nella process list

La password non è passata come argomento `--password=...` (visibile a chiunque lanci `ps aux`) ma
tramite la **variabile d'ambiente `MYSQL_PWD`** del processo figlio.

## Configurazione

Sotto `spring.datasource.backup` ([[Ambienti e profili Spring]]):

| Parametro | Default |
|---|---|
| `logs.path` | `/opt/discord-bot/logs` (i backup vanno in `backups/` sotto questo path) |
| `retention-days` | 7 |
| `compression-enabled` | `true` |
| `timeout-seconds` | 300 |
| `mysqldump-command` | `mysqldump` |

⚠️ Due parametri sono **dichiarati ma non usati come ci si aspetterebbe**:

- `mysqldump-command` non viene letto: il comando è la stringa letterale `"mysqldump"` nel codice.
  Rinominare o spostare il binario rompe il backup a prescindere dalla configurazione.
- `compression-enabled` aggiunge il flag `--compress` a mysqldump, che comprime **il protocollo di
  rete**, non il file prodotto. Il `.sql` resta non compresso.

## Prerequisiti sul server

Il binario `mysqldump` deve essere installato **sull'host dell'applicazione** e la directory dei log
scrivibile dall'utente `deploy`. Con MySQL in Docker, questo significa avere il client MySQL
installato anche fuori dal container.

## Fallimento non bloccante

Se il backup fallisce, il batch **prosegue comunque** con un warning: la mancanza di backup non
impedisce i promemoria e i degradi.

## ⚠️ I backup generati prima del 2026-08-12 non sono ripristinabili così come sono

Fino a quella data il servizio univa lo **stderr di mysqldump allo stdout**, cioè al file di dump:
warning ed errori finivano **dentro** il `.sql`, fra le istruzioni. Il ripristino si interrompe alla
prima riga con un errore di sintassi.

Verificato sul dump dell'11/08/2026, che conteneva due righe spurie:

```
riga  1: WARNING: --compress is deprecated...
riga 18: mysqldump: Error: 'Access denied; you need (at least one of) the PROCESS privilege(s)...'
```

**I dati erano comunque integri**: il confronto con un dump della stessa base fatto da DBeaver ha
mostrato uno schema identico riga per riga. Il problema era solo il rumore in testa al file.

Per ripristinare un backup di quel periodo, ripulirlo prima:

```bash
grep -vE "^(WARNING:|mysqldump:|ERROR)" backup.sql > backup_pulito.sql
```

Dal fix in poi lo stderr va in un file `.log` affiancato al dump, e il `.sql` contiene solo SQL.
Resta consigliato concedere il privilegio `PROCESS` all'utente MySQL del backup
(`GRANT PROCESS ON *.* TO '<utente>'@'%';`): non serve ai dati, ma toglie l'errore dal log.

## Voci correlate
- [[Batch verifica abbonamenti]]
- [[Deploy e CI-CD]]
- [[Schema del database]]
