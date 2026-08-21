---
tipo: modulo
titolo: Reportistica
alias: [report, saldi, ReportService]
tag: [dominio/admin]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-20
stato: stabile
---

# Reportistica

I calcoli finanziari dietro ai report del menu `!Admin` ([[Comandi admin]]).

## Chi può aprirli

Le tre voci economiche — Report Saldo, Report Pagamenti, Report Completo — rispondono solo a chi
compare in `REPORT_UTENTI_AUTORIZZATI` ([[Tabella cfg_server]], migration `V35`). **Elenco vuoto =
tutti gli amministratori**, come per [[Prelievo|prelievi]] e
[[Notifiche agli amministratori|notifiche]]; le tre chiavi sono indipendenti fra loro.

Gli altri report del menu — scadenze del mese, agenti, masterclass — restano accessibili a chiunque
sia amministratore.

Il controllo sta **dentro ogni handler** (`AutorizzazioniAdminService.puoVedereReport`), non solo
nel menu: nascondere una voce è cortesia verso chi non deve usarla, ma un componente Discord già
inviato resta cliccabile anche dopo che il menu è cambiato.

## Le formule

```
saldo(metodo)      = Σ payments.importo (COMPLETED, metodo, ≤ data)
                   − Σ track_prelievi.importo (COMPLETATO, metodo, ≤ data)

saldo(account)     = come sopra, filtrando anche stripe_account

saldo netto periodo = Σ pagamenti nel range − Σ prelievi nel range
```

Tutti i filtri sono su `stato_verifica = 'COMPLETED'` per i [[Pagamento|pagamenti]] e
`stato_prelievo = 'COMPLETATO'` per i [[Prelievo|prelievi]].

## I tre report

| Report | Risponde a | Contenuto |
|---|---|---|
| **Report Saldo** | «quanto ho **adesso**» | Crypto (USDT) e Stripe (EUR), ognuno con depositi, prelievi, saldo. Nessuna data |
| **Report Pagamenti** | «**chi** ha pagato di recente» | l'elenco dei pagamenti del periodo — data, utente, importo, canale, abbonamento o donazione, email dell'account che ha pagato — dal più recente. In coda i totali per canale |
| **Report Completo** | «**come è andato** il periodo» | entrate per canale con media e confronto sul periodo precedente, composizione (abbonamenti / donazioni), prelievi, saldo del periodo, movimento degli utenti |

I due report a periodo **non si sovrappongono**: uno elenca fatti, l'altro li riassume.

### Con un solo conto Stripe il secondo non compare

Finché `STRIPE_SECONDARIO_SECRET_KEY` e il relativo webhook secret non sono valorizzati, il
secondo account **non esiste per l'interfaccia**: il Report Saldo mostra un'unica sezione
`🔸 STRIPE` (totale del canale, senza filtro per account, così rientrano anche i movimenti
registrati prima che gli account esistessero), il Report Completo non mostra la ripartizione fra i
conti, e il menu dei [[Prelievo|prelievi]] offre una sola voce «Stripe · EUR». Vale per tutti i
comandi: un conto che non c'è non va nominato.

### La ripartizione nel titolo delle sezioni Stripe (solo con due conti)

```
🔸 STRIPE PRIMARIO — 62,50% (obiettivo 70%)
🔸 STRIPE SECONDARIO — 37,50% (obiettivo 30%)
```

La percentuale è la quota di quell'account sul **saldo netto complessivo** dei due conti Stripe;
l'obiettivo è `PERCENTUALE_STRIPE_SECONDARIO` ([[Tabella cfg_server]]). Serve a sapere in
anticipo dove finirà il prossimo pagamento: nell'esempio il secondario è sopra il suo obiettivo,
quindi toccherà al primario ([[Bilanciamento degli account Stripe]]).

Quando non c'è nulla da ripartire — nessun incasso, o tutto prelevato — i titoli restano senza
percentuale, invece di mostrare uno `0%` che farebbe pensare a uno sbilanciamento inesistente.

## Il movimento degli utenti nel Report Completo

| Voce | Come si ottiene |
|---|---|
| Nuovi iscritti nel periodo | `countByDataPrimaIscrizioneBetween(inizio, fine)` |
| Rinnovi nel periodo | transazioni di tipo `SUPPORTER_MEMBER` meno i nuovi iscritti (mai negativo) |
| Abbonati attivi oggi | `countByDataScadenzaIscrizioneAfter(adesso)` — **fotografia del momento**, non del periodo |

I rinnovi sono una sottrazione, non un conteggio: chi si iscrive e rinnova **dentro lo stesso
periodo** viene contato una volta sola fra i nuovi. Su periodi mensili la differenza è trascurabile;
su periodi lunghi il numero dei rinnovi è per difetto.

## Il confronto col periodo precedente

Le entrate di ogni canale portano la variazione rispetto al periodo immediatamente precedente **di
pari durata**: un intervallo di 30 giorni si confronta con i 30 giorni prima. Quando il periodo
precedente è a zero la variazione **non viene mostrata**, invece di stampare un `+100%` che da zero
non significa nulla.

## Incassi ancora al lordo

Se nel periodo ci sono pagamenti Stripe con `fee_pending = true`, il Report Completo lo dice in
testa: quegli importi sono ancora lordi e il totale scenderà quando `charge.updated` li riconcilia
([[Riconciliazione della fee Stripe]]). Senza l'avviso un totale provvisorio si legge come
definitivo.

## Le valute non si sommano

Crypto in **USDT**, Stripe in **EUR**. Non esiste conversione né totale unico: i due mondi restano
sempre affiancati. Vale anche per i report agenti ([[Comandi agenti]]).

## Come si sceglie il periodo

Discord **non ha un selettore di date**: dentro una finestra modale esistono solo campi di testo.
Per questo i due report a periodo mostrano prima un menu di intervalli pronti, e chiedono di
scrivere le date solo per l'ultima voce:

| Voce | Intervallo |
|---|---|
| Mese corrente | dal primo del mese a oggi |
| Mese precedente | il mese scorso, per intero |
| Ultimi 30 giorni | da `oggi − 29` a oggi (trenta giorni, oggi compreso) |
| Anno corrente | dal primo gennaio a oggi |
| Anno precedente | l'anno scorso, per intero |
| Periodo personalizzato… | apre la finestra con `Data Inizio` e `Data Fine` |

Le etichette portano il mese e l'anno già risolti — «Mese precedente (luglio 2026)» — così non
serve contare. La logica sta in `PeriodoReport` ([[Comandi admin]]).

## Validazione delle date

`DateValidator.validateAndConvertDateRange` impone:

- formato `gg/mm/aaaa` (regex rigida);
- data di fine **non nel futuro**;
- inizio ≤ fine.

L'inizio è portato a `00:00:00`, la fine a `23:59:59.999999999`.

> [!info] Il limite di un anno è stato tolto il 2026-08-21
> Un inizio anteriore a un anno fa veniva rifiutato con *«La data di inizio non può essere superiore
> a 1 anni fa»*. Non proteggeva nulla — sono somme su poche centinaia di righe — e vietava la
> domanda più normale che si faccia a un report contabile: com'è andato l'anno scorso. Con la voce
> «Anno precedente» nel menu sarebbe stato un blocco che contraddice sé stesso.

Nello stesso passaggio la conferma è stata spostata **dopo** la validazione: il bot rispondeva
«✅ Dati ricevuti con successo!» appena letti i campi, e un istante dopo mandava l'errore che diceva
il contrario.

## ⚠️ Il saldo è ricalcolato ogni volta

Non esiste uno storico: ogni lettura riscorre l'intero `pagamenti` e `pagamenti_prelievi`. Con i volumi
attuali è irrilevante, ma è il motivo per cui esisteva l'idea degli
[[Snapshot bilancio]] — funzionalità mai attivata.

Un'altra conseguenza: i saldi **cambiano retroattivamente** quando un pagamento viene riconciliato
da lordo a netto ([[Riconciliazione della fee Stripe]]).

## Metodi presenti ma non raggiungibili dal bot

`ReportService` espone ancora `generaReportUtentePersonalizzato` (storico pagamenti di un singolo
utente), che nessun comando richiama.

`calcolaStatisticheGenerali` è stato **rimosso il 2026-08-20**: sommava Crypto e PayPal — un canale
mai gestito da questa applicazione — e non lo chiamava nessuno. Nella stessa occasione sono spariti
`generaReportPagamenti`, `generaReportCompleto` e il DTO `ReportCompletoDto`, sostituiti da
`riepilogoCanale` + `RiepilogoCanaleDto`: il vecchio DTO descriveva un singolo pagamento e nel tempo
si era riempito di campi di totale, con metà dei valori sempre a zero. I due metodi calcolavano
inoltre l'intero elenco dei pagamenti convertito in DTO a ogni chiamata, elenco che nessun embed
mostrava.

## Il bug della valuta (chiuso il 2026-08-20)

Il Report Completo stampava il saldo Crypto usando la valuta di Stripe:

```java
String.format("%.2f %s", crypto.getSaldoNetto(), stripe.getValuta())   // → "1.234,00 EUR" su USDT
```

Nello stesso passaggio il campo si chiamava «💰 SALDI DISPONIBILI» ma conteneva entrate meno uscite
**del solo periodo**: ora l'etichetta è «Saldo del periodo» e rimanda esplicitamente al Report Saldo
per il saldo dei conti.

## Voci correlate
- [[Comandi admin]]
- [[Pagamento]]
- [[Prelievo]]
- [[Bilanciamento degli account Stripe]]
