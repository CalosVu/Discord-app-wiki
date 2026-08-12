---
tipo: concetto
titolo: Riconciliazione della fee Stripe
alias: [fee_pending, pattern A+B, commissione Stripe]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Riconciliazione della fee Stripe

Il meccanismo che garantisce che l'importo salvato sia il **netto** e non il lordo, anche quando
Stripe non ha ancora calcolato la commissione al momento del webhook.

## Il problema

Il sistema vuole salvare in `payments.importo` quanto è **realmente entrato**, cioè
`lordo − commissione Stripe`. La commissione vive nel `balance_transaction` del charge, che però a
volte **non è ancora disponibile** quando arriva `checkout.session.completed`. Senza rete di
sicurezza, il risultato era il bug storico «a volte si salva il lordo».

## La soluzione: pattern A+B

**A — al checkout.** Si recupera il `PaymentIntent` con
`expand = ["latest_charge.balance_transaction"]` (una sola chiamata invece di tre) e si riprova
**una volta** dopo 1,5 secondi.

- fee disponibile → si salva il **netto**, `fee_pending = false`;
- fee assente → si salva il **lordo**, `fee_pending = true` e si logga un warning.

**B — su `charge.updated`.** Quando il `balance_transaction` diventa disponibile, Stripe manda
l'evento; il sistema:

1. controlla **senza chiamate API** se esiste un pagamento con quel PaymentIntent e
   `fee_pending = true` (se no, esce subito: nessuna retrieve inutile);
2. recupera il balance transaction e ricalcola `netto = lordo − fee`;
3. aggiorna l'importo e mette `fee_pending = false`.

L'operazione è **idempotente**: la query filtra su `fee_pending = true`, quindi arrivi multipli
dello stesso evento dopo la prima riconciliazione non hanno effetto.

## Perché serve registrare `charge.updated`

Se nel Dashboard Stripe l'endpoint è configurato solo per `checkout.session.completed`, la parte **B**
non scatta mai: i pagamenti che nascono con `fee_pending = true` **restano col lordo per sempre**,
gonfiando saldi e commissioni agenti. Entrambi gli eventi vanno registrati su ogni endpoint.

## Lo stesso pattern nelle masterclass

Il [[Sistema masterclass]] riusa l'identico schema, con una differenza importante nel significato
dei numeri:

| Modello | `commissione_stripe` | `netto_relatore` |
|---|---|---|
| **direct** (attivo) | `stripe_fee` letta dal balance | `lordo − quota server − stripe_fee` (teorico) |
| **connect** (congelato) | `fee_totale − application_fee` | il `net` restituito da Stripe (reale) |

Nel modello direct l'erogazione del video **non dipende** dalla fee: il link parte comunque al
checkout, la `fee_pending` riguarda solo la contabilità. Nei report le righe non ancora riconciliate
sono marcate con ⏳.

## Voci correlate
- [[Pagamento]]
- [[Pagamenti Stripe]]
- [[Pagamento masterclass]]
- [[Idempotenza dei webhook]]
