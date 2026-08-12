---
tipo: concetto
titolo: Idempotenza dei webhook
alias: [idempotenza, retry Stripe, doppio accredito]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Idempotenza dei webhook

Stripe **ritenta** la consegna di un webhook — fino a 3 giorni — ogni volta che riceve una risposta
diversa da 2xx o un timeout. Senza protezione, lo stesso pagamento verrebbe registrato più volte:
doppio accredito, doppio rinnovo, doppia commissione.

## Le protezioni in campo

| Flusso | Protezione | Livello |
|---|---|---|
| Supporter (Stripe) | `existsByStripeSessionId(sessionId)` prima di processare | applicativo |
| Masterclass | `existsByStripeSessionId(sessionId)` + `UNIQUE` su `stripe_session_id` | applicativo **+ database** |
| Masterclass | `UNIQUE (user_id, masterclass_id)` | database |
| Crypto | `tx_hash UNIQUE` + `findByHashTransazione` prima della verifica | applicativo **+ database** |
| Commissioni | `existsByPaymentId` | applicativo |
| Riconciliazione fee | query filtrata su `fee_pending = true` | applicativo |

## ⚠️ Il punto debole: i pagamenti supporter

Per il flusso supporter la protezione è **solo applicativa**: `payments.stripe_session_id` non ha un
vincolo `UNIQUE`. Fra il controllo e l'inserimento c'è una finestra in cui due consegne concorrenti
dello stesso evento possono passare entrambe.

La difesa vera sarebbe un indice unico, ma è **bloccata da un dettaglio dei dati**: le righe crypto
salvano `stripe_session_id = ""` (stringa vuota, non `NULL`), quindi un `UNIQUE` le farebbe
collidere tutte fra loro. Per introdurlo servirebbe prima migrare quelle righe a `NULL`.

È un debito noto e tracciato (fonte: [[Piano sviluppo doppio Stripe]], raccomandazione [MEDIA]).

## Come rispondere agli errori

Regola applicata negli endpoint: **400, non 500**, quando la richiesta non è processabile per
configurazione (account non configurato, firma non valida, relatore senza chiavi). Un 500 innesca i
retry di Stripe per giorni su un endpoint che non potrà mai funzionare — un retry-storm inutile.

I casi che invece **devono** dare errore e far ritentare Stripe sono i guasti transitori (database
irraggiungibile): lì l'eccezione propaga e il retry ha senso.

## Il caso del doppio acquisto masterclass

Se il vincolo `UNIQUE (user_id, masterclass_id)` scatta, il codice **non erroga di nuovo il
contenuto** e manda agli admin un messaggio esplicito che invita a **valutare il rimborso** del
secondo pagamento. È l'unico punto in cui il sistema segnala attivamente una possibile restituzione.

## Voci correlate
- [[Pagamenti Stripe]]
- [[Riconciliazione della fee Stripe]]
- [[Pagamento masterclass]]
