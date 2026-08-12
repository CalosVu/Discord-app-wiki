---
tipo: fonte
titolo: Guida Stripe CLI
alias: [GUIDA_STRIPE_CLI_FORWARD]
tag: [fonte/documento, dominio/pagamenti]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Guida Stripe CLI

Guida al testing in locale dei webhook Stripe tramite la CLI ufficiale. **Fonte di rango 4**.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/GUIDA_STRIPE_CLI_FORWARD.md` (~10 KB)
- **Data:** agosto 2025
- **Binario:** `${DISCORD_APP_DOCS}/stripe_1.29.0_windows_x86_64/`

## Il problema che risolve

Stripe invia i webhook solo a **URL pubblici**: non può raggiungere `localhost:8080`. La CLI crea un
tunnel fra Stripe Cloud e la macchina di sviluppo.

## Sequenza operativa

1. `stripe login` — autorizzazione via browser.
2. `stripe listen --events=checkout.session.completed,charge.updated --forward-to localhost:8080/api/webhooks/stripe`
3. La CLI stampa un **signing secret temporaneo** (`whsec_…`): va messo nella variabile del webhook
   secret e l'app va **riavviata** (vedi [[Variabili d'ambiente]]).
4. Da un secondo terminale: `stripe trigger checkout.session.completed`, oppure un pagamento reale
   con carta di test `4242 4242 4242 4242` (rifiutata: `4000000000000002`).

I listener della CLI sono **temporanei**: spariscono chiudendo il comando e non compaiono nel
Dashboard.

## Varianti per i flussi di questo progetto

- **Supporter, secondo account:** puntare il forward a `/api/webhooks/stripe/danny` usando la chiave
  di quell'account (vedi [[Bilanciamento degli account Stripe]]).
- **Masterclass, modello attivo "direct":** un endpoint per relatore →
  `--forward-to localhost:8080/api/webhooks/stripe/masterclass/relatore/{relatoreId}` con la chiave
  di quel relatore.
- **Masterclass, modello Connect (congelato):** serve `--forward-connect-to`, perché gli eventi
  avvengono sui connected account.

## Avvertenza sull'ambiente

Tutto deve stare nella **stessa sandbox**: chiave usata da `stripe listen`, chiave dell'app e
connected account. Mescolare sandbox diverse produce errori difficili da diagnosticare (il conto
"non risulta connesso alla piattaforma").

## Voci correlate
- [[Fonti]]
- [[Pagamenti Stripe]]
- [[Sistema masterclass]]
