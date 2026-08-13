---
tipo: tassonomia
titolo: Enum di dominio
alias: [enum, PaymentMethod, PaymentStatus, StatoPrelievo, StripeAccount]
tag: [dominio/tassonomie]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Enum di dominio

I valori codificati del sistema, con l'indicazione di quali sono **realmente prodotti** dal codice e
quali esistono solo come possibilità.

## `PaymentMethod`

| Valore | Usato? |
|---|---|
| `CRYPTO` | ✅ [[Pagamenti crypto Arbitrum]] |
| `STRIPE` | ✅ [[Pagamenti Stripe]] |
| `PAYPAL` | ❌ **mai prodotto** — nessuna integrazione PayPal esiste |

`PAYPAL` sopravvive nell'enum e nelle DDL. Compare in `ReportService.calcolaStatisticheGenerali`, che
somma Crypto + PayPal — metodo però non raggiungibile da alcun comando ([[Reportistica]]).

Traccia dell'intenzione originale documentata in [[DOC_PROGETTO]].

## `PaymentStatus`

| Valore | Usato? |
|---|---|
| `COMPLETED` | ✅ l'unico realmente scritto |
| `PENDING` | ❌ mai scritto |
| `FAILED` | ❌ mai scritto |

Vale sia per `pagamenti` (su **due** colonne, `stato_verifica` e `status`) sia per
`masterclass_pagamenti`. Un pagamento fallito semplicemente **non produce una riga**: l'esito
negativo di una verifica crypto finisce in [[Tentativo di verifica transazione]], non in `pagamenti`.

⚠️ Le query di bilancio filtrano su **`stato_verifica`**: è quel campo che va usato nelle nuove query.

## `StatoPrelievo`

| Valore | Etichetta | Usato? |
|---|---|---|
| `COMPLETATO` | Completato | ✅ l'unico scritto |
| `IN_ATTESA` | In Attesa | ❌ |
| `IN_ELABORAZIONE` | In Elaborazione | ❌ |
| `FALLITO` | Fallito | ❌ |

L'enum ha etichette, descrizioni e metodi (`isCompletato`, `isFallito`, `isInElaborazione`) mai
usati. Tutte le somme dei prelievi filtrano su `COMPLETATO` ([[Prelievo]]).

## `StripeAccount`

| Valore | Significato |
|---|---|
| `PRIMARIO` | account storico; tutte le righe Stripe preesistenti sono state migrate qui |
| `SECONDARIO` | secondo account, per ripartire gli incassi |

`NULL` sulle righe crypto. Vedi [[Bilanciamento degli account Stripe]].

⚠️ In DDL **deve** essere `ENUM('PRIMARIO','SECONDARIO')`, non `VARCHAR`: con `ddl-auto: validate`
una colonna `VARCHAR` fa **fallire il boot** ([[Schema del database]]).

I valori si chiamavano `LILLO` e `DANNY` fino al 2026-08-12: erano i nomi dei titolari dei conti, e
la migration `V8` li ha resi neutri.

## `MotivoPendenza`

Perché l'attribuzione del referral non è riuscita ([[Referral pendente]]).

| Valore | Significato | `recuperabile` |
|---|---|---|
| `NESSUN_DELTA` | nessun invito risultava incrementato: contatore non ancora propagato da Discord | `true` |
| `AMBIGUO` | più inviti incrementati, o meno incrementi che utenti in attesa | `false` |

Il flag `recuperabile` non è decorativo: è quello che decide se scattano i **retry automatici** a 2, 5
e 15 secondi. Su un caso ambiguo riprovare non aggiungerebbe informazione.

## `Payments.TransactionType`

Enum interno all'entità:

| Valore | Quando |
|---|---|
| `SUPPORTER_MEMBER` | [[Abbonamento Supporter Member]] |
| `GOLD_SUPPORTER_MEMBER` | [[Sostegno libero]] |

## `snapshot_bilancio.metodo_pagamento`

Caso a parte: la DDL ammette solo `ENUM('CRYPTO','PAYPAL')` — **manca `STRIPE`**. Irrilevante finché
la funzionalità resta disattivata ([[Snapshot bilancio]]), ma va corretto prima di riattivarla.

## Voci correlate
- [[Schema del database]]
- [[Pagamento]]
- [[Prelievo]]
