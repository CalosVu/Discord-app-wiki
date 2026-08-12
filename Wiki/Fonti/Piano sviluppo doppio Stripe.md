---
tipo: fonte
titolo: Piano sviluppo doppio Stripe
alias: [PianoSviluppoDoppioStripe]
tag: [fonte/documento, dominio/pagamenti]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Piano sviluppo doppio Stripe

Documento di piano del branch `feature/doppioStripe`, oggi **mergiato su `main`**. **Fonte di
rango 3**: spiega il *perché* del bilanciamento fra due conti Stripe e dei flag di blocco pagamenti.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/PianoSviluppoDoppioStripe.md` (~16 KB)
- **Data:** luglio 2026
- **Stato dichiarato:** tutte le fasi ✅ completate, build con test verdi

## Le tre cose che ha portato

1. **Doppio account Stripe** (Lillo + Danny) con instradamento per **saldo netto** →
   [[Bilanciamento degli account Stripe]].
2. **Flag di blocco pagamenti** granulari in `server_config`, **cross-canale** (Stripe + Crypto) →
   [[Blocco dei pagamenti]].
3. **Fix della notifica admin** sulla donazione libera: il ramo `else` di
   `aggiornaAbbonamentoUtente` assegnava il ruolo ma non chiamava `notificaAdmin` →
   [[Sostegno libero]].

## Decisioni consolidate

- Criterio di selezione: **saldo netto minore** (`depositi − prelievi` per account); a parità o se
  Danny è maggiore → **LILLO** (tie-break deterministico).
- Webhook: **endpoint separati per account** (opzione A1). Quello di Lillo resta invariato.
- Flag di blocco: **un solo flag per tipo operazione**, valido su entrambi i canali. Non si sdoppia
  per canale.
- Storico: tutte le righe Stripe preesistenti (`payments` e `track_prelievi`) migrate a `LILLO`.
- La `Stripe.apiKey` globale **non si tocca** (resta Lillo): le chiamate per-account usano
  `RequestOptions.setApiKey(...)`.

## Vincolo di migrazione da ricordare

> ⚠️ La colonna `stripe_account` **deve** essere `ENUM('LILLO','DANNY')`, non `VARCHAR`: con
> `ddl-auto: validate` in produzione, Hibernate 6 mappa gli enum Java su `ENUM` nativo e una
> colonna `VARCHAR` fa **fallire il boot**. Vedi [[Schema del database]].

## Raccomandazioni lasciate aperte

Riportate qui perché non sono regressioni introdotte, ma debito noto:

- **[MEDIA]** L'idempotenza del webhook non è atomica: la difesa vera sarebbe un `UNIQUE` su
  `payments.stripe_session_id`. Ostacolo: le righe crypto salvano `stripe_session_id = ""` → prima
  vanno migrate a `NULL`. Vedi [[Idempotenza dei webhook]].
- **[MEDIA, teorica]** Le query di riconciliazione fee non filtrano per account; in pratica
  irrilevante perché gli id PaymentIntent sono univoci globalmente.
- **[INFO]** In `application.yml` restano, nei commenti, chiavi Stripe **di test**: da rimuovere.
- **[test]** Manca un test per `ReportService.calcolaSaldoStripeAccount`.

## Voci correlate
- [[Fonti]]
- [[Bilanciamento degli account Stripe]]
- [[Blocco dei pagamenti]]
