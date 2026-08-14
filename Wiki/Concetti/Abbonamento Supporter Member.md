---
tipo: concetto
titolo: Abbonamento Supporter Member
alias: [supporter member, abbonamento, iscrizione]
tag: [dominio/abbonamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Abbonamento Supporter Member

L'abbonamento al server: dà il ruolo `SUPPORTER_MEMBER` e l'accesso a tutti i canali. Si paga a
mesi, in anticipo, tramite [[Pagamenti Stripe]] o [[Pagamenti crypto Arbitrum]].

Non è un abbonamento ricorrente: **non c'è addebito automatico**. Ogni rinnovo è un nuovo pagamento
volontario, sollecitato dai promemoria del [[Batch verifica abbonamenti]].

## Il calcolo della scadenza

Tutto avviene in `aggiornaAbbonamentoUtente`, uguale per entrambi i canali:

```
giorni = pianoApplicato.durataGiorniAbbonamento × numeroMesi     (30 × mesi)

se scadenza è null oppure già passata:
    nuova scadenza = adesso + giorni
    se dataPrimaIscrizione è null → dataPrimaIscrizione = adesso
altrimenti (scadenza futura, rinnovo anticipato):
    nuova scadenza = scadenza + giorni        ← i giorni residui NON si perdono
```

Poi, sempre: `numeroRinnovi += 1`, `dataUltimaDonazione = adesso`,
`ultimoPagamento` = il [[Pagamento]] appena creato, assegnazione del ruolo.

**Il rinnovo anticipato è premiato**: chi rinnova prima della scadenza somma i giorni invece di
azzerarli.

## Nuovo iscritto o rinnovo?

La distinzione si basa **solo** su `dataPrimaIscrizione == null`, non su `numeroRinnovi`. È il campo
che decide quale flag di [[Blocco dei pagamenti]] si applica e quale testo ricevono gli admin
(«Nuova registrazione» vs «Rinnovo»).

Attenzione all'ordine: `numeroRinnovi` viene incrementato **dopo** aver valutato l'eventuale promo,
perché `getPromoAttiva` usa quel contatore per capire se si tratta di un rinnovo
([[Promozioni temporali]]).

## Il prezzo

Dipende dal canale e dallo stato dell'utente:

| Canale | Sorgente del prezzo |
|---|---|
| Stripe | `utente.pianoApplicato.prezzoEur` × mesi |
| Crypto | `PIONIERE.prezzoUsd` se [[Membri pionieri]], altrimenti `BASIC.prezzoUsd` |

In entrambi i casi una promo attiva sovrascrive prezzo **e** numero di mesi. Vedi
[[Catalogo servizi]] per il dettaglio (e per la trappola delle due sorgenti divergenti).

## Notifica agli admin

Ogni abbonamento andato a buon fine produce un DM a **tutti** i membri con ruolo admin, con:
azione (nuova registrazione / rinnovo), mesi, promo applicata, totale verificato, metodo di
pagamento. Se il pagamento arriva mentre il relativo flag è disattivato, il messaggio è preceduto
da un avviso esplicito ([[Blocco dei pagamenti]]).

## Storia / claim superate

> [!warning] Sostituito da fonte più attendibile
> [[Integrazione sistema pagamenti]] prevedeva scadenza calcolata come
> `data_scadenza + durata` con `data_iscrizione` riscritta al valore precedente della scadenza, e
> un limite di rinnovo di 5 giorni. Il codice attuale usa la logica descritta sopra e un ritardo
> configurabile (`N_GIORNI_DOPO_SCADENZA`, oggi 3). **Vale il codice.**

## Voci correlate
- [[Utente]]
- [[Ruoli Discord]]
- [[Batch verifica abbonamenti]]
- [[Sostegno libero]]
