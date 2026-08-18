---
tipo: tassonomia
titolo: Schema del database
alias: [database, tabelle, DDL, migrazioni]
tag: [dominio/database]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Schema del database

Le tabelle MySQL del sistema, le relazioni e — soprattutto — le **regole per modificarle** senza
rompere la produzione.

Database: `discord_db`. Schema e dati sono versionati con **Flyway** in
`discord-access-persistence/src/main/resources/db/migration/`.

## Le tabelle

Dal 2026-08-13 il nome è `<dominio>_<cosa>`, in italiano: le tabelle di uno stesso ambito stanno
vicine in ordine alfabetico, e non convivono più due lingue (`users` accanto a `utenti_lifetime`,
`payments` accanto a `pagamenti_masterclass`). Il rename è la migration `V11`.

| Tabella | Nome precedente | Entità | Pagina |
|---|---|---|---|
| `cfg_server` | `server_config` | `ServerConfig` | [[Configurazione di server]] |
| `cfg_testi` | `text_config` | `TextConfig` | [[Tabella cfg_server]] |
| `cfg_server_obbligatorie` | — | `ConfigObbligatoria` | [[Tabella cfg_server]] |
| `cfg_piani` | `catalogo_servizi` → `cfg_catalogo_servizi` | `Piano` | [[Catalogo servizi]] |
| `cfg_promo` | *(era nella stessa tabella dei piani)* | `Promo` | [[Promozioni temporali]] |
| `utenti` | `users` | `User` | [[Utente]] |
| `utenti_lifetime` | — | `UtentiLifetime` | [[Utente lifetime]] |
| `utenti_disclaimer` | `disclaimer_accept` | `DisclaimerAccept` | [[Accettazione disclaimer]] |
| `pagamenti` | `payments` | `Payments` | [[Pagamento]] |
| `pagamenti_prelievi` | `track_prelievi` | `TrackPrelievi` | [[Prelievo]] |
| `pagamenti_utenti_verifiche` | `user_verify_transaction` | `UserVerifyTransaction` | [[Tentativo di verifica transazione]] |
| `referral_utenti` | `referral_agent` | `ReferralAgent` | [[Referral agent]] |
| `referral_agenti` | `agenti` | `Agente` | [[Agente]] |
| `referral_commissioni` | `commissioni_pagamento` | `CommissionePagamento` | [[Commissione pagamento]] |
| `referral_pendenti` | — | `ReferralPendente` | [[Referral pendente]] |
| `masterclass` | — | `Masterclass` | [[Masterclass]] |
| `masterclass_relatori` | `relatori` | `Relatore` | [[Relatore]] |
| `masterclass_pagamenti` | `pagamenti_masterclass` | `PagamentoMasterclass` | [[Pagamento masterclass]] |
| `sys_log_server` | `log_service` | `LogServer` | [[Log operativo]] |
| `affiliazioni_exchange` | `user_account` | — (non mappata) | vedi in fondo |
| `flyway_schema_history` | — | — | storico delle migration, gestita da Flyway |

`flyway_schema_history` non è stata rinominata di proposito: Flyway la cerca per nome, e cambiarlo
richiederebbe di riconfigurarlo senza alcun guadagno.

⚠️ **I nomi di vincoli e indici sono rimasti quelli vecchi**: dopo il rename una chiave esterna si
chiama ancora `referral_pendenti_ibfk_1`. Non compaiono nell'uso quotidiano e rinominarli avrebbe
richiesto di ricrearli uno per uno.

> [!warning] Eliminata: `snapshot_bilancio`
> Rimossa da `V11` insieme a entità, repository e batch. Non è mai stata scritta: la classe
> `SnapshotBilancioBatch` era un guscio vuoto con `@Scheduled`, query e repository interamente
> commentati. Zero righe in produzione. Vedi [[Snapshot bilancio]].

## Le relazioni portanti

```
cfg_server ───── cfg_server_obbligatorie   (FK ON DELETE RESTRICT: le config non si cancellano)

referral_utenti ─┬──< utenti >──── cfg_piani              (piano_applicato_id)
                 │       │  │
                 │       │  └──── utenti_disclaimer       (1-a-1)
                 │       │  └──── pagamenti               (ultimo pagamento, 1-a-1)
                 │       ├──< referral_agenti ──< referral_commissioni >── pagamenti
                 │       ├──< masterclass_relatori ──< masterclass ──< masterclass_pagamenti
                 │       └──< pagamenti_utenti_verifiche
                 └──< cfg_promo               (promo riservata a un referral)
```

Particolarità: `pagamenti` ha **due** FK verso `utenti` — su `user_id` e su `discord_id`.
`referral_pendenti` ha una FK verso `utenti.discord_id` con vincolo di unicità: una riga per utente.

`sys_log_server` **non ha chiavi esterne**, di proposito: un log deve restare leggibile anche se
l'utente viene cancellato. La vecchia `log_service` puntava a `disclaimer_accept`, il che rendeva
registrabile un evento solo per chi aveva accettato il disclaimer ([[Log operativo]]).

## Le migration applicate

| Versione | Contenuto |
|---|---|
| `V1__baseline_schema.sql` | schema di base (ex `sql/create_table.sql`) |
| `V2__dati_iniziali.sql` | dati di bootstrap (ex `sql/insert.sql`) |
| `V3__referral_utilizzi_e_pendenti.sql` | colonna `referral_agent.utilizzi` + tabella `referral_pendenti` |
| `V4__text_config.sql` | tabella `cfg_testi` + `UNIQUE` su `server_config.nome_configurazione` |
| `V5__testi_istanza.sql` | disclaimer e testi con riferimenti espliciti |
| `V6__tx_hash_lunghezza.sql` | `payments.tx_hash` da `varchar(66)` a `varchar(128)` |
| `V7__flag_batch_abbonamenti.sql` | chiave `BATCH_ABBONAMENTI_ABILITATO` in `cfg_server` |
| `V8__account_stripe_neutri_e_backup.sql` | `stripe_account` da `LILLO`/`DANNY` a `PRIMARIO`/`SECONDARIO`; rinomina la chiave di V7 in `BATCH_VERIFICA_ABBONAMENTI`; aggiunge `BACKUP_DB_ABILITATO` e le cinque `RUOLO_*` |
| `V9__pulizia_config_inutilizzate.sql` | elimina `PERCENTUALE_COMMISSIONI_STRIPE` e `QUOTA_FISSA_COMM_STRIPE`, che nessun codice legge |
| `V10__percentuale_stripe_secondario.sql` | aggiunge `PERCENTUALE_STRIPE_SECONDARIO` ([[Bilanciamento degli account Stripe]]) |
| `V11__rinomina_tabelle_e_log.sql` | rinomina le tabelle per dominio, elimina `snapshot_bilancio`, sostituisce `log_service` con `sys_log_server` |
| `V12__utenti_pulizia_colonne_morte.sql` | elimina `utenti.abilitato` e `utenti.disclaimer_id`, scritte e mai lette |
| `V13__utenti_disclaimer_reazione.sql` | `discord_id` a `varchar(64)`; `data_accettazione` → `data_ultima_reazione` |
| `V14__campi_uniformi_pagamenti_utenti.sql` | nomi e ordine dei campi di `pagamenti`, `pagamenti_prelievi`, `pagamenti_utenti_verifiche`, `utenti` |
| `V15__referral_utenti_pulizia.sql` | elimina `commissione_percentuale`, `limite_utilizzi`, `data_attivazione`; `descrizione_referral` → `tipo` (`ENUM`) |
| `V16__referral_agenti_audit.sql` | `data_inserimento` → `data_update` e riordino delle colonne |
| `V17__commissioni_importo_congelato.sql` | `referral_commissioni.importo_commissione`: l'importo non viene più ricalcolato a ogni lettura |
| `V18__masterclass_audit.sql` | `masterclass.data_creazione` → `data_update` |
| `V19__masterclass_relatori_audit.sql` | `masterclass_relatori.data_inserimento` → `data_update`; commento su `stripe_account_id` |
| `V20__masterclass_pagamenti_audit.sql` | `masterclass_pagamenti.created_at` → `data_update` |
| `V21__pionieri_a_numero_chiuso.sql` | `utenti.pioniere_storico`, `PIONIERI_ASSEGNATI`, `PIONIERI_ABILITATI` ([[Membri pionieri]]) |
| `V22__promo_destinatari.sql` | `destinatari` come `ENUM` a tre valori al posto di un flag |
| `V23__piani_e_promo_separati.sql` | `cfg_catalogo_servizi` divisa in `cfg_piani` e `cfg_promo`; FK di `utenti` sui soli piani |
| `V24__cfg_testi_pulizia.sql` | `data_modifica` → `data_update`; via il testo `accesso.revocato`, irraggiungibile |
| `V25__conservazione_log.sql` | `LOG_CONSERVAZIONE_GIORNI` ([[Log operativo]]) |
| `V26__interruttore_comandi_bot.sql` | `COMANDI_BOT_ABILITATI` + testo `bot.disabilitato` |
| `V27__utenti_nome_visualizzato.sql` | `utenti.nome_visualizzato`, il nome della lista membri ([[Utente]]) |
| `V28__finestra_verifica_crypto.sql` | `VERIFICA_CRYPTO_FINESTRA_ORE`: chiude il riscatto di transazioni storiche ([[Pagamenti crypto Arbitrum]]) |
| `V29__cfg_server_protetta_da_delete.sql` | `cfg_server_obbligatorie`: la FK impedisce di cancellare le configurazioni, e ne dichiara i tipi |
| `V30__email_cliente_fuori_da_transaction_hash.sql` | `pagamenti.email_cliente`: l'email esce dall'hash sintetico e prende una colonna indicizzata ([[Pagamento]]) |

> [!warning] `V29` insegna una cosa su MySQL
> Il primo tentativo usava un trigger `BEFORE DELETE`. MySQL lo **rifiuta** con l'errore `1419` se il
> binary logging è attivo e l'utente non ha `SUPER` — quindi sia in locale sia in produzione.
>
> Peggio: la migration era già passata oltre l'`UPDATE` iniziale quando il `CREATE TRIGGER` è
> fallito, lasciando il database a metà e Flyway con una migration marcata come fallita, che blocca
> ogni avvio successivo. È servito rimuovere quella riga da `flyway_schema_history` a mano.
>
> **Regola che ne deriva: niente trigger nelle migration.** Per i vincoli si usano chiavi esterne, che
> non richiedono privilegi speciali e valgono per tutti gli utenti, root compreso.

### Colonne vuote che NON sono residui

Durante la revisione sono state eliminate diverse colonne perché nessuno le leggeva. Il criterio
non è però «è vuota, quindi va via»: conta se **esiste un percorso di codice che può valorizzarla**.

`masterclass_relatori.stripe_account_id` è `NULL` sull'unico relatore esistente, ma resta: serve al
modello di pagamento **Connect**, congelato e selezionabile a runtime con
`MASTERCLASS_PAYMENT_MODE=connect`. Il suo codice — strategia, servizio, resolver, controller
webhook — è tutto presente e funzionante ([[Relatore]], [[Sistema masterclass]]).

La differenza con `snapshot_bilancio` o `utenti.abilitato`, eliminate, è che lì il codice era
commentato o irraggiungibile: nessuna configurazione poteva riattivarlo.

### La convenzione sui campi di audit

Prima esistevano **quattro nomi per la stessa cosa** — `created_at`, `data_creazione`,
`data_inserimento`, `data_creazione_account` — più `data_aggiornamento` e `data_modifica`
(quest'ultimo su `cfg_testi`, allineato da `V24`). Ora la
regola è una: **`data_update`**, con `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`, in
fondo alla tabella. Registra l'ultima volta che la riga è stata toccata.

Due eccezioni volute:

- **`pagamenti_utenti_verifiche` non ha audit**: `data_verifica` *è* l'evento e la riga non viene
  mai modificata. Aggiungerlo sarebbe rumore.
- **`utenti` conserva anche `data_ingresso_server`** accanto a `data_update`: quella riga cambia di
  continuo (disclaimer, pagamenti, rinnovi, degradi) e senza un campo dedicato si perderebbe
  quando l'utente è entrato nel server — dato non ricostruibile da altre fonti.

### Date che sembravano ridondanti e non lo erano

`pagamenti` ha sia `data_pagamento` sia `data_update`; `pagamenti_prelievi` sia `data_prelievo`
sia `data_update`; `masterclass_pagamenti` idem. Sembrano doppioni, ma i dati dicono il contrario:

| | Righe | Coincidono | Differiscono | Scarto max |
|---|---|---|---|---|
| `pagamenti` | 205 | 50 | **155** | ~14 ore |
| `pagamenti_prelievi` | 47 | 35 | **12** | ~61 giorni |

La prima è **quando il fatto è avvenuto** (transazione on-chain, evento Stripe, prelievo
effettivo), la seconda **quando l'applicazione lo ha saputo**. Nelle crypto l'utente paga e
verifica col bot anche molto dopo; un prelievo può essere registrato due mesi più tardi.

Su `masterclass_pagamenti` la tabella è ancora vuota, ma lo scarto è garantito dal flusso: la
riconciliazione della fee riscrive `commissione_stripe`, `importo_netto_relatore` e `fee_pending`
ore dopo l'acquisto ([[Pagamento masterclass]]).

### ⚠️ Rinominare un campo ha tre superfici d'impatto, non una

Le tabelle si rinominano senza toccare le query, perché JPQL usa i nomi delle *entità*. **I campi
no**: rinominarne uno rompe anche le query, e in modi che il compilatore non vede.

| Superficie | Quando si scopre l'errore |
|---|---|
| getter, setter, builder | compilazione |
| `@Query` JPQL che nomina l'attributo | **avvio dell'applicazione** |
| derived query (`findByPaymentMethod`) | avvio, e cambia il nome del metodo |

Successo con `V14`: dopo la build verde l'applicazione non partiva con
`Could not resolve attribute 'paymentMethod' of 'Payments'`. Le `@Query` sono stringhe e le
derived query sono convenzioni sui nomi: `mvn` non le controlla.

Peggio, **l'avvio si ferma al primo repository che fallisce**: correggendo solo ciò che l'eccezione
nomina si scopre l'errore successivo al riavvio dopo, uno alla volta. Il modo efficiente è
elencare in un colpo tutti gli attributi citati in tutte le `@Query` e tutte le derived query del
progetto, e confrontarli con i campi rinominati.

### Rinominare tabelle senza rompere le chiavi esterne

`V11` usa **un solo** `RENAME TABLE` con tutte le tabelle elencate: MySQL lo esegue in modo atomico
e aggiorna da sé le chiavi esterne che puntano alle tabelle rinominate. Farne uno per tabella
avrebbe lasciato lo schema in stati intermedi incoerenti se una fosse fallita.

Il rename è stato praticabile perché nel progetto **non esiste una sola query nativa**: tutte le
interrogazioni sono JPQL, che usa i nomi delle *entità*, non delle tabelle. L'unico punto da
aggiornare erano le annotazioni `@Table`.

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
`referral_pendenti` nasceva `utf8mb4_0900_ai_ci` per default, `utenti` era `utf8mb4_unicode_ci`.

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

`affiliazioni_exchange` (24 righe in produzione) **non corrisponde ad alcuna entità JPA** e nessuna riga di
codice la nomina — ma **non è un residuo**: è un registro di gestione interna, compilato a mano.

Raccoglie gli utenti che hanno aperto un account sugli **exchange con cui esiste un'affiliazione**,
con il loro username TradingView e gli indicatori attualmente attivi. Serve a sapere a chi
spettano gli indicatori e a chi è riconducibile una commissione di affiliazione.

L'ipotesi è di gestirla un domani da interfaccia; finché non accade resta alimentata manualmente.
Hibernate con `validate` ignora le tabelle in più, quindi la sua presenza non disturba l'avvio.

Revisionata il 2026-08-16 e **lasciata volutamente com'è**: nessuna entità, nessuna migration.
Finché la si compila a mano, mapparla aggiungerebbe solo codice da mantenere.

| Colonna | Contenuto |
|---|---|
| `user_id` | riferimento all'[[Utente]], `UNIQUE`. **Senza chiave esterna**: come per il [[Log operativo]], il registro deve sopravvivere alla cancellazione di un utente |
| `username` | snapshot al momento dell'inserimento |
| `blofin`, `mexc` | UID sull'exchange, numerici |
| `tradingview` | account TradingView a cui assegnare gli indicatori |
| `trigger`, `flow_x`, `edge_reversal` | indicatori assegnati, uno per prodotto |
| `indicators` | **non è la somma dei tre**: 10 righe su 24 hanno `indicators = 1` e nessun indicatore specifico attivo. Sono due informazioni diverse, e chi lo eliminasse come ridondante perderebbe quelle dieci |

Verificato il 2026-08-16: i 24 `user_id` puntano tutti a utenti esistenti, nessun riferimento
orfano.

> [!warning] `trigger` è una parola riservata SQL
> `SELECT trigger FROM affiliazioni_exchange` **è un errore di sintassi**: serve `` `trigger` `` con
> i backtick. Oggi non fa danni perché nessun codice tocca la tabella, ma il giorno che la si
> mappasse in JPA, Hibernate genererebbe SQL non quotato e l'applicazione non partirebbe — servirebbe
> ``@Column(name = "`trigger`")``.
>
> Rinominarla oggi costerebbe nulla; la scelta di lasciarla è consapevole, non una svista.

⚠️ **Non cancellarla** durante le pulizie dello schema: l'assenza di riferimenti nel codice la fa
sembrare orfana, ma i dati che contiene non sono ricostruibili da nessun'altra parte.

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

> ℹ️ Flyway 11 (versione gestita da Spring Boot 3.5.16) dichiara il supporto fino a MySQL 8.1: con
> MySQL 9.x emette all'avvio un **warning** «Flyway upgrade recommended: MySQL 9.3 is newer than this
> version of Flyway» e prosegue. Non è un errore — il warning c'era anche con Flyway 9.22.3 e resta
> identico dopo l'aggiornamento (verificato in locale il 2026-08-18).
> Dalla 10 il supporto MySQL vive nell'artifact separato **`flyway-mysql`**: senza quella dipendenza
> l'avvio fallisce. I checksum delle migration già applicate non cambiano passando dalla 9 alla 11.

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
