---
tipo: entita
titolo: Pagamento masterclass
alias: [pagamenti_masterclass, PagamentoMasterclass]
tag: [dominio/masterclass, dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Pagamento masterclass

L'acquisto di una [[Masterclass]] da parte di un [[Utente]]. Tabella `masterclass_pagamenti`,
tenuta **separata** da `pagamenti` perché i campi non sono pertinenti (nessun wallet, nessun ruolo da
assegnare).

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `masterclass`, `relatore`, `user` | `masterclass_id`, `relatore_id`, `user_id` | `relatore_id` è **denormalizzato** per i report |
| `discordIdAcquirente`, `usernameAcquirente` | omonime | snapshot dell'acquirente |
| `importoLordo` | `importo_lordo` | quanto ha pagato l'acquirente |
| `commissioniServer` | `commissioni_server` | quota server = `lordo × percentuale_server / 100` |
| `commissioneStripe` | `commissione_stripe` | fee Stripe reale; `0` finché `fee_pending` |
| `importoNettoRelatore` | `importo_netto_relatore` | `lordo − commissioni_server − fee` |
| `percentualeApplicata` | `percentuale_applicata` | snapshot della % al momento dell'acquisto |
| `stripeSessionId` | `stripe_session_id` | `UNIQUE` → [[Idempotenza dei webhook]] |
| `stripePaymentIntentId` | `stripe_payment_intent_id` | correlazione con `charge.updated` |
| `feePending` | `fee_pending` | `true` = importi ancora provvisori |
| `stato` | `stato` | in pratica sempre `COMPLETED` |
| `dataPagamento` | `data_pagamento` | ora italiana della registrazione |
| `dataUpdate` | `data_update` | ultima scrittura; ex `created_at` (`V20`). Cambia con la riconciliazione della fee, quindi **non** coincide con `data_pagamento` |

## ⚠️ Gli importi sono teorici, non contabili

Nel modello attivo ("chiave per relatore", nessun Stripe Connect) **il server non trattiene nulla**:
l'incasso arriva interamente sull'account Stripe del relatore.

| Campo | Significato reale |
|---|---|
| `importo_lordo` | ✅ reale — quanto ha pagato l'acquirente |
| `commissione_stripe` | ✅ reale — letta dal balance transaction |
| `commissioni_server` | ⚠️ **teorico** — calcolato ma mai incassato |
| `importo_netto_relatore` | ⚠️ **teorico** — il relatore incassa davvero `lordo − stripe_fee` |

I campi restano popolati perché il codice sia pronto se un domani si riattivassero le commissioni
(vedi [[Piano sviluppo masterclass]] §13.3). Per la contabilità reale va letto **solo il lordo**.

Nel modello Connect (congelato) gli stessi campi sarebbero invece tutti reali, perché
l'`application_fee` viene realmente accreditata alla piattaforma.

## Doppia protezione contro il doppio acquisto

1. **Applicativa**, prima del checkout: `existsByUserIdAndMasterclassIdAndStato(..., COMPLETED)` →
   l'utente riceve «Hai già acquistato questa masterclass».
2. **Database**: vincolo `UNIQUE (user_id, masterclass_id)`. Se un doppio pagamento sfugge al primo
   controllo, l'inserimento fallisce, il contenuto **non** viene erogato di nuovo e gli admin
   ricevono una notifica esplicita che invita a **valutare il rimborso**.

## Voci correlate
- [[Masterclass]]
- [[Sistema masterclass]]
- [[Riconciliazione della fee Stripe]]
