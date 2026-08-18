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

I profili dell'applicazione e cosa cambia in ciascuno.

Il profilo attivo viene da `SPRING_PROFILES_ACTIVE`, con default **`dev`**. In produzione lo impone
il servizio systemd (`discord-bot.service:13`).

## Le differenze che contano

| Aspetto | `dev` | `prod` |
|---|---|---|
| `ddl-auto` | `validate` | `validate` |
| Indirizzo di ascolto | `0.0.0.0` | **`127.0.0.1`** |
| Porta MySQL tipica | 3307 (Docker locale) | 3306 |
| Swagger UI | attivo | **disabilitato** |
| Pool Hikari | default | max 10, min idle 5 |
| Shutdown | immediato | `graceful` |
| Log Hibernate | `ERROR` | `WARN` |

> [!info] I profili sono due, non tre
> `application-docker.yml` è stato **eliminato il 2026-08-18**. Non lo usava nessuno — nessun
> compose avvia l'applicazione, non esiste un `Dockerfile`, e il servizio in produzione imposta
> `prod` — e non avrebbe nemmeno funzionato: puntava a un database `tradingdb` che non esiste da
> nessuna parte (ovunque è `discord_db`).
>
> Il motivo per cui è stato tolto invece che corretto: non sovrascriveva nulla, quindi ereditava da
> `application.yml` log a livello `DEBUG`, **Swagger attivo** e ascolto su `0.0.0.0`. Un profilo che
> nessuno usa ma che, se avviato per sbaglio, abbassa le difese. Se un domani servirà il deploy in
> container si riscriverà insieme al `Dockerfile`.
>
> Le righe `spring.docker.compose.enabled: false` restano in `dev` e `prod`: servono a impedire che
> lo starter `spring-boot-docker-compose`, ancora fra le dipendenze, avvii da sé un compose
> all'avvio dell'applicazione.

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

## Che fine ha fatto Docker

Sul server **solo MySQL è containerizzato**: l'applicazione gira come servizio systemd sull'host, a
partire dal JAR depositato dalla pipeline ([[Deploy e CI-CD]]). Non è mai esistito un `Dockerfile`
per l'applicazione, ed è il motivo per cui il profilo `docker` era rimasto un guscio vuoto.

## Voci correlate
- [[Variabili d'ambiente]]
- [[Deploy e CI-CD]]
- [[Schema del database]]
