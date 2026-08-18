---
tipo: entita
titolo: Pagamento
alias: [Payments, payments, incasso]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Pagamento

Un incasso verso il server: abbonamento [[Abbonamento Supporter Member]] o [[Sostegno libero]],
pagato in crypto o con carta. Tabella `pagamenti`, entità `discord.access.app.entity.Payments`.

Non include gli acquisti di masterclass, che vivono su una tabella separata
([[Pagamento masterclass]]).

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `user` / `discordId` | `user_id`, `discord_id` | doppio riferimento all'[[Utente]] (FK su entrambi) |
| `importo` | `importo` | **netto** dopo la fee Stripe; in crypto è l'importo trasferito. Vedi [[Riconciliazione della fee Stripe]] |
| `emailCliente` | `email_cliente` | email dell'account Stripe che ha pagato, per il riconoscimento da parte degli admin. `NULL` in crypto. Indicizzata |
| `transactionHash` | `transaction_hash` | `UNIQUE`. In crypto è l'hash reale; in Stripe è un **UUID sintetico** generato per rispettare il vincolo |
| `rete` | `rete` | `"Arbitrum"` oppure `"Stripe"` |
| `stripeSessionId` | `stripe_session_id` | id della Checkout Session; per il crypto è **stringa vuota** |
| `stripePaymentIntentId` | `stripe_payment_intent_id` | serve a correlare l'evento `charge.updated` |
| `feePending` | `fee_pending` | `true` se l'importo salvato è ancora **lordo** |
| `metodoPagamento` | `metodo_pagamento` | `CRYPTO` \| `STRIPE` \| `PAYPAL` (mai usato) |
| `stripeAccount` | `stripe_account` | `PRIMARIO` \| `SECONDARIO`; `NULL` sulle righe crypto ([[Bilanciamento degli account Stripe]]) |
| `tipoTransazione` | `tipo_transazione` | `SUPPORTER_MEMBER` \| `GOLD_SUPPORTER_MEMBER` |
| `statoVerifica` / `status` | `stato_verifica`, `status` | entrambi `PENDING`\|`COMPLETED`\|`FAILED` |
| `walletMittente` | `wallet_mittente` | crypto: indirizzo `from`. Stripe: ci viene messo lo *username* Discord |
| `dataPagamento` | `data_pagamento` | crypto: timestamp del blocco. Stripe: ora italiana del webhook |

## Regole di salvataggio

Tutti i pagamenti passano da un unico metodo — `CryptoPaymentService.savePaymentAndUpdateUser` —
usato anche dal flusso Stripe. Conseguenze:

- Le righe nascono **sempre** `COMPLETED` su entrambi i campi di stato: `PENDING` e `FAILED`
  esistono nell'enum ma non vengono mai scritti.
- Dopo il salvataggio viene tentata la registrazione della [[Commissione pagamento]]; un errore lì
  viene loggato ma **non** annulla il pagamento.
- Subito dopo si aggiorna l'[[Utente]] (scadenza, rinnovi, ruolo) e si notificano gli admin.

## Doppia scrittura di stato

`statoVerifica` e `status` contengono sempre lo stesso valore, ma **le query di bilancio filtrano
solo `stato_verifica = 'COMPLETED'`**. Chi scrive nuove query deve usare quel campo per restare
coerente con i report esistenti.

## Perché l'hash sintetico su Stripe

`transaction_hash` è `UNIQUE` a livello di tabella per impedire il doppio uso della stessa transazione
crypto. I pagamenti Stripe non hanno un hash: il codice genera un `UUID` per soddisfare il vincolo.
È un dato **senza significato**: per identificare un pagamento Stripe si usa `stripe_session_id` o
`stripe_payment_intent_id`.

Fino alla `V30` l'hash valeva `UUID + "_" + email cliente`: l'email serve agli admin per riconoscere
chi ha pagato, ma stava in una colonna tecnica, cercabile solo con `LIKE '%...'` e invisibile a chi
legge lo schema. La `V30` l'ha spostata in `email_cliente` recuperandola dalle righe esistenti, e ha
troncato gli hash storici al solo UUID.

## Voci correlate
- [[Pagamenti Stripe]]
- [[Pagamenti crypto Arbitrum]]
- [[Prelievo]]
- [[Reportistica]]
