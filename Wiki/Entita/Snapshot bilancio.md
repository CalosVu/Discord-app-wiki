---
tipo: entita
titolo: Snapshot bilancio
alias: [snapshot_bilancio, SnapshotBilancio]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Snapshot bilancio

Fotografia periodica del bilancio (depositi, prelievi, saldo) per metodo di pagamento. Tabella
`snapshot_bilancio`, entità `SnapshotBilancio`.

## ⚠️ Funzionalità NON attiva

La tabella esiste, l'entità e il repository sono completi e ricchi di query, ma **nessuna riga viene
mai scritta**: l'intera classe `SnapshotBilancioBatch` è **commentata riga per riga**. Al suo interno
resta solo la dichiarazione `@Service` con un corpo vuoto.

Anche lo `@Scheduled` previsto (`0 0 3 * * MON`, ogni lunedì alle 3:00) è commentato.

Chiunque cerchi lo storico del bilancio non lo troverà: esiste solo il **calcolo a runtime** dei
saldi, fatto ogni volta da zero su `payments` e `track_prelievi` ([[Reportistica]]).

## Struttura prevista

| Campo | Note |
|---|---|
| `dataSnapshot` + `oraSnapshot` | data e ora della fotografia |
| `totaleDepositi`, `totalePrelievi`, `saldoDisponibile` | i tre numeri del bilancio |
| `valuta`, `metodoPagamento` | ⚠️ l'enum in DDL ammette solo `CRYPTO` e `PAYPAL`: **manca `STRIPE`** |
| `numeroTransazioni`, `numeroUtentiAttivi`, `importoMedioTransazione` | statistiche |
| `variazionePercentuale` | scostamento rispetto allo snapshot precedente |
| `automatico`, `generatoDa`, `noteSnapshot` | provenienza |
| vincolo `UNIQUE (data_snapshot, metodo_pagamento)` | uno snapshot al giorno per metodo |

## Cosa servirebbe per riattivarla

1. Decommentare la classe e lo `@Scheduled`.
2. **Estendere l'enum in DDL** a `STRIPE`, altrimenti gli snapshot Stripe non sono rappresentabili.
3. Decidere se lo snapshot va **per account Stripe** (primario/secondario) come i saldi attuali, oppure
   aggregato: oggi la colonna non lo prevede ([[Bilanciamento degli account Stripe]]).
4. Implementare `contaTransazioni` e `contaUtentiAttivi`, che nel codice commentato ritornano `0`.

## Voci correlate
- [[Reportistica]]
- [[Prelievo]]
- [[Pagamento]]
