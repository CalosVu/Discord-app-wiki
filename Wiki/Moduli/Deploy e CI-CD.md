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
4. `scp` del JAR sul server e, via `ssh`, rinomina in `app.jar` + `systemctl restart discord-bot`.

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
`-Xms512m -Xmx2g`, `Restart=always` con `RestartSec=10`, `NoNewPrivileges`, `PrivateTmp`, log
rediretti su file.

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
