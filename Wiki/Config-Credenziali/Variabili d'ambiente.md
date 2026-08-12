---
tipo: config
titolo: Variabili d'ambiente
alias: [.env, env, variabili]
tag: [dominio/configurazione]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Variabili d'ambiente

Inventario **completo** delle variabili lette dall'applicazione, ricavato da `application.yml` e dai
`@Value` nel codice.

> ⚠️ Solo nomi, mai valori. I valori vivono nel file `.env` sul server
> (`/home/deploy/discord-bot/deployment/.env`, `chmod 600`, mai in git).

## Database

| Variabile | Nota |
|---|---|
| `DB_URL` | JDBC. In prod porta **3306**, in locale **3307**. Non c'entra col dominio: al cambio dominio **non si tocca** |
| `DB_USERNAME` | |
| `DB_PASSWORD` | usata anche dal [[Backup del database]] via `MYSQL_PWD` |

## Discord

| Variabile | Nota |
|---|---|
| `DISCORD_BOT_TOKEN` | token del bot. Rotazione: rigenerare nel Developer Portal e riavviare |
| `DISCORD_GUILD_ID` | id del server |
| `DISCORD_DISCLAIMER_CHANNEL` | id del canale del disclaimer |
| `DISCORD_SUPPORTER_MEMBER_ROLE` | **nome** del ruolo, non l'id → [[Ruoli Discord]] |
| `DISCORD_GOLD_SUPPORTER_MEMBER_ROLE` | idem |
| `DISCORD_GUEST_ROLE` | idem |
| `DISCORD_ADMIN_ROLE` | idem — determina chi può usare i [[Comandi admin]] |
| `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` | OAuth2. Flusso **non attivo** ([[Sicurezza e autenticazione]]) |
| `DISCORD_REDIRECT_URI` | **cambia col dominio**; deve essere byte-identico al Developer Portal |

## Stripe

Dettagli e procedura di rotazione in [[Chiavi Stripe]]:
`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`,
`STRIPE_DANNY_SECRET_KEY`, `STRIPE_DANNY_WEBHOOK_SECRET`,
`STRIPE_MC_SECRET_KEY`, `STRIPE_MC_WEBHOOK_SECRET`,
`STRIPE_MC_SK_<relatoreId>`, `STRIPE_MC_WHSEC_<relatoreId>`,
`STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`, `STRIPE_MC_SUCCESS_URL`, `STRIPE_MC_CANCEL_URL`,
`MASTERCLASS_PAYMENT_MODE` (`direct` default | `connect`).

## Crypto / Arbitrum

| Variabile | Nota |
|---|---|
| `ARBITRUM_WALLET_ADDRESS` | wallet che deve **ricevere** i pagamenti. Non è un segreto, ma cambiarlo invalida le verifiche in corso |
| `WEB3J_CLIENT_ADDRESS` | endpoint RPC del nodo Arbitrum. Se contiene una API key (Alchemy/Infura) **è un segreto** |

Gli indirizzi dei contratti USDT/USDC e i decimali sono **fissi in `application.yml`**, non variabili.

## Cloudflare R2

`R2_ENDPOINT`, `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` → [[Credenziali R2]].

## Altro

| Variabile | Nota |
|---|---|
| ~~`VUTRACKER_API_KEY`~~ | **non più usata** dal 2026-08-12: l'integrazione è stata rimossa ([[Integrazione VuTracker]]). Si può togliere dai `.env` |
| `JWT_SECRET`, `JWT_EXPIRATION` | flusso JWT **non attivo**; da rigenerare con valore casuale se un giorno si attiva |
| `SPRING_PROFILES_ACTIVE` | `dev` \| `docker` \| `prod` ([[Ambienti e profili Spring]]) |

## Le cinque variabili che cambiano col dominio

Al cambio dominio si modifica **solo l'host**, lasciando identici i path
([[Runbook cambio dominio]]):

`DISCORD_REDIRECT_URI` · `STRIPE_SUCCESS_URL` · `STRIPE_CANCEL_URL` · `STRIPE_MC_SUCCESS_URL` ·
`STRIPE_MC_CANCEL_URL`

## Come si applica una modifica

L'ambiente si legge **all'avvio**: dopo ogni modifica serve
`sudo systemctl restart discord-bot`. Una modifica senza riavvio non ha alcun effetto — è l'errore
più comune, documentato anche nel troubleshooting del [[Runbook cambio dominio]].

## Voci correlate
- [[Chiavi Stripe]]
- [[Credenziali R2]]
- [[Ambienti e profili Spring]]
- [[Deploy e CI-CD]]
