---
tipo: concetto
titolo: Bilanciamento degli account Stripe
alias: [doppio Stripe, Lillo, Danny, StripeAccountSelector]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Bilanciamento degli account Stripe

Il sistema incassa su **due account Stripe distinti**, `LILLO` e `DANNY`, e sceglie automaticamente
dove indirizzare ogni nuovo pagamento per tenere i due saldi allineati.

- **LILLO** — l'account storico. Tutte le righe Stripe preesistenti sono state migrate a questo valore.
- **DANNY** — il secondo account, aggiunto per bilanciare gli incassi.

## Il criterio di scelta

```
netto(account) = somma pagamenti COMPLETED di quell'account
               − somma prelievi COMPLETATI di quell'account

si sceglie l'account con netto MINORE
a parità (o se DANNY è maggiore) → LILLO      ← tie-break deterministico
```

Il calcolo si fa a ogni generazione di link, su tutto lo storico. Con Lillo che parte da uno storico
positivo e Danny da zero, **Danny riceve tutti i pagamenti finché non pareggia**, poi i due si
alternano a zig-zag.

I [[Prelievo|prelievi]] entrano nel conto: registrarne uno su un account lo fa tornare "più povero"
e quindi favorito per gli incassi successivi.

## La guardia di sicurezza

Se il secondo account **non è configurato** (manca la secret key o il webhook secret), il selettore
non tenta nemmeno il calcolo: instrada tutto su `LILLO` e lo scrive nel log. Questo rende sicuro il
deploy del doppio account anche **prima** di inserire le chiavi di Danny.

## Isolamento delle chiavi

La `Stripe.apiKey` globale resta quella di Lillo (retrocompatibilità). Tutte le chiamate del flusso
a doppio account passano invece `RequestOptions` con la chiave dell'account corretto — creazione
della sessione, `PaymentIntent.retrieve`, `Customer.retrieve`, `BalanceTransaction.retrieve`. Un
evento di Danny non viene mai interrogato con la chiave di Lillo.

## Due endpoint webhook separati

| Account | Endpoint | Firma verificata con |
|---|---|---|
| LILLO | `/api/webhooks/stripe` (invariato) | webhook secret di Lillo |
| DANNY | `/api/webhooks/stripe/danny` | webhook secret di Danny |

L'account viene dedotto **dall'endpoint chiamato**, non dal metadata della sessione: un metadata è
falsificabile, il percorso no. Il metadata `stripe_account` viene comunque scritto, come ridondanza
di verifica.

Se un endpoint riceve una chiamata ma le chiavi di quell'account mancano, risponde **400** e non
500: un 500 farebbe ritentare Stripe per giorni (retry-storm) su un endpoint inutilizzabile.

## Dove si vede il risultato

Il report saldo del menu `!Admin` mostra **tre sezioni**: Crypto, Stripe Lillo, Stripe Danny —
ognuna con depositi, prelievi e saldo. Vedi [[Reportistica]].

## Voci correlate
- [[Pagamenti Stripe]]
- [[Prelievo]]
- [[Chiavi Stripe]]
- [[Piano sviluppo doppio Stripe]]
