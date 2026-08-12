---
tipo: entita
titolo: Tentativo di verifica transazione
alias: [user_verify_transaction, UserVerifyTransaction]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Integrazione sistema pagamenti]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Tentativo di verifica transazione

Il registro di **ogni** tentativo di verifica di una transazione crypto, riuscito o fallito.
Tabella `user_verify_transaction`, entità `UserVerifyTransaction`.

## A cosa serve

A due cose insieme:

1. **rate limiting** — impedire che un utente bombardi il sistema con hash a caso;
2. **audit** — capire a posteriori perché una verifica non è andata a buon fine, visto che il
   messaggio di errore viene salvato per intero.

## Struttura

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | FK verso `users.discord_id` |
| `transactionHash` | `transaction_hash` | l'hash tentato (anche se inesistente) |
| `dataVerifica` | `data_verifica` | ora italiana del tentativo |
| `esito` | `esito` | booleano |
| `messaggio` | `messaggio` | `"Successo"` oppure il messaggio d'errore completo |

## Il rate limiting

Prima di ogni verifica il sistema conta i tentativi dell'utente nella finestra recente:

```
tentativi negli ultimi TEMPO_LIMITE_VERIFICA ore  >=  N_TENTATIVI_VERIFICA   →   rifiuto
```

Entrambi i parametri vengono da [[Tabella server_config]] (oggi: 3 tentativi in 2 ore, default nel
codice 3 e 2). Al superamento l'utente riceve: «Raggiunto limite massimo di 3 tentativi errati nelle
ultime 2h».

## ⚠️ Contano anche i tentativi riusciti

Il conteggio non filtra su `esito`: **ogni** riga nella finestra contribuisce al limite, comprese le
verifiche andate a buon fine. Un utente che completa tre pagamenti crypto legittimi in due ore si
trova bloccato al quarto. Il messaggio parla di «tentativi errati», ma il comportamento è diverso.

Nota anche che il testo del messaggio cita valori **fissi** (3 tentativi, 2 ore) mentre i valori
reali sono configurabili: se si cambia la configurazione, il messaggio non segue.

## Voci correlate
- [[Pagamenti crypto Arbitrum]]
- [[Tabella server_config]]
- [[Configurazione di server]]
