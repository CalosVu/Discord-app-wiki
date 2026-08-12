---
tipo: concetto
titolo: Sostegno libero
alias: [donazione libera, GOLD_SUPPORTER_MEMBER, offerta libera]
tag: [dominio/abbonamenti]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Sostegno libero

La donazione di importo libero: non dà accesso ai canali, dà un **badge di riconoscimento**
(`GOLD_SUPPORTER_MEMBER`). È l'alternativa "senza impegno" all'[[Abbonamento Supporter Member]].

## Cosa succede a chi dona

- viene creato un [[Pagamento]] con `transactionType = GOLD_SUPPORTER_MEMBER`;
- viene assegnato il ruolo `GOLD_SUPPORTER_MEMBER` ([[Ruoli Discord]]);
- viene aggiornata `dataUltimaDonazione` sull'[[Utente]];
- **non** vengono toccati scadenza, `numeroRinnovi` né `abilitato`.

I messaggi promettono il badge «per 30 giorni», ma **nulla lo rimuove**: il codice che avrebbe
tolto il ruolo dopo 30 giorni esiste ma è **commentato** dentro il
[[Batch verifica abbonamenti]], con la nota «Da sviluppare meglio». In pratica il badge è
permanente.

## I due canali

| Canale | Come funziona |
|---|---|
| **Stripe** | link di checkout con quantità modificabile: unità da **2,00 €** (`unitAmount = 200`), minimo 1. L'utente sceglie la quantità, non l'importo libero |
| **Crypto** | l'utente invia quanto vuole al wallet e verifica la transazione: l'importo atteso è `BigDecimal.ONE`, quindi passa qualunque trasferimento ≥ 1 unità |

Nel flusso Stripe è attivo anche `setAllowPromotionCodes(true)`: sui codici sconto è l'unico punto
del sistema in cui compaiono.

## Nessun controllo di importo

A differenza del Supporter Member — dove un pagamento inferiore all'atteso **blocca** l'assegnazione
e notifica gli admin — sul sostegno libero non c'è verifica: è per definizione a importo libero.

## Il fix della notifica admin

Fino al branch `feature/doppioStripe` gli admin **non venivano avvisati** delle donazioni libere: il
ramo `else` di `aggiornaAbbonamentoUtente` assegnava il ruolo ma non chiamava `notificaAdmin`. Oggi
la notifica c'è, con utente, importo e metodo (fonte: [[Piano sviluppo doppio Stripe]] Fase 2).

Le donazioni **erano comunque già conteggiate** nei saldi: le query filtrano per metodo e stato, non
per `transaction_type`.

## Voci correlate
- [[Abbonamento Supporter Member]]
- [[Pagamenti Stripe]]
- [[Blocco dei pagamenti]]
