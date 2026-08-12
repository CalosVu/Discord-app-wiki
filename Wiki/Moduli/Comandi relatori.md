---
tipo: modulo
titolo: Comandi relatori
alias: [miemasterclass, report relatore]
tag: [dominio/bot, dominio/comandi, dominio/masterclass]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Comandi relatori

Un solo comando, `!miemasterclass`, riservato a chi è censito nella tabella `relatori`
([[Relatore]]).

## Chi può usarlo

Il riconoscimento è `relatoreRepository.findByDiscordId(user.getId())`. Chi non è relatore riceve
«Non risulti registrato come relatore». Nota: il controllo **non** guarda il flag `attivo` — un
relatore disattivato può ancora consultare i propri report storici, pur non comparendo più nel menu
di acquisto.

## Il percorso

```
!miemasterclass
  └─ menu: [Tutte le masterclass] + le sue masterclass (anche quelle disattivate)
       └─ menu: [Mese corrente] [Mese precedente]
            └─ embed del report in DM
```

Nel primo menu compaiono **tutte** le masterclass del relatore, incluse le non più attive: i report
storici restano consultabili.

## Cosa contiene il report

Una riga per acquirente:

```
• <username> — lordo X€ · server Y€ · Stripe Z€ · netto W€ ⏳ — gg/MM
```

e in fondo i totali: numero acquirenti, totale lordo, commissione server, commissione Stripe, netto
relatore.

Il simbolo **⏳** indica una riga con `fee_pending = true`, cioè commissione Stripe non ancora
confermata e netto **provvisorio** ([[Riconciliazione della fee Stripe]]).

## ⚠️ I numeri "server" e "netto" sono teorici

Nel modello attivo il server **non trattiene nulla**: l'incasso arriva interamente sull'account
Stripe del relatore. Quindi:

- `lordo` e `commissione Stripe` sono **reali**;
- `commissione server` e `netto relatore` sono **calcolati ma non applicati**: il relatore incassa
  davvero `lordo − commissione Stripe`.

È una conseguenza diretta della scelta di non usare Stripe Connect. Vedi
[[Pagamento masterclass]] e [[Sistema masterclass]].

## Notifiche automatiche

Oltre al report su richiesta, il relatore riceve un **DM a ogni vendita** con masterclass,
acquirente, importo lordo, proprio netto (marcato «⏳ in conferma» se la fee non è ancora nota) e
data. Se il DM non parte — per esempio con i messaggi privati chiusi — l'errore viene loggato ma
**non** blocca l'erogazione del contenuto all'acquirente.

## La vista admin

Gli admin hanno due comandi analoghi ma più ampi: `!report_masterclass` (per relatore, con
selezione della masterclass) e `!profitti_masterclass` (globale, con breakdown per relatore). Vedi
[[Comandi admin]].

## Voci correlate
- [[Relatore]]
- [[Masterclass]]
- [[Sistema masterclass]]
- [[Comandi admin]]
