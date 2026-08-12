---
tipo: tassonomia
titolo: Schema del database
alias: [database, tabelle, DDL, migrazioni]
tag: [dominio/database]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-12
stato: stabile
---

# Schema del database

Le tabelle MySQL del sistema, le relazioni e — soprattutto — le **regole per modificarle** senza
rompere la produzione.

Database: `discord_db`. Schema e dati sono versionati con **Flyway** in
`discord-access-persistence/src/main/resources/db/migration/`.

## Le tredici tabelle

| Tabella | Entità | Pagina |
|---|---|---|
| `users` | `User` | [[Utente]] |
| `utenti_lifetime` | `UtentiLifetime` | [[Utente lifetime]] |
| `disclaimer_accept` | `DisclaimerAccept` | [[Accettazione disclaimer]] |
| `catalogo_servizi` | `CatalogoServizi` | [[Catalogo servizi]] |
| `referral_agent` | `ReferralAgent` | [[Referral agent]] |
| `agenti` | `Agente` | [[Agente]] |
| `commissioni_pagamento` | `CommissionePagamento` | [[Commissione pagamento]] |
| `payments` | `Payments` | [[Pagamento]] |
| `track_prelievi` | `TrackPrelievi` | [[Prelievo]] |
| `user_verify_transaction` | `UserVerifyTransaction` | [[Tentativo di verifica transazione]] |
| `server_config` | `ServerConfig` | [[Configurazione di server]] |
| `relatori` | `Relatore` | [[Relatore]] |
| `masterclass` | `Masterclass` | [[Masterclass]] |
| `pagamenti_masterclass` | `PagamentoMasterclass` | [[Pagamento masterclass]] |
| `referral_pendenti` | `ReferralPendente` | [[Referral pendente]] |
| `snapshot_bilancio` | `SnapshotBilancio` | [[Snapshot bilancio]] (non alimentata) |
| `log_service` | `LogService` | tabella di log, senza pagina dedicata |
| `flyway_schema_history` | — | storico delle migration, gestita da Flyway |

## Le relazioni portanti

```
referral_agent ──┬──< users >──── catalogo_servizi   (piano_applicato_id)
                 │       │  │
                 │       │  └──── disclaimer_accept  (1-a-1)
                 │       │  └──── payments           (ultimo pagamento, 1-a-1)
                 │       ├──< agenti      ──< commissioni_pagamento >── payments
                 │       ├──< relatori    ──< masterclass ──< pagamenti_masterclass
                 │       └──< user_verify_transaction
                 └──< catalogo_servizi    (promo per referral)
```

Particolarità: `payments` ha **due** FK verso `users` — su `user_id` e su `discord_id`.
`log_service` ha una FK verso `disclaimer_accept.discord_id`, non verso `users`.
`referral_pendenti` ha una FK verso `users.discord_id` con vincolo di unicità: una riga per utente.

## Le migration applicate

| Versione | Contenuto |
|---|---|
| `V1__baseline_schema.sql` | schema di base (ex `sql/create_table.sql`) |
| `V2__dati_iniziali.sql` | dati di bootstrap (ex `sql/insert.sql`) |
| `V3__referral_utilizzi_e_pendenti.sql` | colonna `referral_agent.utilizzi` + tabella `referral_pendenti` |
| `V4__text_config.sql` | tabella `text_config` + `UNIQUE` su `server_config.nome_configurazione` |
| `V5__testi_istanza.sql` | disclaimer e testi con riferimenti espliciti |
| `V6__tx_hash_lunghezza.sql` | `payments.tx_hash` da `varchar(66)` a `varchar(128)` |
| `V7__flag_batch_abbonamenti.sql` | chiave `BATCH_ABBONAMENTI_ABILITATO` in `server_config` |
| `V8__account_stripe_neutri_e_backup.sql` | `stripe_account` da `LILLO`/`DANNY` a `PRIMARIO`/`SECONDARIO`; rinomina la chiave di V7 in `BATCH_VERIFICA_ABBONAMENTI`; aggiunge `BACKUP_DB_ABILITATO` e le quattro `RUOLO_*` |

### Come si cambiano i valori di un `ENUM` senza perdere i dati

`V8` doveva rinominare i valori di `payments.stripe_account` e `track_prelievi.stripe_account`.
Un solo `MODIFY COLUMN` verso i nuovi valori avrebbe messo a `NULL` tutte le righe esistenti,
perché per MySQL `'LILLO'` non appartiene più al dominio. Servono tre passaggi:

```sql
-- 1. si estende l'ENUM a vecchi + nuovi
ALTER TABLE payments MODIFY COLUMN stripe_account ENUM('LILLO','DANNY','PRIMARIO','SECONDARIO') DEFAULT NULL;
-- 2. si migrano i dati
UPDATE payments SET stripe_account = 'PRIMARIO' WHERE stripe_account = 'LILLO';
-- 3. si restringe ai soli nuovi
ALTER TABLE payments MODIFY COLUMN stripe_account ENUM('PRIMARIO','SECONDARIO') DEFAULT NULL;
```

## La collation va dichiarata: non ereditarla dal database

`V1__baseline_schema.sql` **non dichiara charset né collation**: ogni tabella eredita il default del
database, che cambia da un'installazione all'altra. Lo schema di produzione è
**`utf8mb4_unicode_ci`** (il database fu creato così), mentre MySQL 8+ propone
`utf8mb4_0900_ai_ci` per un database nuovo.

Conseguenza verificata il 2026-08-12, importando il dump di produzione in un database creato con
`CREATE DATABASE discord_db` secco:

```
Error Code: 3780
Referencing column 'discord_id' and referenced column 'discord_id' in foreign key
constraint 'referral_pendenti_ibfk_1' are incompatible.
```

MySQL rifiuta una chiave esterna fra due `varchar(64)` con collation diverse. La tabella
`referral_pendenti` nasceva `utf8mb4_0900_ai_ci` per default, `users` era `utf8mb4_unicode_ci`.

**Regola:** ogni migration che crea una tabella con una chiave esterna verso una colonna testuale
dichiara `COLLATE utf8mb4_unicode_ci` sulla colonna e `DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci` sulla tabella. Così la migration si comporta allo stesso modo ovunque,
qualunque sia il default del database ospite — che in produzione, fra l'altro, non è noto: il dump
contiene le tabelle ma non l'istruzione `CREATE DATABASE`.

`docker-compose.yml` avvia MySQL con `--collation-server=utf8mb4_unicode_ci`, così l'ambiente
locale ricreato da zero nasce allineato.

> [!note] Se una migration fallisce a metà
> MySQL non annulla le DDL: la parte già eseguita resta. Nel caso sopra `V3` aveva aggiunto
> `referral_agent.utilizzi` prima di fermarsi sulla `CREATE TABLE`. Per riprovare servono
> entrambe le cose: `DELETE FROM flyway_schema_history WHERE success = 0` e l'annullamento
> manuale di quanto era passato.

## Due divergenze fra sviluppo e produzione

Emerse confrontando lo schema reale (dump del 2026-08-11) con quello di sviluppo:

| Colonna | Sviluppo | Produzione | Conseguenza |
|---|---|---|---|
| `payments.fee_pending` | `bit(1)` | `tinyint(1)` | nessuna: Hibernate accetta entrambi come booleano, la produzione gira già con `validate` |
| `payments.tx_hash` | `varchar(66)` | `varchar(128)` | ⚠️ **rilevante** — vedi sotto |

La seconda era un difetto latente. La baseline dichiara `varchar(66)`, misura giusta per gli hash
Arbitrum (`0x` + 64 esadecimali), ma i pagamenti Stripe salvano un hash **sintetico**
`UUID_email` che in produzione arriva a **72 caratteri**. In produzione la colonna era stata
allargata a mano e il problema non si vedeva; su un database creato da zero con le sole migration
ogni pagamento Stripe sarebbe fallito con «Data too long for column 'tx_hash'». La migration `V6`
allinea le due situazioni.

## Tabelle non mappate

`user_account` (24 righe in produzione) **non corrisponde ad alcuna entità JPA**: è un residuo.
Hibernate con `validate` ignora le tabelle in più, quindi non causa problemi, ma non è documentata
altrove perché nessun codice la usa.

## Le regole di migrazione (con Flyway, dal 2026-07-25)

`ddl-auto` è **`validate`** in tutti i profili: Hibernate **verifica** lo schema all'avvio e **fa
fallire il boot** se non corrisponde alle entità. Lo schema lo costruisce Flyway.

1. **Ogni modifica al database è una nuova migration** `V<n>__descrizione.sql` in
   `discord-access-persistence/src/main/resources/db/migration/`. Si applica **da sé** al riavvio: non
   servono più `ALTER TABLE` manuali prima del deploy.
2. **Le migration già applicate non si modificano mai.** Il checksum cambierebbe e Flyway bloccherebbe
   l'avvio. Serve una correzione? Un'altra migration.
3. **Baseline fissata a `V2`** (`baseline-on-migrate: true`, `baseline-version: 2`): in produzione, dove
   schema e dati esistono già, `V1__baseline_schema.sql` e `V2__dati_iniziali.sql` vengono **marcate**
   come applicate senza essere eseguite; da `V3` in avanti si applicano normalmente. Su un database
   vuoto (sviluppo) girano tutte dalla V1.
4. **Gli enum Java devono essere `ENUM` nativi MySQL, non `VARCHAR`.** Hibernate 6 li mappa così: una
   colonna `VARCHAR` produce
   `Schema-validation: wrong column type ... found [varchar], but expecting [enum]` e l'app non parte.
5. Lo storico delle applicazioni vive nella tabella **`flyway_schema_history`**, creata alla prima
   esecuzione.

> ℹ️ Flyway 9.22.3 (versione gestita da Spring Boot 3.2.3) dichiara il supporto fino a MySQL 8: con
> MySQL 9.x emette all'avvio un **warning** «Flyway upgrade recommended: MySQL 9.3 is newer than this
> version of Flyway» e prosegue. Non è un errore — verificato in locale il 2026-07-26.
> Un override a Flyway 10/11 non è compatibile con la `FlywayAutoConfiguration` di Spring Boot 3.2.

Prima applicazione in locale (2026-07-26): Flyway ha creato `flyway_schema_history` con un'unica riga
`version 2`, `type BASELINE`, `success 1`, senza eseguire V1 e V2 — e la validazione Hibernate è
passata, confermando che schema e entità erano già allineati.

## Storia / claim superate

> [!warning] Sostituito da una modifica al codice
> Fino al 2026-07-25 lo schema viveva in `sql/create_table.sql` e i dati in `sql/insert.sql`: ogni
> `ALTER TABLE` andava eseguito **a mano in produzione prima del deploy** e `insert.sql` non girava
> mai in produzione. In locale `ddl-auto` era `update`. **Ora vale Flyway**, come descritto sopra; i
> due file sono stati eliminati (la loro storia resta in git, il loro contenuto è in `V1` e `V2`).

## Debito noto sui vincoli

- `payments.stripe_session_id` **non è `UNIQUE`**: l'idempotenza dei webhook supporter è solo
  applicativa. Introdurre il vincolo richiede prima di migrare le righe crypto da `""` a `NULL`
  ([[Idempotenza dei webhook]]).
- `server_config.nome_configurazione` **non è `UNIQUE`**: doppie chiavi possibili
  ([[Configurazione di server]]).
- `snapshot_bilancio.metodo_pagamento` non contempla `STRIPE` ([[Enum di dominio]]).

## Ambiente locale

`docker-compose.yml` avvia MySQL sulla porta **3307** (esterna) e crea **solo il database vuoto**:
schema e dati li applica Flyway all'avvio dell'applicazione. Il mount di `./sql` in
`docker-entrypoint-initdb.d` è stato rimosso. Vedi [[Ambienti e profili Spring]].

## Voci correlate
- [[Entita]]
- [[Deploy e CI-CD]]
- [[Backup del database]]
