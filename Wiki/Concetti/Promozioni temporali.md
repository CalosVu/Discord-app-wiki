---
tipo: concetto
titolo: Promozioni temporali
alias: [promo, PROMO, promozione]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Promozioni temporali

Un'offerta a tempo che **sovrascrive prezzo e durata** dell'[[Abbonamento Supporter Member]] per
gli utenti non pionieri. Vive come riga `PROMO` del [[Catalogo servizi]].

Esempio dai dati iniziali: 130 € / 149 USD per **4 mesi** (invece di 160 €), valida dal 31/03/2026
al 15/08/2026.

## Le quattro condizioni di applicabilità

`getPromoAttiva(utente)` ritorna una promo solo se **tutte** sono vere:

1. l'utente **non** è pioniere ([[Membri pionieri]]);
2. la promo ha `numeroMesi` valorizzato;
3. se l'utente sta **rinnovando** (`numeroRinnovi > 0`), la promo deve avere `rinnovo = true`;
4. se la promo ha un `referral`, l'utente deve essere entrato **con quello stesso** referral
   ([[Referral agent]]).

La query di partenza filtra già su `nome_servizio = 'PROMO'`, `attivo = true` e `adesso` compreso
fra `data_inizio` e `data_fine`.

## Precedenza fra più promo

Se più promo risultano valide contemporaneamente, vince quella **specifica per referral** sulla
generica:

```java
.min(Comparator.comparingInt(p -> p.getReferral() == null ? 1 : 0))
```

Fra due promo generiche o due promo con lo stesso referral, la scelta è **non deterministica**
(dipende dall'ordine restituito dal database). Conviene evitare sovrapposizioni.

## Effetto sul flusso di pagamento

| Canale | Effetto |
|---|---|
| **Stripe** | il campo "numero mesi" della modale **non viene mostrato**: mesi e prezzo totale arrivano dalla promo. Se la modale è già aperta, il valore inserito viene comunque ignorato |
| **Crypto** | il prezzo totale viene **diviso** per il numero di mesi, perché la verifica on-chain moltiplica poi per i mesi; `nMesi` viene forzato al valore della promo |

Gli embed mostrano un blocco «🔥 PROMO IN CORSO!» con data di fine e mesi coperti.

## Duplicazione da conoscere

Il metodo `getPromoAttiva` è **replicato identico in tre classi**: `CommandBot`,
`OnButtonInteractionListener` e `CryptoPaymentService`. Una modifica alla logica va riportata in
tutti e tre i punti, altrimenti i canali divergono.

## Disattivazione automatica

Il [[Batch verifica abbonamenti]], a ogni esecuzione, cerca le promo con `data_fine` passata e le
porta ad `attivo = false`. La promo scade quindi da sola, ma solo dopo il primo giro del batch
successivo alla scadenza.

## Voci correlate
- [[Catalogo servizi]]
- [[Membri pionieri]]
- [[Abbonamento Supporter Member]]
