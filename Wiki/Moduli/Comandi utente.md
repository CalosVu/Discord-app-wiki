---
tipo: modulo
titolo: Comandi utente
alias: [comandi bot, comandi DM]
tag: [dominio/bot, dominio/comandi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Comandi utente

Tutti i comandi disponibili a un utente normale. Si scrivono **in messaggio privato al bot**,
iniziano con `!` e il confronto è case-insensitive.

## Elenco completo

| Comando | Cosa fa | Richiede disclaimer |
|---|---|---|
| `!Comandi` | invia il messaggio di benvenuto con i 5 pulsanti | no |
| `!Stato-disclaimer` | mostra se il disclaimer risulta accettato | no |
| `!Donazione` | avvia il flusso di pagamento: scelta fra Crypto e Stripe | **sì** |
| `!verifica-transazione` | avvia la verifica di un pagamento crypto | **sì** |
| `!masterclass` | avvia l'acquisto di una masterclass | no |
| `!miemasterclass` | report vendite — solo se si è [[Relatore]] | no |
| `!mieiref` | report commissioni — solo se si è [[Agente]] | no |

Non esiste un comando "aiuto" oltre a `!Comandi`. Un comando sconosciuto viene **ignorato in
silenzio** (i pulsanti non riconosciuti rispondono invece «Comando non riconosciuto»).

## L'interruttore generale

`COMANDI_BOT_ABILITATI` a `false` spegne **tutto quanto in questa pagina**, e non solo: anche
bottoni, menu a tendina e finestre di inserimento, quindi non basta avere un vecchio embed in chat
per aggirarlo. A ogni tentativo il bot risponde con il testo `bot.disabilitato` e non fa altro.

Il controllo sta in cinque punti — `MessageReceivedListener`, i due gestori di
`OnButtonInteractionListener`, i due di `MenuSelectionListener` — perché quelle sono tutte e sole le
porte da cui entra un'interazione. Nessun comando lo verifica per conto proprio.

**Gli amministratori sono esenti** e continuano a operare normalmente ([[Comandi admin]]).
L'esenzione vale su tutte le superfici, non solo su `!Admin`: quel comando apre un pannello di
bottoni e menu, che altrimenti si aprirebbe muto.

Non tocca invece ciò che non è un comando: censimento all'ingresso, disclaimer, referral, batch delle
22:00, webhook di pagamento. Vedi [[Tabella cfg_server]], dove è spiegato anche perché per
riaccenderlo si passa dal database.

## I cinque pulsanti di `!Comandi`

*Stato Disclaimer* · *Info Donazione* · *Verifica Transazione* · *Bacheca* · *Verifica Scadenza*.

**Due di questi esistono solo come pulsante**, non come comando testuale — scriverli in chat non
produce nulla, perché `MessageReceivedListener` non li conosce:

| Pulsante | Id interno | Cosa mostra |
|---|---|---|
| *Bacheca* | `!Bacheca` | contatti, servizi attivi, canali utili, orari |
| *Verifica Scadenza* | `!Scadenza-abbonamento` | la data di scadenza dell'abbonamento |

Gli altri tre corrispondono ai comandi testuali della tabella sopra, e il pulsante fa esattamente
quello che farebbe il comando.

## Il flusso di donazione, passo per passo

```
!Donazione
  └─ (se nessun tipo di pagamento è abilitato → "pagamenti sospesi", fine)
  └─ 2 pulsanti: [Crypto] [Stripe]
       ├─ Crypto → 2 embed in DM: wallet, rete, importo, avvertenze
       │            poi l'utente paga e usa !verifica-transazione
       └─ Stripe → pulsanti [Supporter Member] [Sostegno Libero]   (solo quelli abilitati)
                    ├─ Supporter Member → modale "numero mesi" (saltata se c'è una promo)
                    │                      → link di checkout in DM, valido 5 ore
                    └─ Sostegno Libero  → link diretto, importo modificabile
```

Il flusso di verifica crypto è simmetrico:

```
!verifica-transazione
  └─ pulsante "Inserisci Dati Transazione"
       └─ pulsanti [Supporter Member] [Sostegno Libero]
            └─ modale: TX-hash (66 caratteri esatti) + numero mesi (1-24)
                 └─ verifica on-chain → esito in DM
```

I dettagli dei due canali sono in [[Pagamenti Stripe]] e [[Pagamenti crypto Arbitrum]].

## L'acquisto di una masterclass

`!masterclass` apre un menu a cascata: **relatore → masterclass → embed con prezzo → pulsante
Acquista**. Al click partono tre controlli (masterclass attiva, non già acquistata, file presente
su R2) e poi il link di checkout. Vedi [[Sistema masterclass]].

## Comportamenti da conoscere

- **I pulsanti non scadono.** I messaggi Discord restano cliccabili per sempre: per questo ogni
  handler ricontrolla i flag di [[Blocco dei pagamenti]] prima di agire.
- **I link Stripe scadono**: 5 ore per le donazioni (configurabile), 2 ore per le masterclass
  (fisso nel codice).
- Chi non ha accettato il disclaimer riceve un embed che rimanda al canale `#disclaimer`, non un
  errore generico.
- Chi non è censito in `utenti` provoca un `RuntimeException("Utente non censito!")`: succede a chi
  interagisce senza aver mai reagito al disclaimer.

## Voci correlate
- [[Bot Discord]]
- [[Comandi admin]]
- [[Abbonamento Supporter Member]]
- [[Sostegno libero]]
