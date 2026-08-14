---
tipo: entita
titolo: Referral agent
alias: [referral_agent, ReferralAgent, codice invito]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-14
stato: stabile
---

# Referral agent

Un **codice invito Discord** con l'indicazione di chi l'ha creato. È l'anello che collega un
[[Utente]] a chi lo ha portato, e quindi la base delle commissioni. Tabella `referral_utenti`.

Nonostante il nome, **non** rappresenta un agente: l'agente è un'entità diversa ([[Agente]]). Qui
finisce **ogni** invito della guild, creato da chiunque.

## Come si popola

Automaticamente, dal `InviteListener` ([[Onboarding e disclaimer]]):

- **all'avvio del bot** (`onReady`) tutti gli inviti esistenti della guild vengono sincronizzati;
- **alla creazione** di un nuovo invito (`onGuildInviteCreate`) la riga viene aggiunta o aggiornata.

La sincronizzazione aggiorna solo `nomeAgente` sulle righe già presenti: gli altri campi restano
quelli del primo inserimento.

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `codiceReferral` | `codice_referral` | il codice dell'invito, es. `3WHCEvZT`. `UNIQUE` |
| `idDiscordAgente` | `id_discord_agente` | Discord ID di chi ha creato l'invito. **Non univoco**: un utente può generare più inviti — nei dati reali fino a 22 |
| `nomeAgente` | `nome_agente` | username di chi l'ha creato |
| `tipo` | `tipo` | `ENUM('UTENTE','ADMIN')`: chi ha generato il codice |
| `utilizzi` | `utilizzi` | utilizzi **già attribuiti** a un utente: è la baseline dell'attribuzione |
| `dataCreazione`, `dataUpdate` | idem | audit |
| `utentiReferiti` | (relazione) | gli [[Utente|utenti]] entrati con quel codice |

> [!warning] Eliminate da `V15` il 2026-08-14
> **`commissione_percentuale`** valeva `0.00` su tutte e 157 le righe: la percentuale applicata la
> legge `CommissioneService` da [[Agente]], mai da qui. Era il residuo del modello in cui codice
> invito e agente erano la stessa cosa.
>
> **`limite_utilizzi`** era valorizzata su 1 riga su 157; la query `findReferralAlLimite()` e il
> metodo `isAttivo()` che la usavano non avevano chiamanti — e `isAttivo()`, verificando solo il
> limite, restituiva sempre `true`.
>
> **`data_attivazione`** coincideva con la data di creazione.
>
> **`descrizione_referral`** è diventata `tipo`: era un `TEXT` con due soli valori.
>
> Con esse è stato ridotto `ReferralAgentService`, da 153 righe a 58: creazione, aggiornamento e
> associazione utente-referral erano **tutti metodi senza chiamanti**, superati da `AgentiService`
> e `CommissioneService` quando gli agenti hanno preso tabella propria. La classe iniettava anche
> **due volte lo stesso repository** con nomi diversi, uno per lo strato vivo e uno per quello
> morto.

## La colonna `utilizzi` (dalla migration V3)

Non è il contatore di Discord, è **l'ultimo valore attribuito**. La differenza fra i due è ciò che
identifica l'invito usato da un nuovo membro ([[Sistema referral e commissioni]]):

- viene incrementata di **uno** a ogni attribuzione riuscita;
- **non** viene toccata quando un'attribuzione fallisce — così la differenza resta recuperabile;
- viene allineata al valore reale all'avvio del bot, ma **solo** se non ci sono
  [[Referral pendente|pendenti]];
- una riga creata *ex novo* nasce già allineata al contatore reale, per non generare differenze
  fittizie.

## La percentuale non sta qui

Questa tabella dice **chi ha portato chi**, non quanto gli spetta. La percentuale è su
`referral_agenti.commissione_percentuale` ([[Agente]]), e il collegamento è:

```
utenti.referral_id → referral_utenti.id_discord_agente → referral_agenti.discord_id → percentuale
```

Chi crea un invito diventa quindi remunerato **solo se** risulta anche fra gli agenti. Fino a `V15`
esisteva una `commissione_percentuale` anche qui, sempre a `0.00`: il residuo del modello in cui le
due cose erano una sola. Vedi [[Sistema referral e commissioni]].

## Un utente, molti codici

Lo stesso Discord ID compare su più righe, una per invito creato — nei dati reali fino a 22 per la
stessa persona. Fra questi, `referral_agenti.codici_ref_validi` sceglie quali danno diritto a
commissione: se è vuoto valgono tutti.

## Voci correlate
- [[Agente]]
- [[Sistema referral e commissioni]]
- [[Onboarding e disclaimer]]
