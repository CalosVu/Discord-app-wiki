---
tipo: fonte
titolo: Guida di deployment
alias: [DEPLOYMENT_GUIDE]
tag: [fonte/documento, dominio/infrastruttura]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Guida di deployment

Runbook completo per ricreare da zero l'ambiente di produzione su Hetzner Cloud. **Fonte di rango 4**:
descrive l'infrastruttura, che il codice non può raccontare.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/DEPLOYMENT_GUIDE.md` (~24 KB, 8 fasi + troubleshooting)
- **Data:** aprile 2026

## Cosa copre

| Fase | Contenuto |
|---|---|
| 1 | Creazione server Hetzner (Ubuntu 22.04, 2 vCPU / 4 GB / 40 GB), chiavi SSH, utente `deploy`, UFW, fail2ban |
| 2 | Installazione Java 21, Maven 3.9.11, nginx |
| 3 | Chiave SSH dedicata a GitHub Actions e secret di repository (`SERVER_HOST`, `SERVER_SSH_KEY`) |
| 4 | Upload di `.env`, script SQL, docker-compose, unit systemd (scp o WinSCP) e permessi |
| 5 | Avvio di MySQL in Docker e verifica dell'inizializzazione dello schema |
| 6 | Installazione del servizio systemd `discord-bot` e directory dei log |
| 7 | Primo deploy e verifica |
| 8 | Accesso al DB da locale via **tunnel SSH** in DBeaver |

Più: comandi di manutenzione, troubleshooting, backup/restore manuale del database.

## Fatti operativi che ne derivano

Sono raccolti nelle pagine di destinazione, non duplicati qui (CLAUDE.md §5.7):

- server, percorsi di deploy e dei log, unit systemd → [[Deploy e CI-CD]]
- profili Spring e file `.env` → [[Ambienti e profili Spring]]
- backup del database → [[Backup del database]]

## Sovrapposizioni e precedenza

Il documento si sovrappone parzialmente a [[Guida SSL e DNS]] (che aggiunge DNS, nginx, certbot e
Stripe) e a [[Runbook cambio dominio]] (che è **più recente**: luglio 2026). In caso di conflitto
sull'infrastruttura, **vale il documento più recente**.

Un dettaglio già superato: la guida cita l'IP `49.13.83.180` e il dominio `inwestors.it`; il dominio
è stato migrato a `vutradingfarm.it` il 2026-07-24 (vedi [[Runbook cambio dominio]]).

## Voci correlate
- [[Fonti]]
- [[Deploy e CI-CD]]
