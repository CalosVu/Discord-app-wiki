---
tipo: entita
titolo: Snapshot bilancio
alias: [snapshot_bilancio, SnapshotBilancio]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-13
stato: obsoleto
---

# Snapshot bilancio

> [!warning] Eliminato il 2026-08-13
> Tabella, entità, repository e batch **non esistono più**: rimossi dalla migration `V11` e dal
> commit dello stesso giorno. Questa pagina resta perché il nome ricorre altrove nella wiki e
> perché la storia spiega una scelta — non descrive nulla di presente nel codice.

Doveva essere la fotografia periodica del bilancio (depositi, prelievi, saldo) per metodo di
pagamento, nella tabella `snapshot_bilancio`.

## Perché è stato eliminato

Non è mai stato attivo un solo giorno. L'entità e il repository erano completi e ricchi di query,
ma **tutte commentate**; la classe `SnapshotBilancioBatch` era un guscio vuoto:

```java
@Service @Slf4j @RequiredArgsConstructor @Validated
public class SnapshotBilancioBatch {
}
```

con dodici import inutilizzati e lo `@Scheduled` previsto (`0 0 3 * * MON`, ogni lunedì alle 3:00)
commentato due volte. In produzione la tabella aveva **zero righe**.

Il danno non era il codice inerte ma la documentazione: `CLAUDE.md` e questa wiki lo elencavano fra
i **batch schedulati attivi**, accanto a quello degli abbonamenti. Chi leggeva poteva credere che
esistesse uno storico del bilancio su cui fare affidamento per una riconciliazione.

**Nel progetto esiste un solo `@Scheduled`**: quello delle 22:00 in `VerificaAbbonamentiBatch`
([[Batch verifica abbonamenti]]).

## Se servisse davvero uno storico

Oggi i saldi sono **ricalcolati a runtime** ogni volta, da zero, su `pagamenti` e
`pagamenti_prelievi` ([[Reportistica]]). Con i volumi attuali è irrilevante. Uno storico avrebbe
senso per due ragioni diverse — prestazioni, oppure poter dire *quanto c'era in cassa il 3 marzo* —
e andrebbe riscritto partendo da quel requisito, non recuperando questo codice.

## Com'era la struttura prevista

| Campo | Note |
|---|---|
| `dataSnapshot` + `oraSnapshot` | data e ora della fotografia |
| `totaleDepositi`, `totalePrelievi`, `saldoDisponibile` | i tre numeri del bilancio |
| `valuta`, `metodoPagamento` | ⚠️ l'enum in DDL ammette solo `CRYPTO` e `PAYPAL`: **manca `STRIPE`** |
| `numeroTransazioni`, `numeroUtentiAttivi`, `importoMedioTransazione` | statistiche |
| `variazionePercentuale` | scostamento rispetto allo snapshot precedente |
| `automatico`, `generatoDa`, `noteSnapshot` | provenienza |
| vincolo `UNIQUE (data_snapshot, metodo_pagamento)` | uno snapshot al giorno per metodo |

## I difetti che il progetto originale aveva già

Sono il motivo per cui non conviene recuperarlo, ma riscriverlo:

1. l'enum in DDL ammetteva solo `CRYPTO` e `PAYPAL`: **mancava `STRIPE`**, cioè il canale
   principale non era nemmeno rappresentabile;
2. non era previsto il dettaglio **per account Stripe** (primario/secondario), che invece i saldi
   attuali distinguono ([[Bilanciamento degli account Stripe]]);
3. `contaTransazioni` e `contaUtentiAttivi` ritornavano `0` — statistiche mai implementate.

## Voci correlate
- [[Reportistica]]
- [[Batch verifica abbonamenti]]
- [[Log operativo]]
- [[Schema del database]]
