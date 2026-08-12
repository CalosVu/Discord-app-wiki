---
tipo: log
titolo: Log
creato: 2026-07-25
aggiornato: 2026-07-25
---

# Log — diario della wiki (append-only)

> File di servizio del manutentore, in `meta/` (nascosto al lettore via `userIgnoreFilters`).
> Registro cronologico di cosa è successo e quando (CLAUDE.md §7). **Append-only.**
> Formato voce: `## [YYYY-MM-DD] <tipo> | <titolo>` — tipo ∈ `ingest | query | lint | manutenzione | intervento`.

## [2026-07-25] manutenzione | Inizializzazione wiki
Wiki creata con `/wiki-init esistente` + modulo interventi. Schema in `CLAUDE.md`, vault in `Wiki/`.
Il vault vive in un repo dedicato (`Discord-app-wiki`), separato dal repo del codice: i percorsi
esterni (codice, documentazione) sono in `.paths`. Installati anche due comandi slash nel repo del
codice (`/wiki-chiedi`, `/wiki-aggiorna`) per aggiornare la wiki durante lo sviluppo.

## [2026-07-25] ingest | Codice sorgente su main — ingest completo
Ingerito l'intero codice sorgente di `Discord-access-app` (branch `main`, ~14.800 righe Java su 5
moduli Maven) più gli script `sql/create_table.sql` e `sql/insert.sql`. Prodotte le pagine di
[[Entita]], [[Concetti]], [[Moduli]], [[Tassonomie]] e [[Config-Credenziali]].
Fonte: [[Codice Discord-access-app]]. Non sono stati analizzati i branch feature non mergiati
(scelta esplicita in fase di init: si documenta ciò che è in produzione).

## [2026-07-25] ingest | Documentazione tecnica di progetto
Ingeriti gli 8 documenti `.md` alla radice della cartella documentazione:
[[DOC_PROGETTO]], [[Integrazione sistema pagamenti]], [[Piano sviluppo masterclass]],
[[Piano sviluppo doppio Stripe]], [[Guida di deployment]], [[Runbook cambio dominio]],
[[Guida SSL e DNS]], [[Guida Stripe CLI]].
Rilevate divergenze rilevanti tra i due documenti più vecchi ([[DOC_PROGETTO]],
[[Integrazione sistema pagamenti]]) e il codice attuale: annotate nelle rispettive pagine-fonte e
nelle sezioni `## Storia / claim superate` delle pagine di contenuto, applicando la gerarchia
delle fonti (CLAUDE.md §3).
Non ingerite le sottocartelle non tecniche (media, marketing, loghi, live, indicatori, fatture) né
il dump DB: registrate in `meta/aperture-ingest.md`.

## [2026-07-25] intervento | Referral non attribuito e Fix Referral inefficace
Aperta la pagina-intervento [[2026-07-25 Referral non attribuito e Fix Referral inefficace]] con
l'analisi a codice: il comando *Fix Referral* non puo' aggiornare nessun utente (insiemi disgiunti fra
`getUsersWithoutValidInvite` e la guardia in `getReferralForUser`), il tracciamento inviti vive solo in
RAM, e l'attribuzione viene scritta solo all'accettazione del disclaimer. Ipotesi aggiuntiva: race sul
contatore `uses` letto dentro `onGuildMemberJoin`. Nessuna modifica al codice applicata: piano in
attesa di approvazione. Branch di lavoro: `feature/versioneProdotto`.

## [2026-07-25] intervento | Fase 1 - Flyway per il versionamento dello schema
Introdotto Flyway in `discord-access-persistence` (versione gestita da Spring Boot 3.2.3, nessun
override). `V1__baseline_schema.sql` = ex `sql/create_table.sql`, `V2__dati_iniziali.sql` = ex
`sql/insert.sql`, copiati byte-per-byte e verificati con `diff`. Baseline a V2, `ddl-auto: validate`
in tutti i profili, mount `./sql` rimosso dai due docker-compose, cartella `sql/` eliminata.
Pagine aggiornate: [[Schema del database]] (nuove regole + sezione claim superate),
[[Deploy e CI-CD]], [[Ambienti e profili Spring]], [[Codice Discord-access-app]], [[Fonti]].
Aggiornati anche `CLAUDE.md` del repo del codice e la memoria di progetto sulla regola SQL.
Fase 1 di [[2026-07-25 Referral non attribuito e Fix Referral inefficace]]. Build a carico dell'utente.

## [2026-07-26] intervento | Fase 1 Flyway - verifica in locale
Prima esecuzione verificata: `flyway_schema_history` creata con una sola riga (version 2, type
BASELINE, success 1), nessuna migration eseguita, validazione Hibernate passata (l'avvio ha superato
la creazione dell'EntityManagerFactory arrivando a JDA e Tomcat). Warning atteso
"MySQL 9.3 is newer than this version of Flyway". Corretta in [[Codice Discord-access-app]] e
[[Schema del database]] la confusione fra versione del server MySQL (9.3, `mysql:latest`) e del driver
JDBC (`mysql-connector-j` 9.2.0).

## [2026-07-26] intervento | Fase 2 - Censimento dell'utente all'ingresso nel server
Nuovo `CensimentoUtenteService` (in `service/management/`) con `censisciSeAssente`, idempotente e
unico punto di creazione di `users` nel codice applicativo. `DisclaimerListener` riscritto: censimento
+ ruolo GUEST + benvenuto su `onGuildMemberJoin`; su `onMessageReactionAdd` solo registrazione
dell'accettazione, collegamento a `users.disclaimer_id` e ultimo tentativo di assegnazione del
referral. Ruolo e benvenuto non sono piu' subordinati all'esistenza del canale disclaimer. Rimossi da
`DisclaimerListener` due campi non piu' usati (`CatalogoServiziRepository`, `LoadConfigurationService`).
Nessuna migration necessaria: le colonne coinvolte erano gia' nullable.
Aggiunto `CensimentoUtenteServiceTest` (5 casi: valori iniziali, idempotenza, piano mancante, referral
noto, referral non sovrascritto).
Pagine aggiornate con sezioni di claim superate: [[Utente]], [[Onboarding e disclaimer]],
[[Accettazione disclaimer]]. Fase 2 di
[[2026-07-25 Referral non attribuito e Fix Referral inefficace]]. Build e test a carico dell'utente.

## [2026-07-26] intervento | Fase 3 - Attribuzione referral persistita e comando !SyncReferral
Migration `V3`: colonna `referral_agent.utilizzi` (baseline degli utilizzi gia' attribuiti) e tabella
`referral_pendenti`. Nuovi: entita' `ReferralPendente`, enum `MotivoPendenza`, repository,
`AttribuzioneReferralService` (indipendente da JDA per essere testabile), metodi
`DiscordService.recuperaUtilizziInviti` e `mappaUtilizzi`. `InviteListener` riscritto con retry a
2/5/15 secondi. `CommandBot`: rimossa la voce *Fix Referral* (menu da 9 a 8 voci) e aggiunto il flusso
`!SyncReferral` con lista, esito previsto e conferma a pulsanti. Eliminato `InviteUsageService`.
Invariante centrale: i contatori si incrementano SOLO sulle attribuzioni riuscite, cosi' la differenza
resta recuperabile. 13 test in `AttribuzioneReferralServiceTest`, incluso quello sull'invariante.
Pagine: nuova [[Referral pendente]]; aggiornate [[Sistema referral e commissioni]] (riscritta),
[[Referral agent]], [[Comandi admin]], [[Schema del database]], [[Enum di dominio]],
[[Onboarding e disclaimer]], [[Entita]], [[index]] e la pagina-intervento.

## [2026-07-31] manutenzione | Il prodotto prende il nome VuPass
Il prodotto si chiama ora **VuPass**, della famiglia VuTradingFarm (con VuTracker e VuMarkets).
Sostituisce `Discord-access-app` come NOME DEL PRODOTTO; il repository git e gli artefatti Maven
conservano il nome storico. Aggiornati: `CLAUDE.md` (titolo e §1), [[Panoramica]], `index.md`,
`README.md` del repo wiki e `CLAUDE.md` del repo del codice.
Distinzione resa esplicita in tutti i punti toccati: **VuPass** e' il software, **InWestors** e' la
community Discord che ne ospita la prima istanza. Le due occorrenze di "InWestors" nel codice
(`Constants.txtBenvenuto` e `txtDisclaimer`) sono messaggi rivolti agli utenti della community e
NON sono state modificate.
Colta l'occasione per allineare `index.md`: menu admin da nove a otto voci e stato dell'intervento
referral da "in analisi" a "implementato".

## [2026-08-12] intervento | Collaudo delle migration sul dump di produzione
Importato il dump di produzione dell'11/08/2026 in un database separato e applicate V3, V4, V5:
tutte riuscite. Dati intatti (116 utenti, 205 pagamenti, 157 inviti, 47 prelievi, 14 configurazioni).
Il confronto dello schema migrato con quello di sviluppo ha rivelato due divergenze, documentate in
[[Schema del database]]: `fee_pending` (bit vs tinyint, innocua) e soprattutto `tx_hash`
varchar(66) nella baseline contro varchar(128) in produzione. I pagamenti Stripe salvano un hash
sintetico `UUID_email` lungo fino a 72 caratteri: su un database creato da zero ogni pagamento
Stripe sarebbe fallito. Aggiunta la migration `V6__tx_hash_lunghezza.sql`, collaudata.
Trovato anche che i backup automatici erano NON ripristinabili: `DatabaseBackupService` univa lo
stderr di mysqldump allo stdout, inserendo warning ed errori dentro il file .sql. Corretto
(stderr su file .log separato, rimosso `--compress` deprecato e inutile su server locale).
Aggiornata [[Tabella server_config]]: in produzione sono 14 configurazioni, non 9, di cui cinque
non lette da alcun codice. Documentata la tabella `user_account`, priva di entita' corrispondente.
