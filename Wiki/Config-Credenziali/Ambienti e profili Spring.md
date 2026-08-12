---
tipo: config
titolo: Ambienti e profili Spring
alias: [profili, dev, docker, prod]
tag: [dominio/configurazione, dominio/infrastruttura]
fonti: [Codice Discord-access-app, Guida di deployment]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Ambienti e profili Spring

I tre profili dell'applicazione e cosa cambia in ciascuno.

Il profilo attivo viene da `SPRING_PROFILES_ACTIVE`, con default **`dev`**.

## Le differenze che contano

| Aspetto | `dev` | `docker` | `prod` |
|---|---|---|---|
| `ddl-auto` | `validate` | `validate` | `validate` |
| Indirizzo di ascolto | `0.0.0.0` | `0.0.0.0` | **`127.0.0.1`** |
| Porta MySQL tipica | 3307 (Docker locale) | 3306 (rete Docker) | 3306 |
| Swagger UI | attivo | attivo | **disabilitato** |
| Actuator | tutto | tutto | solo `health`, `info` |
| Pool Hikari | default | default | max 10, min idle 5 |
| Shutdown | immediato | immediato | `graceful` |
| Log Hibernate | `ERROR` | — | `WARN` |

## La conseguenza più importante: `validate` in tutti i profili

Con `ddl-auto: validate` Hibernate **confronta** entità e schema all'avvio e **rifiuta di partire**
se non corrispondono. Lo schema lo costruisce **Flyway**, dalle migration nel repo. Significa che:

- una modifica alle entità senza la migration corrispondente **blocca l'avvio**, anche in locale — e
  questo è il pregio: l'errore si manifesta subito sulla macchina di sviluppo, non solo in produzione;
- un tipo di colonna sbagliato (classico: `VARCHAR` invece di `ENUM`) blocca l'applicazione;
- non servono più `ALTER TABLE` manuali prima del deploy.

Fino al 2026-07-25 in `dev` e `docker` `ddl-auto` era `update`, quindi Hibernate creava e allineava le
tabelle da sé e gli errori di schema si scoprivano solo in produzione. Vedi
[[Schema del database]] per le regole complete.

## Come si legge il file d'ambiente

Sia `dev` sia `prod` includono:

```yaml
spring:
  config:
    import: optional:file:.env
```

Il file `.env` viene cercato **nella working directory** del processo. In produzione è
`/home/deploy/discord-bot/deployment/`, ed è **anche** caricato da systemd via `EnvironmentFile`.
Essendo `optional:`, la sua assenza non blocca l'avvio: le variabili risultano semplicemente
mancanti, con errori a runtime meno leggibili.

## L'ambiente locale

`docker-compose.yml` avvia solo MySQL (`mysql:latest`), esposto sulla porta **3307** per non
collidere con installazioni locali. Crea **il database vuoto**: schema e dati iniziali li applica
Flyway al primo avvio dell'applicazione.

```bash
docker-compose up -d
mvn -pl discord-access-api spring-boot:run -Dspring-boot.run.profiles=dev
```

⚠️ Avviando in locale con un `.env` di produzione, il bot si connette al **server Discord reale** e
un pagamento di test toccherebbe dati reali. Per i test Stripe si usa la sandbox e la CLI
([[Guida Stripe CLI]]).

## Il profilo `docker`

`application-docker.yml` esiste per l'esecuzione dell'app dentro un container, con il DB raggiungibile
per nome di servizio sulla porta 3306. **In produzione non si usa**: l'app gira come servizio
systemd sull'host e solo MySQL è containerizzato ([[Deploy e CI-CD]]).

## Voci correlate
- [[Variabili d'ambiente]]
- [[Deploy e CI-CD]]
- [[Schema del database]]
