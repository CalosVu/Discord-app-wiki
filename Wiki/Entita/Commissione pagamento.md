---
tipo: entita
titolo: Commissione pagamento
alias: [commissioni_pagamento, CommissionePagamento]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Commissione pagamento

La riga che lega un [[Pagamento]] all'[[Agente]] che lo ha procurato. Tabella
`commissioni_pagamento`, entità `CommissionePagamento`.

## Quando viene creata

Subito dopo il salvataggio di **ogni** pagamento (crypto o Stripe), dentro
`CommissioneService.registraCommissioneSeApplicabile`. La riga nasce solo se **tutte** queste
condizioni sono vere:

1. il pagamento è associato a un [[Utente]];
2. l'utente ha un `referral` valorizzato ([[Referral agent]]);
3. il creatore di quell'invito esiste nella tabella `agenti`;
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
| `metodoPagamento` | `metodo_pagamento` | separa i report Stripe (EUR) da quelli crypto (USD) |
| `dataPagamento` | `data_pagamento` | copiata dal pagamento; è il campo su cui si filtra il mese |

## L'importo non è salvato

La tabella **non ha una colonna importo**: la commissione si calcola on-demand a ogni report, come

```
importo_commissione = payment.importo × percentuale_applicata / 100     (HALF_UP, 2 decimali)
```

Due conseguenze pratiche:

- se il [[Pagamento]] viene **riconciliato** dopo (lordo → netto, vedi
  [[Riconciliazione della fee Stripe]]), la commissione si ricalcola sul **netto**: il valore
  mostrato può cambiare fra un report e quello successivo;
- la percentuale invece **non** cambia mai retroattivamente, perché è congelata sulla riga.

## Idempotenza

`existsByPaymentId` impedisce il doppio conteggio se lo stesso pagamento viene rielaborato. Non
esiste però un vincolo `UNIQUE` a livello di tabella: la protezione è solo applicativa.

## Voci correlate
- [[Agente]]
- [[Sistema referral e commissioni]]
- [[Comandi agenti]]
