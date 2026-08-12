---
tipo: modulo
titolo: Pagamenti Stripe
alias: [Stripe, checkout, webhook Stripe]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Pagamenti Stripe

Il canale di pagamento con carta: link di **Checkout Session** generati dal bot e webhook che
registra l'incasso. Copre sia l'[[Abbonamento Supporter Member]] sia il [[Sostegno libero]].

## Generazione del link

1. Il selettore sceglie l'account su cui incassare
   ([[Bilanciamento degli account Stripe]]).
2. Si legge la durata di validità da `N_ORE_DURATA_LINK_STRIPE` ([[Tabella server_config]], oggi 5).
3. Si crea la Checkout Session in modalità `PAYMENT`, `SubmitType.DONATE`,
   `CustomerCreation.ALWAYS`, con `expiresAt` calcolato.

| Tipo | Line item | Modificabile |
|---|---|---|
| Supporter Member | prezzo × mesi, quantità 1 | ❌ importo fisso |
| Sostegno Libero | unità da **2,00 €**, quantità regolabile (min. 1) | ✅ dall'utente |

I **metadata** portano `user_id`, `donation_type`, `original_amount`, `id_discord`, `numero_mesi`,
`timestamp`, `currency`, `stripe_account`, `expires_at`. Sono la sola informazione che torna indietro
con il webhook.

## I due endpoint

| Endpoint | Account |
|---|---|
| `POST /api/webhooks/stripe` | LILLO (storico, path invariato) |
| `POST /api/webhooks/stripe/danny` | DANNY |

Entrambi verificano la firma con il webhook secret **di quell'account** e usano la sua chiave per
ogni chiamata alle API. Gli eventi gestiti sono **due soli**: `checkout.session.completed` e
`charge.updated`. Qualunque altro evento viene solo loggato.

## Cosa fa `checkout.session.completed`

1. **Filtro masterclass**: se i metadata contengono `masterclass_id`, l'evento **non** è di questo
   flusso e viene ignorato ([[Sistema masterclass]]).
2. Calcolo dell'importo pagato (`amount_total / 100`).
3. Recupero della fee, con la strategia A del pattern A+B
   ([[Riconciliazione della fee Stripe]]).
4. Recupero dell'email cliente (best effort: un errore non blocca).
5. **Controllo bloccante sull'importo** (solo Supporter Member): se il pagato è inferiore
   all'atteso, **l'accesso non viene concesso** e gli admin ricevono l'avviso «Pagamento
   SupporterMember sospetto». Sovra-pagamenti ammessi.
6. Registrazione: idempotenza sulla session, creazione del [[Pagamento]], aggiornamento
   dell'[[Utente]], assegnazione del ruolo, DM di conferma, notifica admin.

## La pagina di ritorno

`GET /payment/success?session_id=…` e `GET /payment/cancel` restituiscono una pagina HTML di
cortesia con importo, tipo di donazione, mesi e Discord ID.

⚠️ È **solo estetica**: il redirect non è affidabile (l'utente può chiudere il browser). L'unica
fonte di verità è il webhook.

## Storia / claim superate

> [!warning] Sostituito da fonte più attendibile
> [[Guida SSL e DNS]] indicava di registrare gli eventi `payment_intent.succeeded`,
> `payment_intent.payment_failed`, `customer.subscription.created`, `invoice.payment_succeeded`.
> Il codice gestisce **solo** `checkout.session.completed` e `charge.updated`. **Valgono questi
> due** — e `charge.updated` è indispensabile, altrimenti la fee non viene mai riconciliata.

## Voci correlate
- [[Pagamento]]
- [[Bilanciamento degli account Stripe]]
- [[Riconciliazione della fee Stripe]]
- [[Chiavi Stripe]]
