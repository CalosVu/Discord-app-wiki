---
tipo: fonte
titolo: Guida SSL e DNS
alias: [Guida_installazione_ssl_dns]
tag: [fonte/documento, dominio/infrastruttura]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Guida SSL e DNS

Variante estesa della [[Guida di deployment]] che aggiunge **DNS, nginx, Let's Encrypt e la
configurazione dei webhook Stripe**. **Fonte di rango 4**.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/Guida_installazione_ssl_dns.md` (~18 KB, 9 fasi)
- **Data:** agosto 2025

## Cosa aggiunge rispetto alla guida di deployment

- **Fase 2 — DNS:** dominio principale sul provider, record `A` del sottodominio `discord.` verso
  l'IP Hetzner, verifica con `nslookup` e whatsmydns.net (propagazione 5-60 minuti).
- **Fase 7 — nginx:** virtual host su porta 80 con `proxy_pass` verso `127.0.0.1:8080` e gli header
  `X-Real-IP`, `X-Forwarded-*`; abilitazione via symlink in `sites-enabled`, `nginx -t`, reload.
- **Fase 8 — SSL:** `certbot --nginx -d <sottodominio>`, verifica dell'auto-rinnovo con
  `certbot renew --dry-run` e `systemctl status certbot.timer`. Certbot riscrive da solo il blocco
  nginx aggiungendo redirect HTTP→HTTPS e configurazione TLS.
- **Fase 9 — Stripe:** creazione dell'endpoint webhook nel Dashboard e copia del `whsec_` nel `.env`.

## Il file `discord-bot.service` (systemd)

È qui che il documento riporta l'unit completa: utente `deploy`, `EnvironmentFile` che carica il
`.env`, `SPRING_PROFILES_ACTIVE=prod`, `-Xms512m -Xmx2g`, `Restart=always` con `RestartSec=10`,
log su file, `NoNewPrivileges` e `PrivateTmp`. Dettagli in [[Deploy e CI-CD]].

## ⚠️ Punti superati

- Gli **eventi webhook** suggeriti (`payment_intent.succeeded`, `payment_intent.payment_failed`,
  `customer.subscription.created`, `invoice.payment_succeeded`) non corrispondono a quelli
  effettivamente gestiti dal codice, che sono **solo** `checkout.session.completed` e
  `charge.updated` (vedi [[Pagamenti Stripe]]).
- Il redirect OAuth indicato (`/api/auth/callback`) non è quello reale
  (`/login/oauth2/code/discord`, vedi [[Runbook cambio dominio]]).
- Il `docker-compose` proposto usa `mysql:8.0` e la direttiva `version:`; quello nel repo usa
  `mysql:latest` senza `version:`.
- Il dominio d'esempio è precedente alla migrazione a `vutradingfarm.it`.

## Voci correlate
- [[Fonti]]
- [[Guida di deployment]]
- [[Runbook cambio dominio]]
