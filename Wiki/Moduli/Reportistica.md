---
tipo: modulo
titolo: Reportistica
alias: [report, saldi, ReportService]
tag: [dominio/admin]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Reportistica

I calcoli finanziari dietro ai report del menu `!Admin` ([[Comandi admin]]).

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

| Report | Contenuto |
|---|---|
| **Report Saldo** | tre sezioni — Crypto (USDT), Stripe **Lillo** (EUR), Stripe **Danny** (EUR) — ognuna con depositi, prelievi, saldo. Nessuna data: è il saldo *ad adesso* |
| **Report Pagamenti** | dato un range: totale e numero transazioni, separati per Crypto e Stripe |
| **Report Completo** | come sopra, più il **saldo netto del periodo** e il numero di **abbonati attivi** |

Il numero di abbonati attivi è `countByDataScadenzaIscrizioneAfter(adesso)`: **non è filtrato per
periodo** né per metodo. Nel Report Completo compare sotto entrambe le sezioni ma è un solo numero
globale — l'etichetta lo segnala («non filtrati per data»).

## Le valute non si sommano

Crypto in **USDT**, Stripe in **EUR**. Non esiste conversione né totale unico: i due mondi restano
sempre affiancati. Vale anche per i report agenti ([[Comandi agenti]]).

## Validazione delle date

`DateValidator.validateAndConvertDateRange` impone:

- formato `gg/mm/aaaa` (regex rigida);
- data di inizio **non oltre 1 anno fa**;
- data di fine **non nel futuro**;
- inizio ≤ fine.

L'inizio è portato a `00:00:00`, la fine a `23:59:59.999999999`.

## ⚠️ Il saldo è ricalcolato ogni volta

Non esiste uno storico: ogni lettura riscorre l'intero `payments` e `track_prelievi`. Con i volumi
attuali è irrilevante, ma è il motivo per cui esisteva l'idea degli
[[Snapshot bilancio]] — funzionalità mai attivata.

Un'altra conseguenza: i saldi **cambiano retroattivamente** quando un pagamento viene riconciliato
da lordo a netto ([[Riconciliazione della fee Stripe]]).

## Metodi presenti ma non raggiungibili dal bot

`ReportService` espone anche `generaReportUtentePersonalizzato` (storico pagamenti di un singolo
utente) e `calcolaStatisticheGenerali` (aggregato Crypto + PayPal). Nessuno dei due è collegato a un
comando: sono codice non raggiungibile dall'interfaccia.

## Voci correlate
- [[Comandi admin]]
- [[Pagamento]]
- [[Prelievo]]
- [[Bilanciamento degli account Stripe]]
