---
tipo: concetto
titolo: Bilanciamento degli account Stripe
alias: [doppio Stripe, ripartizione Stripe, StripeAccountSelector]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-08-13
stato: stabile
---

# Bilanciamento degli account Stripe

Il sistema incassa su **due account Stripe distinti**, `PRIMARIO` e `SECONDARIO`, e sceglie
automaticamente dove indirizzare ogni nuovo pagamento per rispettare una **ripartizione
configurabile** degli incassi.

- **PRIMARIO** — l'account storico. Tutte le righe Stripe preesistenti sono migrate a questo valore.
- **SECONDARIO** — il secondo account, aggiunto per ripartire gli incassi.

> [!note] Nomi cambiati il 2026-08-12
> Fino ad allora i due valori portavano i nomi delle persone titolari dei conti (`LILLO`, `DANNY`):
> dati di una singola istanza dentro uno schema di prodotto. La migration `V8` ha convertito enum,
> colonne e path del webhook ([[Schema del database]]).

## Il criterio di scelta

```
netto(account) = somma pagamenti COMPLETED di quell'account
               − somma prelievi COMPLETATI di quell'account

quota secondario = netto(SECONDARIO) / (netto(PRIMARIO) + netto(SECONDARIO))

quota < PERCENTUALE_STRIPE_SECONDARIO  →  SECONDARIO      altrimenti  →  PRIMARIO
```

Si ragiona sugli **euro**, non sul numero di transazioni: `30` significa «il 30% del denaro
incassato», non «3 pagamenti su 10».

⚠️ **Il singolo pagamento non viene mai diviso fra i due conti.** Stripe crea il checkout con la
chiave di un solo account: la percentuale può agire solo su come i pagamenti si distribuiscono nel
tempo, mai dentro il pagamento stesso. Dividere un incasso richiederebbe Stripe Connect con
application fee, il modello accantonato ([[Sistema masterclass]]).

**Con la percentuale a 50 il comportamento è quello storico**: `quota < 50%` equivale a «netto
secondario minore del primario». La ripartizione paritaria è il caso particolare, non una modalità
separata.

### Il primo pagamento va al primario

Con entrambi i netti a zero la quota non è calcolabile — non è una parità da dirimere, è una
divisione per zero. In quel caso si sceglie il **primario**. Vale al primo incasso in assoluto e
ogni volta che si è prelevato tutto da entrambi i conti.

### Cosa succede in pratica

Con lo storico sul primario e il secondario a zero, la prima fase **non è alternata**: tutti i
pagamenti vanno al secondario finché non raggiunge la sua quota. Solo dopo comincia l'alternanza,
con la cadenza dettata dalla percentuale (al 30%, circa un pagamento su tre).

Esempio con pagamenti da 40 € e obiettivo 30%:

| Pagamento | Quota secondario prima | Va su | PRIMARIO | SECONDARIO |
|---|---|---|---|---|
| 1° | — (tutto a zero) | PRIMARIO | 40 € | 0 € |
| 2° | 0% | SECONDARIO | 40 € | 40 € |
| 3° | 50% | PRIMARIO | 80 € | 40 € |
| 4° | 33,3% | PRIMARIO | 120 € | 40 € |
| 5° | 25% | SECONDARIO | 120 € | 80 € |
| 6° | 40% | PRIMARIO | 160 € | 80 € |
| 7° | 33,3% | PRIMARIO | 200 € | 80 € |
| 8° | 28,6% | SECONDARIO | 200 € | 120 € |

I [[Prelievo|prelievi]] entrano nel conto: registrarne uno su un account ne abbassa la quota e lo
rimette in gioco per gli incassi successivi. È la leva per pilotare il flusso.

## Due limiti da conoscere

**La scelta avviene quando si genera il link**, non quando l'utente paga: quindi senza sapere
ancora l'importo. Con importi molto diversi fra loro la quota oscilla attorno all'obiettivo invece
di restarci incollata — un pagamento promozionale da 130 € assegnato a un conto che era appena
sotto quota può portarlo parecchio sopra, e servono diversi pagamenti sull'altro per riequilibrare.

**I saldi sono quelli registrati a database**, non quelli reali dei conti Stripe. Rimborsi, storni o
prelievi fatti dal cruscotto Stripe senza registrarli con il comando admin non entrano nel calcolo:
la ripartizione continuerebbe a credere che quel denaro sia ancora dov'era.

## Valori fuori intervallo

Una percentuale sotto 0 o sopra 100 viene **ignorata** e si ricade sul 50%, con un warning nei log.
Un `150` inserito per errore dirotterebbe altrimenti ogni pagamento sul secondario per sempre,
senza che nulla lo segnali.

## La guardia di sicurezza

Se il secondo account **non è configurato** (manca la secret key o il webhook secret), il selettore
non tenta nemmeno il calcolo: instrada tutto sul `PRIMARIO` e lo scrive nel log. Questo rende sicuro
il deploy del doppio account anche **prima** di inserire le chiavi.

⚠️ Prima di valorizzare le chiavi del secondario va **registrato il suo webhook su Stripe**. Se si
attivano le chiavi senza registrare l'endpoint, il cliente paga ma la notifica non arriva mai:
nessuna riga in `pagamenti`, nessun ruolo assegnato ([[Idempotenza dei webhook]]).

## Isolamento delle chiavi

La `Stripe.apiKey` globale resta quella del primario (retrocompatibilità). Tutte le chiamate del
flusso a doppio account passano invece `RequestOptions` con la chiave dell'account corretto —
creazione della sessione, `PaymentIntent.retrieve`, `Customer.retrieve`,
`BalanceTransaction.retrieve`. Un evento del secondario non viene mai interrogato con la chiave del
primario.

## Due endpoint webhook separati

| Account | Endpoint | Firma verificata con |
|---|---|---|
| PRIMARIO | `/api/webhooks/stripe` (invariato) | webhook secret del primario |
| SECONDARIO | `/api/webhooks/stripe/secondario` | webhook secret del secondario |

L'account viene dedotto **dall'endpoint chiamato**, non dal metadata della sessione: un metadata è
falsificabile, il percorso no. Il metadata `stripe_account` viene comunque scritto, come ridondanza
di verifica.

Se un endpoint riceve una chiamata ma le chiavi di quell'account mancano, risponde **400** e non
500: un 500 farebbe ritentare Stripe per giorni (retry-storm) su un endpoint inutilizzabile.

## Dove si vede il risultato

Il report saldo del menu `!Admin` mostra **tre sezioni**: Crypto, Stripe Primario, Stripe
Secondario. Le due sezioni Stripe riportano nel titolo la **quota attuale e l'obiettivo**:

```
🔸 STRIPE PRIMARIO — 62,50% (obiettivo 70%)
🔸 STRIPE SECONDARIO — 37,50% (obiettivo 30%)
```

Così si sa in anticipo dove andrà il prossimo pagamento: qui il secondario è sopra il suo obiettivo,
quindi toccherà al primario. Quando non c'è nulla da ripartire i titoli restano senza percentuale,
invece di mostrare uno 0% fuorviante. Vedi [[Reportistica]].

## Voci correlate
- [[Pagamenti Stripe]]
- [[Prelievo]]
- [[Chiavi Stripe]]
- [[Tabella cfg_server]]
- [[Piano sviluppo doppio Stripe]]
