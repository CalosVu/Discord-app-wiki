---
tipo: modulo
titolo: Deploy e CI-CD
alias: [deploy, GitHub Actions, systemd, Hetzner]
tag: [dominio/infrastruttura]
fonti: [Codice Discord-access-app, Guida di deployment, Runbook cambio dominio, Guida SSL e DNS]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Deploy e CI-CD

Da `git push` alla produzione, senza passaggi manuali.

## ⚠️ Push su `main` = deploy in produzione

Il workflow GitHub Actions si attiva sui branch **`main` e `master`** (più esecuzione manuale). Ogni
push su `main` è un **rilascio in produzione**: non esiste ambiente di staging.

Prima di ogni merge su `main` conviene annotare lo **SHA dell'ultimo commit funzionante**, per poter
tornare indietro con `git revert` in caso di problemi.

## I quattro passi del workflow

1. checkout del codice;
2. JDK 21 (Temurin) con cache Maven;
3. `mvn clean package` — **i test vengono eseguiti**: un test rosso ferma il deploy. Fino al
   2026-08-18 la pipeline usava `-DskipTests` e mandava in produzione artefatti mai verificati;
4. `scp` del JAR sul server e, via `ssh`, rinomina in `app.jar` + `systemctl restart discord-bot`;
5. **attesa di 30 secondi e verifica che il servizio sia ancora vivo**: se non lo è, il passo esce
   con errore e la pipeline diventa rossa.

## Perché il deploy aspetta trenta secondi

systemd considera avviato un servizio `simple` **appena il processo parte**, molto prima che Spring
Boot arrivi in fondo — l'avvio ne impiega circa sette, di secondi, e le migration Flyway girano in
mezzo. Fino al 2026-08-19 il workflow aspettava 5 secondi e poi chiamava `systemctl status` senza
guardarne l'esito: **un'applicazione che moriva dopo lasciava la pipeline verde e il bot spento**, e
la notizia arrivava dagli utenti.

Non è teoria: è successo due volte in agosto, con `V29` (errore MySQL `1419` sui trigger) e con
`V31` (un duplicato preesistente, vedi [[Idempotenza dei webhook]]). In entrambi i casi Flyway ha
fatto fallire l'avvio **dopo** che il processo era partito.

Ora la verifica è `systemctl is-active --quiet discord-bot`, che restituisce un codice di uscita:
servizio assente → `exit 1` → pipeline rossa, con lo stato del servizio stampato nel log del
workflow.

> [!info] Perché `is-active` non ha bisogno di `sudo`
> È una lettura di stato, non un'operazione privilegiata: nessuna riga in più nel sudoers di
> `ci-deploy`. E i comandi che invece usano `sudo` restano **senza opzioni aggiuntive** — la regola
> autorizza esattamente `systemctl status discord-bot`, quindi anche un innocuo `--no-pager` lo
> renderebbe un comando non autorizzato, con sudo che chiede la password e il deploy che fallisce
> per il motivo sbagliato.

Segreti necessari nel repository: `SERVER_HOST` e `SERVER_SSH_KEY` (chiave privata dedicata,
generata sul server per l'utente `deploy`).

## Perché le action sono fissate a un SHA

Nel workflow le action non compaiono come `@v4` ma come SHA di commit, con il tag nel commento:

```yaml
uses: appleboy/ssh-action@0ff4204d59e8e51228ff73bce53f80d53301dee2  # v1.2.5
```

Un tag Git **si può spostare**, e queste action ricevono `secrets.SERVER_SSH_KEY`. Se il repository
di un'action venisse compromesso e il tag riscritto, la chiave del server uscirebbe al primo push
senza che nulla qui sia cambiato. Il SHA non si sposta.

Per aggiornarne una: si prende il SHA della nuova release
(`curl -s https://api.github.com/repos/<owner>/<repo>/git/ref/tags/<tag>`) e si aggiorna anche il
commento, altrimenti fra sei mesi nessuno sa più a quale versione corrisponda.

## Due utenti sul server: `deploy` e `ci-deploy`

Dal 2026-08-18 la pipeline **non entra più come `deploy`**.

| Utente | Chi è | Poteri |
|---|---|---|
| `deploy` | l'amministratore in carne e ossa; la chiave sta sul suo PC | gruppo `sudo` con `NOPASSWD:ALL`, gruppo `docker`, gestisce MySQL e legge i log |
| `ci-deploy` | la pipeline; la chiave sta nei **secret di GitHub** | né `sudo` generale né `docker`: solo `systemctl restart` e `status discord-bot` |

La distinzione nasce da dove vive la chiave privata. Quella di `ci-deploy` sta su GitHub, cioè fuori
dal controllo diretto: è l'unica che un attaccante può rubare senza toccare il PC dell'amministratore.
Prima la pipeline usava `deploy`, con `NOPASSWD:ALL`, e quella chiave era di fatto **la chiave di
root del server** — quindi accesso a `.env.prod`: token Discord, chiavi Stripe di quattro account,
credenziali R2 e MySQL.

In `/etc/sudoers.d/ci-deploy`:

```
ci-deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart discord-bot, /usr/bin/systemctl status discord-bot
```

Sono esattamente i due comandi che il workflow esegue.

La cartella `/home/deploy/discord-bot/deployment` appartiene a `deploy` col gruppo `ci-deploy`,
permessi `775` più il bit **setgid**: i file creati dentro ereditano il gruppo, così i due utenti non
si bloccano a vicenda. `/home/deploy` ha la `x` per gli altri, che basta ad attraversarla senza
poterne elencare il contenuto.

Per verificare l'assetto dopo una modifica:

```bash
sudo -u ci-deploy sudo -n systemctl status discord-bot          # i privilegi funzionano
sudo -u ci-deploy touch /home/deploy/discord-bot/deployment/x   # la scrittura funziona
```

> [!warning] Modificare sudoers senza restare chiusi fuori
> Si scrive in un file dedicato sotto `/etc/sudoers.d/`, non in coda a `/etc/sudoers`, e si valida
> con `visudo -c -f <file>` **prima** di considerarlo attivo. Verificare il percorso reale con
> `which systemctl`. Non chiudere la sessione SSH finché un secondo terminale non conferma che
> `sudo` funziona ancora: una sintassi sbagliata rende `sudo` inutilizzabile, e si rientra solo
> dalla console di recupero Hetzner.

> [!info] Perché `ci-deploy` sta fuori dal gruppo docker
> Appartenere al gruppo `docker` **equivale ad avere root**: chi parla col demone può montare la
> radice del filesystem dentro un container. È il motivo per cui separare i due utenti non era un
> vezzo: restringere i privilegi `sudo` di un utente che sta nel gruppo `docker` non serve a niente.
> `deploy` ci resta perché gli serve per il container MySQL, ma la sua chiave non è su GitHub.

## L'ambiente di produzione

| Elemento | Valore |
|---|---|
| Provider | Hetzner Cloud, Ubuntu 22.04, 2 vCPU / 4 GB / 40 GB |
| Utente di esecuzione | `deploy` (non root) |
| JAR e configurazione | `/home/deploy/discord-bot/deployment/` |
| Log applicativi e backup | `/opt/discord-bot/logs/` |
| Servizio | systemd `discord-bot` |
| Database | MySQL in Docker (`docker-compose.mysql-only.yml`), porta 3306 |
| Reverse proxy | nginx sui sottodomini, certificati Let's Encrypt |
| Porta applicativa | 8080, in ascolto su `127.0.0.1` |

L'unit systemd: `EnvironmentFile` che carica il `.env`, `SPRING_PROFILES_ACTIVE=prod`,
`-Xms512m -Xmx2g`, `Restart=always` con `RestartSec=10`, `NoNewPrivileges`, `PrivateTmp`,
`UMask=0077`, stdout e stderr sul **journal**.

### Chi scrive i log, e perché non più systemd sugli stessi file

I file sotto `/opt/discord-bot/logs/` li scrive e li ruota **logback** (30 giorni, `totalSizeCap`
1GB). Fino al 2026-08-19 l'unit systemd scriveva stdout e stderr **sugli stessi percorsi** con
`append:`, e le due cose si ostacolavano: quando logback rinominava il file per la rotazione,
systemd restava agganciato all'inode vecchio e continuava a scriverci — un file che nessuno ruotava
più e cresceva senza limite.

Ora i due flussi sono separati:

```bash
journalctl -u discord-bot -f          # avvio, crash, output non gestito (ruota systemd)
tail -f /opt/discord-bot/logs/*.log   # log applicativi (ruota logback)
```

`UMask=0077` fa nascere quei file leggibili al solo utente del servizio: prima erano `0644`, e
contengono username e ID Discord — quindi erano leggibili da chiunque avesse un account sul server,
**`ci-deploy` compreso**, che esiste apposta per non poter leggere più del dovuto.

> [!warning] Il file nel repository non è il servizio attivo
> `deployment/discord-bot.service` è un modello. Dopo averlo modificato va copiato in
> `/etc/systemd/system/` e serve `sudo systemctl daemon-reload`, altrimenti sul server continua a
> girare la versione precedente.

Il dominio è **`vutradingfarm.it`** dal 2026-07-24 (prima `inwestors.it`): l'app risponde su
`discord.<dominio>`, VuTracker su `vutracker.<dominio>` ([[Runbook cambio dominio]]).

## Cosa il deploy NON fa

- **non applica migrazioni al database** — ma dal 2026-07-25 non serve: le applica **Flyway** al
  riavvio dell'applicazione, dalle migration versionate nel repo. `ddl-auto` resta `validate`, quindi
  se una migration manca il boot fallisce con un messaggio chiaro ([[Schema del database]]);
- **non aggiorna il `.env`**: va caricato via scp/WinSCP e l'app **riavviata**, perché l'ambiente si
  legge solo all'avvio;
- **non esegue i test**;
- **non tocca nginx né i certificati**.

## Comandi essenziali sul server

```bash
sudo systemctl status discord-bot        # stato
sudo systemctl restart discord-bot       # riavvio (serve dopo ogni modifica al .env)
sudo journalctl -u discord-bot -f        # log in tempo reale
tail -f /opt/discord-bot/logs/discord-bot.log
```

## Voci correlate
- [[Ambienti e profili Spring]]
- [[Variabili d'ambiente]]
- [[Schema del database]]
- [[Backup del database]]
