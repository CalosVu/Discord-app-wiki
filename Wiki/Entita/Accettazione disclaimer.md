---
tipo: entita
titolo: Accettazione disclaimer
alias: [disclaimer_accept, DisclaimerAccept]
tag: [dominio/utenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Accettazione disclaimer

Registra chi ha accettato le regole del server reagendo con ✅ al messaggio del disclaimer. Tabella
`utenti_disclaimer`, entità `DisclaimerAccept`.

## Struttura

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | `UNIQUE`; usato come FK da `sys_log_server` |
| `accettato` | `accettato` | booleano, aggiornato in entrambe le direzioni |
| `dataUltimaReazione` | `data_ultima_reazione` | riscritta a ogni cambio: dice quando ha accettato o revocato |

## Il gate di tutto il resto

L'accettazione è la **precondizione** di ogni operazione che riguardi denaro o informazioni. Il
metodo `discordService.hasAcceptedDisclaimer(discordId)` viene invocato all'ingresso di:

- `!Donazione` e la scelta del canale di pagamento;
- `!verifica-transazione` e l'apertura della modale;
- la generazione dei link Stripe;
- l'effettiva verifica di una transazione crypto;
- il pulsante *Bacheca* (`!Bacheca`, che esiste **solo** come pulsante — vedi [[Comandi utente]]).

Chi non ha accettato riceve un embed che lo rimanda al canale `#disclaimer`. Il comando `!Comandi`
e `!Stato-disclaimer` restano invece sempre disponibili.

## Reazione rimossa = accettazione revocata

Se l'utente **toglie** la reazione ✅, `onMessageReactionRemove` porta `accettato` a `false`: da quel
momento tutti i flussi sopra tornano bloccati. La riga non viene cancellata, e l'[[Utente]] già
censito resta con il suo abbonamento e i suoi ruoli — **il degrado non è automatico**.

## Legame con l'utente

L'accettazione **collega** il proprio record all'[[Utente]] tramite `users.disclaimer_id`. L'utente a
quel punto esiste già, perché viene censito all'ingresso nel server
([[Onboarding e disclaimer]]); se per qualche motivo mancasse — per esempio un membro entrato prima
dell'introduzione del censimento all'ingresso — viene creato in quel momento come rete di sicurezza.

> [!warning] Storia / claim superate
> Fino al 2026-07-26 era **l'accettazione stessa a creare** la riga in `utenti`: senza reazione ✅
> l'utente non esisteva per l'applicazione. **Ora la creazione avviene all'ingresso** e qui resta solo
> il collegamento e l'abilitazione.

## Voci correlate
- [[Utente]]
- [[Onboarding e disclaimer]]
- [[Bot Discord]]
