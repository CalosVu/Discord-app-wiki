---
tipo: concetto
titolo: Idempotenza dei webhook
alias: [idempotenza, retry Stripe, doppio accredito]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-08-18
stato: stabile
---

# Idempotenza dei webhook

Stripe **ritenta** la consegna di un webhook — fino a 3 giorni — ogni volta che riceve una risposta
diversa da 2xx o un timeout. Senza protezione, lo stesso pagamento verrebbe registrato più volte:
doppio accredito, doppio rinnovo, doppia commissione.

## Le protezioni in campo

| Flusso | Protezione | Livello |
|---|---|---|
| Supporter (Stripe) | `existsByStripeSessionId(sessionId)` + `UNIQUE` su `stripe_session_id` (`V31`) | applicativo **+ database** |
| Masterclass | `existsByStripeSessionId(sessionId)` + `UNIQUE` su `stripe_session_id` | applicativo **+ database** |
| Masterclass | `UNIQUE (user_id, masterclass_id)` | database |
| Crypto | `tx_hash UNIQUE` + `findByHashTransazione` prima della verifica | applicativo **+ database** |
| Commissioni | `existsByPaymentId` | applicativo |
| Riconciliazione fee | query filtrata su `fee_pending = true` | applicativo |

## Perché il controllo applicativo da solo non basta

`existsByStripeSessionId` è un **check-then-act**: prima si guarda se la riga esiste, poi la si
scrive. Nel flusso supporter, fra i due momenti passano fino a tre secondi — due
`PaymentIntent.retrieve` verso Stripe con un `Thread.sleep(1500)` in mezzo per recuperare la
commissione. Due consegne concorrenti dello stesso evento superano entrambe il controllo, perché
nessuna delle due ha ancora scritto, e finiscono entrambe con un `INSERT`.

Il risultato non è un doppione innocuo: `savePaymentAndUpdateUser` **somma i mesi alla scadenza**,
quindi l'utente ottiene il doppio del periodo pagato, e il report dei profitti conta due incassi.

Fino alla `V31` il flusso supporter aveva solo il controllo applicativo, ed era bloccato da un
dettaglio dei dati: i pagamenti crypto salvavano `stripe_session_id = ""` — stringa vuota, non
`NULL` — quindi un `UNIQUE` le avrebbe fatte collidere fra loro. La migration normalizza lo storico
a `NULL` (che in MySQL può ripetersi) e il codice ora passa `null` per le crypto.

### Il doppio accredito era già successo

Applicando la `V31` la migration **è fallita**: in `pagamenti` c'erano già due righe per la stessa
sessione Stripe.

| | |
|---|---|
| Righe | `71` e `73`, stesso importo **49,00 €**, stesso utente |
| Date | 2025-09-13 19:44 e 2025-09-14 **02:47**, sette ore dopo |
| Effetto | un incasso contato due volte, abbonamento prolungato del doppio |

Le sette ore escludono la corsa fra due retry concorrenti: è un retry tardivo di Stripe, arrivato
quando **non esisteva ancora nessun controllo** — `existsByStripeSessionId` è del 2026-06-13, nove
mesi dopo.

Per bonificare: `utenti.payment_id` va prima spostato sulla riga da tenere (le chiavi esterne sono in
`RESTRICT`, quindi una riga referenziata non si cancella), poi si rimuove l'eventuale commissione
collegata e infine la riga spuria.

> [!warning] Come NON leggere la query dei duplicati
> Raggruppando su `stripe_session_id IS NOT NULL` compaiono anche **decine di righe crypto** che
> condividono la stringa vuota `''`. **Non sono duplicati**: le normalizza a `NULL` il primo
> statement della migration. Per isolare i duplicati veri serve `AND stripe_session_id <> ''`.

### Cosa succede quando il vincolo scatta

L'ordine dentro `savePaymentAndUpdateUser` è la parte che conta: il pagamento si scrive **prima** di
toccare l'abbonamento, quindi il rifiuto del vincolo interrompe il metodo prima che la scadenza
venga prolungata una seconda volta.

`StripePaymentNotificationService` cattura la `DataIntegrityViolationException` e **non la rilancia**:
è un retry riconosciuto, non un guasto. Rilanciarla farebbe rispondere male al webhook, e Stripe
continuerebbe a ritentare per giorni un evento già andato a buon fine. L'utente non riceve un secondo
DM di conferma: gliel'ha già mandato la prima esecuzione.

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
