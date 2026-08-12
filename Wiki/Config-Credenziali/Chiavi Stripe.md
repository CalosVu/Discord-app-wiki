---
tipo: config
titolo: Chiavi Stripe
alias: [secret key, webhook secret, STRIPE_MC_SK]
tag: [dominio/configurazione, dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Chiavi Stripe

Il sistema usa **più account Stripe contemporaneamente**, ognuno con la propria coppia di chiavi.
Questa pagina elenca quali sono, a cosa servono e come si ruotano.

> ⚠️ Solo nomi di variabili, mai valori (CLAUDE.md §5.6).

## Gli insiemi di chiavi

| Insieme | Variabili | Chi le usa |
|---|---|---|
| **Supporter — Primario** (storico) | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` | [[Pagamenti Stripe]]; la secret key è anche la `Stripe.apiKey` globale |
| **Supporter — Secondario** | `STRIPE_SECONDARIO_SECRET_KEY`, `STRIPE_SECONDARIO_WEBHOOK_SECRET` | [[Bilanciamento degli account Stripe]]. **Default vuoto**: se non valorizzate, tutto va sul primario |
| **Masterclass Connect** (congelato) | `STRIPE_MC_SECRET_KEY`, `STRIPE_MC_WEBHOOK_SECRET` | solo con `MASTERCLASS_PAYMENT_MODE=connect`. Default vuoto |
| **Masterclass per relatore** (attivo) | `STRIPE_MC_SK_<relatoreId>`, `STRIPE_MC_WHSEC_<relatoreId>` | [[Sistema masterclass]] |

Gli URL di ritorno sono variabili separate: `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`,
`STRIPE_MC_SUCCESS_URL`, `STRIPE_MC_CANCEL_URL` ([[Variabili d'ambiente]]).

## Perché le chiavi dei relatori sono nell'ambiente e non nel database

Servono **in chiaro a runtime**, quindi un hash non è applicabile: metterle in una colonna
significherebbe conservare segreti in chiaro nel DB. La soluzione adottata è leggerle dall'ambiente
tramite l'astrazione `RelatoreStripeKeyProvider`.

Se un giorno i relatori diventassero molti, si sostituirebbe **solo** l'implementazione del provider
con una versione a database **cifrato** (AES-GCM con master key nell'ambiente), senza toccare il
resto del codice.

## Aggiungere un relatore

1. inserire la riga in `relatori` e annotare l'`id` generato;
2. aggiungere al file d'ambiente `STRIPE_MC_SK_<id>` e `STRIPE_MC_WHSEC_<id>`;
3. nel Dashboard Stripe **di quel relatore**, creare l'endpoint webhook
   `https://discord.<dominio>/api/webhooks/stripe/masterclass/relatore/<id>` con gli eventi
   `checkout.session.completed` e `charge.updated`;
4. riavviare l'applicazione.

⚠️ Lo stesso `<id>` deve comparire in **tutti e tre** i punti (URL, DB, variabili). Vedi [[Relatore]].

## Rotazione

| Chiave | Procedura |
|---|---|
| Secret key | rigenerare nel Dashboard, aggiornare la variabile, riavviare |
| Webhook secret | se si **edita** l'URL dell'endpoint esistente, il `whsec_` **non cambia**; se si **ricrea** l'endpoint, cambia e va riportato nella variabile |

Vale per ogni account: primario, secondario e **ciascun** relatore. Al cambio dominio è l'errore più
frequente ([[Runbook cambio dominio]]).

⚠️ Il path del webhook del secondario è cambiato il 2026-08-12 da `/api/webhooks/stripe/danny` a
**`/api/webhooks/stripe/secondario`**: va aggiornato nel Dashboard Stripe prima di valorizzare le
chiavi, altrimenti i pagamenti su quell'account non verranno mai notificati all'applicazione.

## Isolamento fra i flussi

La `Stripe.apiKey` globale è **solo** quella del primario. Tutti gli altri flussi passano
`RequestOptions.setApiKey(...)` esplicitamente a ogni chiamata: nessuna chiamata usa per sbaglio la
chiave sbagliata. Se una chiave manca, il codice solleva `IllegalStateException` con **il nome esatto
della variabile attesa** — messaggio prezioso in diagnosi.

## Voci correlate
- [[Pagamenti Stripe]]
- [[Bilanciamento degli account Stripe]]
- [[Sistema masterclass]]
- [[Variabili d'ambiente]]
