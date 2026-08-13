---
tipo: entita
titolo: Referral agent
alias: [referral_agent, ReferralAgent, codice invito]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
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

La sincronizzazione aggiorna solo `nomeAgente` e `limiteUtilizzi` sulle righe già presenti: gli
altri campi restano quelli del primo inserimento.

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `codiceReferral` | `codice_referral` | il codice dell'invito, es. `3WHCEvZT`. `UNIQUE` |
| `idDiscordAgente` | `id_discord_agente` | Discord ID di chi ha creato l'invito |
| `nomeAgente` | `nome_agente` | username di chi l'ha creato |
| `commissionePercentuale` | `commissione_percentuale` | ⚠️ **sempre 0.00**: non è questa la percentuale usata |
| `descrizioneReferral` | `descrizione_referral` | testo libero (`"Utente"`, `"Admin"`) |
| `limiteUtilizzi` | `limite_utilizzi` | copiato da `maxUses` dell'invito Discord, se > 0 |
| `utilizzi` | `utilizzi` | utilizzi **già attribuiti** a un utente: è la baseline dell'attribuzione |
| `utentiReferiti` | (relazione) | gli [[Utente|utenti]] entrati con quel codice |

## La colonna `utilizzi` (dalla migration V3)

Non è il contatore di Discord, è **l'ultimo valore attribuito**. La differenza fra i due è ciò che
identifica l'invito usato da un nuovo membro ([[Sistema referral e commissioni]]):

- viene incrementata di **uno** a ogni attribuzione riuscita;
- **non** viene toccata quando un'attribuzione fallisce — così la differenza resta recuperabile;
- viene allineata al valore reale all'avvio del bot, ma **solo** se non ci sono
  [[Referral pendente|pendenti]];
- una riga creata *ex novo* nasce già allineata al contatore reale, per non generare differenze
  fittizie.

## ⚠️ La percentuale qui non conta

`referral_agent.commissione_percentuale` esiste ed è sempre `0.00`. La percentuale che il sistema
applica davvero sta su **`agenti.commissione_percentuale`** ([[Agente]]). Il collegamento è:

```
Utente.referral → referral_agent.id_discord_agente → agenti.discord_id → percentuale
```

Chi ha creato l'invito diventa quindi remunerato **solo se** risulta anche nella tabella `referral_agenti`.
Vedi [[Sistema referral e commissioni]].

## Un agente, molti codici

Lo stesso Discord ID può comparire su più righe (più inviti creati). Il campo
`agenti.codici_ref_validi`, se valorizzato, restringe la commissione ai soli codici elencati.

## Voci correlate
- [[Agente]]
- [[Sistema referral e commissioni]]
- [[Onboarding e disclaimer]]
