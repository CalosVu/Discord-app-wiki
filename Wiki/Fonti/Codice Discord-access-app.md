---
tipo: fonte
titolo: Codice Discord-access-app
alias: [repo applicativo, sorgente]
tag: [fonte/codice]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Codice Discord-access-app

Il repository applicativo: **fonte di rango 1**, la più attendibile della wiki (CLAUDE.md §3).

## Identificazione

- **Percorso locale:** `${DISCORD_APP_SRC}` (variabile in `.paths`).
- **Branch documentato:** `main` — è quello che viene **deployato automaticamente in produzione**
  ad ogni push (vedi [[Deploy e CI-CD]]). Gli altri branch non sono coperti da questa wiki.
- **Dimensione all'ingest:** 126 file `.java`, ~14.800 righe, 5 moduli Maven.
- **Stack:** Java 21, Spring Boot 3.5.16 (Tomcat 10.1.55, Spring Framework 6.2, Security 6.5),
  JDA 5.5.1, driver `mysql-connector-j` 9.2.0, Stripe SDK 29.4.0, Web3j 5.0.0, AWS SDK v2 (S3/R2),
  Flyway 11, springdoc 2.9.0, Lombok, MapStruct 1.6.3.
- ⚠️ Il **server** MySQL è una cosa distinta dal driver: in locale il container usa `mysql:latest`
  (verificato **9.3** il 2026-07-26). Il `9.2.0` che si trova nella documentazione è la versione del
  driver JDBC, non del database.

## Perché è di rango 1

Push su `main` = build Maven + deploy del JAR sul server + restart del servizio systemd. Quello che
c'è su `main` **è** ciò che gira. Nessun documento può contraddirlo: se lo fa, il documento è
superato.

## Contenuti chiave

| Area | Punto d'ingresso nel codice |
|---|---|
| Avvio bot e listener | `botDiscord/DiscordBot.java` → [[Bot Discord]] |
| Comandi in DM | `botDiscord/CommandBot.java` (1.321 righe), `MasterclassBot.java` |
| Routing eventi | `botDiscord/listener/` (5 listener) |
| Pagamenti crypto | `service/payments/member/CryptoPaymentService.java` (769 righe) |
| Pagamenti Stripe | `service/payments/member/` + `controller/WebhookController.java` |
| Masterclass | `service/payments/masterclass/` (strategy connect/direct) |
| Batch | `batch/VerificaAbbonamentiBatch.java` |
| Config runtime | `service/LoadConfigurationService.java` + tabella `server_config` |
| Schema DB | migration Flyway in `discord-access-persistence/src/main/resources/db/migration/` |
| Configurazione | `discord-access-api/src/main/resources/application*.yml` |
| CI/CD | `.github/workflows/deploy.yml` |

## Pagine wiki derivate

Praticamente tutte. In particolare: tutte le pagine di [[Entita]], [[Concetti]], [[Moduli]],
[[Tassonomie]] e [[Config-Credenziali]].

## Note di ingest

- Le **migration Flyway** sono considerate rango 2: versionate col codice e applicate automaticamente
  all'avvio. Dal 2026-07-25 sostituiscono `sql/create_table.sql` e `sql/insert.sql`, che sono stati
  eliminati (vedi [[Schema del database]]).
- Il **file `.env`** non è nel repo (gitignored): i nomi delle variabili sono ricavati da
  `application.yml`, i valori non compaiono mai nella wiki (CLAUDE.md §5.6).
- I **test JUnit** sono stati letti come conferma della logica, non documentati caso per caso
  (voce nel debito di ingest).

## Voci correlate
- [[Fonti]]
- [[Architettura dei moduli Maven]]
