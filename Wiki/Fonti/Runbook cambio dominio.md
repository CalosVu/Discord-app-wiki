---
tipo: fonte
titolo: Runbook cambio dominio
alias: [ComeCambiarePuntamentiDominioApp]
tag: [fonte/documento, dominio/infrastruttura]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Runbook cambio dominio

Procedura per migrare l'app da un dominio a un altro, ricavata dalla migrazione reale
`inwestors.it` → `vutradingfarm.it`. **Fonte di rango 4**, ed è la **più recente** sull'infrastruttura:
in caso di conflitto prevale su [[Guida di deployment]] e [[Guida SSL e DNS]].

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/ComeCambiarePuntamentiDominioApp.md` (~16 KB)
- **Data:** 2026-07-24 (giorno della migrazione)

## Il fatto architetturale chiave

> L'app **non ha nessun dominio hardcoded nel codice**: tutti gli URL rivolti all'esterno arrivano
> da variabili d'ambiente. Il cambio dominio è quindi lavoro di **configurazione**, non di codice.

Le app girano sui **sottodomini**, il dominio nudo è una landing su hosting separato:

| Sottodominio | Applicazione | Proxy nginx |
|---|---|---|
| `discord.<dominio>` | Discord-access-app | `127.0.0.1:8080` |
| `vutracker.<dominio>` | VuTracker (SPA React + API) | statico + `/api/` → `127.0.0.1:8082` |

## I 5 fronti da allineare

Cambiare il `.env` **non basta**. Ordine consigliato: DNS → nginx/SSL → Discord Portal → Stripe →
`.env` + restart → VuTracker → test → dismissione del vecchio dominio.

1. **DNS**: record A dei sottodomini verso l'IP del server, attendere la propagazione.
2. **nginx + certbot**: blocco solo su porta 80, poi `certbot --nginx` aggiunge l'HTTPS (evita il
   problema dell'uovo e della gallina col certificato).
3. **`.env` dell'app**: 5 variabili di URL da cambiare **solo nell'host** — vedi
   [[Variabili d'ambiente]]. ⚠️ Non toccare `DB_URL`. Riavviare il servizio: l'env si legge all'avvio.
4. **Discord Developer Portal**: il redirect OAuth deve essere **byte-identico** a
   `DISCORD_REDIRECT_URI`, altrimenti `redirect_uri_mismatch`.
5. **Stripe**: i webhook sono chiamate *in entrata*, si aggiornano nel Dashboard di **ogni** account
   — principale, secondo account e **uno per ciascun relatore masterclass**. Se si **edita** l'URL
   il `whsec_` resta lo stesso; se si **ricrea** l'endpoint il secret cambia e va riportato nel `.env`.
6. **VuTracker** (repo separato): `.env` backend + API key allineata, e il **frontend React va
   ricompilato** se l'URL era "cotto" nel build.

## Trappole documentate

- `curl -I` su un endpoint OAuth restituisce **403**: è una `HEAD`, Spring accetta solo `GET`.
  Non è un errore — vale solo il test dal browser.
- La dismissione del vecchio dominio va fatta **in ordine**: prima i symlink nginx, poi
  `certbot delete`, infine i DNS. Altrimenti `nginx -t` fallisce su certificati appena cancellati.
- Fare lo switch in **fascia a basso traffico**: i checkout Stripe già aperti puntano ancora al
  vecchio host per success/cancel.

## Voci correlate
- [[Fonti]]
- [[Deploy e CI-CD]]
- [[Integrazione VuTracker]]
