---
tipo: concetto
titolo: Sistema referral e commissioni
alias: [referral, commissioni agenti]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Sistema referral e commissioni

Il meccanismo che riconosce a un [[Agente]] una percentuale sui pagamenti degli utenti che ha
portato sul server.

## La catena completa

```
invito Discord creato
   → InviteListener lo salva in referral_agent          [[Referral agent]]
utente entra usando quell'invito
   → DisclaimerListener lo censisce in users             [[Utente]]
   → InviteListener confronta i contatori degli inviti con referral_agent.utilizzi
        ├─ un solo invito incrementato → scrive users.referral_id e consuma un utilizzo
        └─ esito non univoco → riga in referral_pendenti [[Referral pendente]]
                               e contatori LASCIATI FERMI
utente paga
   → CommissioneService cerca agenti.discord_id = referral.id_discord_agente
   → se lo trova (e il codice è ammesso) crea commissioni_pagamento   [[Commissione pagamento]]
```

Il punto chiave: **creare inviti non basta**. La commissione matura solo se il creatore dell'invito
è anche censito nella tabella `referral_agenti`, e la percentuale usata è quella di `referral_agenti`, non quella
(sempre 0) di `referral_utenti`.

## Come si individua l'invito usato

**Discord non dice quale invito ha usato un nuovo membro.** Verificato nel jar di JDA 5.5.1: nessun
campo o metodo su `Member`, niente sull'evento di ingresso, e gli audit log **non registrano affatto i
join** (esistono `INVITE_CREATE/DELETE/UPDATE`, non `MEMBER_JOIN`). La colonna «Invitato da» che si
vede nel client Discord è un dato interno non esposto all'API.

L'unico metodo possibile è la **differenza dei contatori**: si confronta il numero di utilizzi di
ciascun invito letto dalla guild con l'ultimo valore **già attribuito**, conservato in
`referral_agent.utilizzi` ([[Referral agent]]).

```
delta(invito) = utilizzi reali su Discord − utilizzi già attribuiti
un solo invito con delta > 0  →  è quello usato
```

## La regola che rende recuperabili i fallimenti

**I contatori si incrementano solo quando un'attribuzione va a buon fine.** Se il confronto non dà
esito univoco, la baseline resta ferma e la differenza rimane visibile a un tentativo successivo —
anche giorni dopo, anche dopo un riavvio, perché è su database.

Conseguenze pratiche:

- **retry automatici** a 2, 5 e 15 secondi assorbono il ritardo con cui Discord propaga il contatore
  (la causa più comune di fallimento);
- l'utente non attribuito finisce in [[Referral pendente]] e resta recuperabile;
- finché esistono pendenti, l'allineamento della baseline all'avvio del bot **viene saltato**.

## Il recupero manuale

Il comando `!SyncReferral` ([[Comandi admin]]) mostra gli utenti in attesa e, su conferma, tenta
l'attribuzione. Attribuisce **solo** nel caso non ambiguo — un solo invito con delta e differenza
sufficiente a coprire tutti gli utenti in attesa — e negli altri casi riporta il dettaglio senza
indovinare, perché un'attribuzione sbagliata produrrebbe commissioni sbagliate.

## Limiti residui

- Se **due utenti entrano nello stesso istante** con inviti diversi, l'attribuzione è indecidibile:
  restano entrambi in attesa come `AMBIGUO`.
- Un utente entrato con un **invito poi revocato** non è più confrontabile: l'invito non compare fra
  quelli attivi della guild.

## Storia / claim superate

> [!warning] Sostituito da una modifica al codice
> Fino al 2026-07-26 i contatori vivevano **in memoria** (`ConcurrentHashMap`) e venivano riallineati
> **anche quando l'attribuzione falliva**: la differenza veniva bruciata e il dato perso per sempre.
> Il referral era scritto solo all'accettazione del disclaimer, quindi un riavvio nel frattempo lo
> perdeva comunque. Il comando *Fix Referral* prometteva il recupero ma **non poteva funzionare**:
> selezionava gli utenti marcati `UNKNOWN`/`ERROR` e li passava a un metodo che rifiutava proprio quei
> valori (vedi [[2026-07-25 Referral non attribuito e Fix Referral inefficace]]).

## Il calcolo

La commissione **non è salvata**: si ricalcola a ogni report come
`payment.importo × percentuale_applicata / 100`. Vedi [[Commissione pagamento]] per le implicazioni.

I report sono separati per canale: Stripe in **EUR**, crypto in **USD**. Non esiste conversione né
totale unico.

## Voci correlate
- [[Agente]]
- [[Referral agent]]
- [[Comandi agenti]]
- [[Onboarding e disclaimer]]
