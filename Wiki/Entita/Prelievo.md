---
tipo: entita
titolo: Prelievo
alias: [track_prelievi, TrackPrelievi, uscita]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Prelievo

Un'uscita di denaro registrata da un admin: serve a tenere il **saldo** allineato a quanto è
realmente rimasto sui conti. Tabella `pagamenti_prelievi`, entità `TrackPrelievi`.

## Chi lo registra e come

Solo un admin, dal menu `!Admin` → *Salva Prelievo*, che apre una modale con cinque campi: importo,
metodo, wallet destinatario, hash transazione, descrizione ([[Comandi admin]]).

Il campo **metodo** accetta tre valori testuali:

| Valore digitato | `metodo_pagamento` | `stripe_account` |
|---|---|---|
| `CRYPTO` | `CRYPTO` | `NULL` |
| `STRIPE_PRIMARIO` | `STRIPE` | `PRIMARIO` |
| `STRIPE_SECONDARIO` | `STRIPE` | `SECONDARIO` |

Qualsiasi altro valore viene rifiutato. La valuta viene dedotta: `USDT` per crypto, `EUR` per Stripe.

## Validazioni applicate

Prima del salvataggio, in ordine:

1. **autorizzazione**: `discordService.isAdmin(...)`, altrimenti `AutorizzazioneNegataException`;
2. **formato importo**: deve corrispondere a `10.00` o `10,00` (due decimali obbligatori), fra
   `0.01` e `1.000.000`;
3. **formato hash e wallet**: hash `0x` + 64 esadecimali, wallet `0x` + 40 esadecimali;
4. **verifica on-chain**: `verifyAdminArbitrumTransaction` decodifica l'input della transazione e
   controlla che il destinatario coincida con il wallet indicato;
5. **regole di business**: importo positivo, descrizione presente e di almeno 5 caratteri.

## ⚠️ La verifica on-chain vale anche per i prelievi Stripe

Il controllo al punto 4 è **incondizionato**: viene eseguito anche quando il metodo è
`STRIPE_PRIMARIO`/`STRIPE_SECONDARIO`. Per registrare un prelievo Stripe bisogna comunque fornire un hash e
un wallet formalmente validi e verificabili su Arbitrum. È un vincolo del flusso attuale, non una
scelta documentata altrove.

## Campi

`importoPrelievo`, `valuta`, `metodoPagamento`, `stripeAccount`, `transactionHash`,
`walletDestinatario`, `dataPrelievo`, `descrizionePrelievo`, `statoPrelievo`, `idDiscordAdmin`,
più i timestamp di creazione/aggiornamento.

`statoPrelievo` è sempre scritto come `COMPLETATO`: gli altri valori dell'enum
(`IN_ATTESA`, `IN_ELABORAZIONE`, `FALLITO`) non vengono mai prodotti dal codice. Tutte le query di
saldo filtrano proprio su `COMPLETATO`.

## Voci correlate
- [[Pagamento]]
- [[Reportistica]]
- [[Comandi admin]]
- [[Bilanciamento degli account Stripe]]
