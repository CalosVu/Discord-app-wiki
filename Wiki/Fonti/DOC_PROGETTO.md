---
tipo: fonte
titolo: DOC_PROGETTO
alias: [documentazione iniziale]
tag: [fonte/documento]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: obsoleto
---

# DOC_PROGETTO

Documento descrittivo iniziale del progetto. **Fonte di rango 5** (il più basso): descrive in gran
parte un sistema **mai realizzato**.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/DOC_PROGETTO.md`
- **Data:** maggio 2025 (inizio progetto)
- **Titolo interno:** «Progetto: Discord Premium Access Bot»

## Cosa contiene ancora di valido

- La **suddivisione in 5 moduli Maven** (`common`, `persistence`, `security`, `service`, `api`) e le
  loro responsabilità: coincide con [[Architettura dei moduli Maven]].
- Le note su **Docker Compose**, porta MySQL `3307` in locale e profili Spring `dev`/`docker`:
  coincidono con [[Ambienti e profili Spring]].
- Il link all'applicazione sul **Discord Developer Portal**.

## ⚠️ Claim superate dal codice

Il documento descrive funzionalità che **non esistono** nel codice su `main`:

| Claim del documento | Realtà nel codice |
|---|---|
| Pagamenti via **Bybit** e **PayPal** | Nessuna integrazione: si usano [[Pagamenti Stripe]] e [[Pagamenti crypto Arbitrum]]. `PAYPAL` sopravvive solo come valore enum mai usato ([[Enum di dominio]]) |
| **2FA con Google Authenticator** (TOTP, QR code) | Assente. Nessuna classe TOTP nel codice |
| **Anti-condivisione credenziali** (IP, User-Agent, 5 accessi, disabilitazione automatica) | Assente. Resta solo `DiscordService.revokeUserAccess`, con javadoc «AL MOMENTO NON VIENE USATO» |
| Endpoint `/auth/2fa/setup`, `/payment/bybit/check`, `/payment/paypal/*`, `/user/profile` | Non esistono. Gli endpoint reali sono in [[Endpoint REST]] |
| **Login OAuth2 Discord** come flusso applicativo con JWT | La configurazione OAuth2 esiste in `application.yml`, ma il flusso JWT **non è attivamente usato** (vedi [[Sicurezza e autenticazione]]) |
| Tabella `tracking_user`, campi `email` e `totp_secret` su `users` | Non esistono nello [[Schema del database]] |

## Come usarlo

Solo come **contesto storico** sull'intenzione originale del progetto. Per qualsiasi affermazione
fattuale sul comportamento attuale, vale il [[Codice Discord-access-app]].

## Voci correlate
- [[Fonti]]
- [[Integrazione sistema pagamenti]] — l'altro documento iniziale, con lo stesso grado di obsolescenza
