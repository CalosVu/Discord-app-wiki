---
tipo: entita
titolo: Agente
alias: [agenti, Agente referral]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Agente

Un utente **remunerato** sui pagamenti di chi è entrato con i suoi inviti. Tabella `agenti`, entità
`Agente`.

## Come si diventa agente

**A mano, via SQL.** Non esiste nessun comando del bot per creare o modificare un agente: la riga va
inserita direttamente in `agenti` (stessa filosofia di [[Relatore]] e [[Utente lifetime]]).

Vincoli: `discord_id` è `UNIQUE` e ha una FK verso `users.discord_id`, quindi l'utente **deve già
essere censito** ([[Utente]]).

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | identifica l'agente; è la chiave di ricerca di tutti i comandi |
| `user` | `user_id` | riferimento all'[[Utente]] |
| `username` | `username` | mostrato nei report |
| `commissionePercentuale` | `commissione_percentuale` | **la** percentuale che conta (es. `10.00`) |
| `codiciRefValidi` | `codici_ref_validi` | opzionale: elenco di codici separati da virgola |
| `dataInserimento` | `data_inserimento` | `@CreationTimestamp` |

## Il filtro `codici_ref_validi`

Se **vuoto o nullo** → l'agente prende commissione su **tutti** gli utenti entrati con un qualunque
invito da lui creato.

Se **valorizzato** (es. `"3WHCEvZT,anJKHdkU"`) → la commissione matura **solo** se il codice con cui
l'utente è entrato compare nella lista. Serve a distinguere gli inviti "di lavoro" da quelli
personali. Lo stesso campo filtra anche l'elenco dei link mostrati dal comando `!mieiref`
([[Comandi agenti]]).

## Cosa può fare un agente

Un solo comando: `!mieiref`, che mostra i propri link referral attivi e i report commissioni per
mese corrente o precedente, separati per Stripe (EUR) e crypto (USD). Vedi [[Comandi agenti]].

Gli admin possono vedere **lo stesso identico report** dal menu `!Admin` → *Report Agente*: la
logica di costruzione degli embed è condivisa (`buildReportAgenteEmbeds`), così le due viste non
possono divergere.

## Voci correlate
- [[Referral agent]]
- [[Commissione pagamento]]
- [[Sistema referral e commissioni]]
- [[Comandi agenti]]
