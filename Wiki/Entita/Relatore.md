---
tipo: entita
titolo: Relatore
alias: [relatori, Relatore masterclass]
tag: [dominio/masterclass]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Relatore

Chi pubblica e vende [[Masterclass]] sul server. Tabella `relatori`, entità `Relatore`.

## Come si diventa relatore

**A mano, via SQL**, come per [[Agente]] e [[Utente lifetime]]. Nessun comando di gestione nel bot
(decisione esplicita, vedi [[Piano sviluppo masterclass]]). `discord_id` è `UNIQUE` con FK verso
`users.discord_id`: l'utente deve essere già censito.

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | chiave di riconoscimento per `!miemasterclass` |
| `user` | `user_id` | riferimento all'[[Utente]] |
| `username` | `username` | mostrato nei menu di acquisto e nei report |
| `stripeAccountId` | `stripe_account_id` | `acct_xxx` del connected account. **NULL nel modello attivo** |
| `attivo` | `attivo` | se `false` il relatore sparisce dal menu di acquisto |
| `dataInserimento` | `data_inserimento` | `@CreationTimestamp` |

La percentuale trattenuta dal server **non** sta qui: è per singola masterclass
(`masterclass.percentuale_server`).

## ⚠️ Il numero del relatore deve combaciare in tre punti

Nel modello attivo "chiave per relatore" ([[Sistema masterclass]]) le chiavi Stripe di ciascun
relatore si leggono dalle variabili d'ambiente **indicizzate per `relatori.id`**:

```
STRIPE_MC_SK_<id>       secret key di quel relatore
STRIPE_MC_WHSEC_<id>    webhook secret del suo endpoint
```

L'`id` deve essere lo stesso in **tre** posti, altrimenti il flusso si rompe in silenzio:

1. l'URL del webhook configurato nel Dashboard Stripe di quel relatore
   (`…/api/webhooks/stripe/masterclass/relatore/{id}`);
2. la colonna `relatori.id` nel database;
3. il suffisso delle due variabili nel file d'ambiente ([[Chiavi Stripe]]).

Se una chiave manca, il codice solleva `IllegalStateException` con il nome esatto della variabile
attesa; il webhook risponde **400** («Relatore non configurato») invece di 500, per non innescare i
retry di Stripe per giorni.

## Cosa può fare un relatore

Un solo comando: `!miemasterclass` — report delle vendite per masterclass (o tutte) e per mese
corrente/precedente. Vedi [[Comandi relatori]].

Riceve inoltre un **DM automatico a ogni vendita**, con acquirente, lordo e netto.

## Voci correlate
- [[Masterclass]]
- [[Pagamento masterclass]]
- [[Sistema masterclass]]
- [[Comandi relatori]]
