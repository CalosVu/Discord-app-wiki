---
tipo: entita
titolo: Commissione pagamento
alias: [commissioni_pagamento, CommissionePagamento]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Commissione pagamento

La riga che lega un [[Pagamento]] all'[[Agente]] che lo ha procurato. Tabella
`referral_commissioni`, entità `CommissionePagamento`.

## Quando viene creata

Subito dopo il salvataggio di **ogni** pagamento (crypto o Stripe), dentro
`CommissioneService.registraCommissioneSeApplicabile`. La riga nasce solo se **tutte** queste
condizioni sono vere:

1. il pagamento è associato a un [[Utente]];
2. l'utente ha un `referral` valorizzato ([[Referral agent]]);
3. il creatore di quell'invito esiste nella tabella `referral_agenti`;
4. se l'agente ha `codici_ref_validi` valorizzato, il codice dell'utente è **in quella lista**;
5. non esiste già una commissione per lo stesso `payment_id`.

Se una qualsiasi condizione manca, il metodo esce in silenzio: nessuna commissione, nessun errore.

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `agente` | `agente_id` | l'[[Agente]] beneficiario |
| `payment` | `payment_id` | il [[Pagamento]] sorgente |
| `discordIdUtente` / `usernameUtente` | omonime | snapshot dell'utente pagante |
| `percentualeApplicata` | `percentuale_applicata` | **congelata** dal valore dell'agente al momento |
| `importoCommissione` | `importo_commissione` | **congelato** alla registrazione (da `V17`) |
| `metodoPagamento` | `metodo_pagamento` | separa i report Stripe (EUR) da quelli crypto (USD) |
| `dataPagamento` | `data_pagamento` | copiata dal pagamento; è il campo su cui si filtra il mese |
| `dataUpdate` | `data_update` | audit |

`metodoPagamento` e `dataPagamento` sono copie di dati che stanno su [[Pagamento]]: ridondanti, ma
sono le colonne su cui filtrano le query dei report, che così non devono fare la join.

## L'importo è congelato alla registrazione

```
importo_commissione = payment.importo × percentuale_applicata / 100     (HALF_UP, 2 decimali)
```

Il calcolo avviene **una volta sola**, quando la commissione nasce. Percentuale e importo sono
quindi entrambi fermi: il report di un mese chiuso dice **quanto spettava allora**.

> [!warning] Com'era prima di `V17` (2026-08-14)
> L'importo non era salvato e veniva ricalcolato a ogni lettura su `payment.importo`. Ma quel
> valore **cambia dopo l'incasso**: se la commissione nasceva su un pagamento Stripe con la fee non
> ancora disponibile, l'importo era il **lordo**, e la riconciliazione lo riportava al netto anche
> ore dopo ([[Riconciliazione della fee Stripe]]).
>
> La commissione calava quindi da sé, e lo stesso report emesso in due giorni diversi dava numeri
> diversi — senza traccia del valore precedente. La percentuale, già congelata, era invece corretta.
>
> Il difetto non si è mai manifestato: al momento della correzione esisteva **una sola commissione**
> in tutto il database, su un pagamento già riconciliato. Il metodo `calcolaCommissione` conserva il
> ricalcolo come ripiego per le righe prive di importo.

## Idempotenza

`existsByPaymentId` impedisce il doppio conteggio se lo stesso pagamento viene rielaborato. Non
esiste però un vincolo `UNIQUE` a livello di tabella: la protezione è solo applicativa.

## Voci correlate
- [[Agente]]
- [[Sistema referral e commissioni]]
- [[Comandi agenti]]
