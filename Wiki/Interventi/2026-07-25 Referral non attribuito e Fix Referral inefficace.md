---
tipo: intervento
titolo: 2026-07-25 Referral non attribuito e Fix Referral inefficace
alias: [fix referral, attribuzione invito]
tag: [dominio/referral, intervento/analisi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: bozza
difetto: attribuzione del referral mancante su parte degli utenti; comando "Fix Referral" incapace di recuperare
task: persistere il tracciamento inviti su DB, censire l'utente all'ingresso, valutare il riallineamento in background
release_target: branch feature/versioneProdotto
componenti: [InviteListener, DisclaimerListener, InviteUsageService, CommandBot, ReferralAgentService]
file_toccati: [InviteUsageService.java, InviteListener.java, DisclaimerListener.java, CommandBot.java]
utility_usate: [LoadConfigurationService, DateValidator]
deploy_ambiente: produzione
deploy_macchina: Hetzner (server dell'app)
deploy_ruolo: applicativo Spring Boot + MySQL
deploy_percorso: /home/deploy/discord-bot/deployment
log_percorso: /opt/discord-bot/logs
---

# 2026-07-25 Referral non attribuito e Fix Referral inefficace

## In sintesi

Una parte degli utenti risulta **senza referral** in `users.referral_id`, quindi non genera
[[Commissione pagamento|commissioni]] per l'[[Agente]] che li ha portati. La voce di menu
**Fix Referral** ([[Comandi admin]]) esiste per recuperarli, ma **non può funzionare**: per
costruzione non aggiorna mai nessun utente.

Tre difetti distinti, che si sommano.

## Difetto 1 — Fix Referral è logicamente inefficace

`CommandBot.handleFixReferrals` invoca `InviteUsageService.updateUsersWithoutValidReferral()`.

| Passo | Codice | Effetto |
|---|---|---|
| 1 | `getUsersWithoutValidInvite()` (`InviteUsageService.java:109-114`) | seleziona **solo** gli utenti il cui codice in mappa è `"UNKNOWN"` o `"ERROR"` |
| 2 | `updateUsersWithoutValidReferral()` (`InviteUsageService.java:178`) | per ognuno chiama `getReferralForUser(userId)` |
| 3 | `getReferralForUser()` (`InviteUsageService.java:138-140`) | rilegge il codice **dalla stessa mappa** e lo accetta **solo se NON è** `UNKNOWN` né `ERROR` |

La guardia al passo 3 è **sempre falsa** sugli elementi selezionati al passo 1: l'insieme di input e
l'insieme accettato dal risolutore sono disgiunti. Si finisce nell'`else` (riga 151) e si ritorna
`null` (riga 158), quindi `updated` resta a `0`.

L'unico ramo che potrebbe risolvere — «l'utente ha già un referral nel DB» (riga 133) — è escluso a
monte, perché il chiamante filtra `user.getReferral() == null` (riga 176).

**Conseguenza:** il comando restituisce sempre «Comando Eseguito! N utenti senza invito valido» senza
aver corretto nulla. Il conteggio è l'unico output reale.

## Difetto 2 — Il tracciamento vive solo in RAM

`userInviteUsage` e `guildInviteUsages` sono `ConcurrentHashMap` non persistiti
(`InviteUsageService.java:27-30`), popolati da `onReady` e dagli eventi di ingresso.

- Ad ogni **riavvio** (cioè ad ogni deploy, e il deploy è automatico su push) la memoria si azzera.
- Gli utenti entrati e non ancora attribuiti diventano **irrecuperabili**.
- `getUsersWithoutValidInvite()` su mappa vuota ritorna lista vuota: il comando risponde «0 utenti
  senza invito valido», che è indistinguibile da «tutto a posto» ma significa «non so nulla».

## Difetto 3 — Finestra fra ingresso e censimento

L'attribuzione viene **letta** all'ingresso (`InviteListener.onGuildMemberJoin`) ma **scritta** solo
all'accettazione del disclaimer (`DisclaimerListener.onMessageReactionAdd`), che crea la riga in
`users` ([[Onboarding e disclaimer]]).

Fra i due momenti possono passare minuti o giorni. Se nel frattempo l'app si riavvia, il referral è
perso anche quando era stato correttamente determinato.

## Ipotesi 4 — Race condition sul contatore degli inviti (da confermare)

Osservazione riportata dall'utente: «inizialmente gli utenti quando entrano non hanno un agente
assegnato, ma dopo Discord aggiorna quel valore e lo mostra».

Spiegazione più probabile: `trackUsedInvite` chiama `guild.retrieveInvites()` **dentro** il
gestore di `onGuildMemberJoin`. Discord può consegnare l'evento `GUILD_MEMBER_ADD` **prima** di aver
propagato l'incremento di `uses` sull'invito. In quel caso nessun invito risulta incrementato,
`usedInviteCode` resta `null` e l'utente viene marcato `UNKNOWN` — pur essendo entrato con un invito
perfettamente valido.

Il metodo per differenza di contatori è l'unico disponibile: **Discord non espone via API quale
invito ha usato un membro**. Da qui segue un vincolo che condiziona tutto il resto: se l'istante
dell'ingresso si perde, il dato **non è più ricostruibile a posteriori** da nessuna chiamata.

⚠️ Da chiarire prima di implementare: l'utente si riferisce al dato mostrato dal **client Discord**
(Server Settings → Members → «Invited by») oppure al valore nel database dell'app? Nel primo caso
Discord conosce il dato internamente ma non lo espone all'API, e la conclusione non cambia.

## Perché il comando così com'è non può essere "riparato"

Correggere la guardia del passo 3 non basterebbe: non esiste una fonte da cui rileggere l'invito di
un utente marcato `UNKNOWN`. Un fix retroattivo è **impossibile in linea di principio**; l'unico
intervento efficace è **non perdere il dato al momento dell'ingresso**.

Ne segue che un eventuale job in background può fare **riallineamento** (propagare su `users` le
attribuzioni già risolte e persistite), non **indovinare** attribuzioni perse.

## Piano d'azione proposto

1. **Flyway** come gestore delle migrazioni, con baseline sullo schema esistente → [[Schema del database]].
2. **Censimento dell'utente all'ingresso** nel server, non all'accettazione del disclaimer; il
   disclaimer resta il gate che **abilita** le azioni ([[Accettazione disclaimer]]).
3. **Tracciamento inviti persistito su DB** (contatori per-invito + attribuzione per-utente), con
   **retry a breve** sulla lettura dei contatori per assorbire la race.
4. **Riallineamento in background** delle attribuzioni risolte, e trasformazione di *Fix Referral* in
   trigger manuale + report diagnostico onesto.

## Regressioni potenziali da verificare

| Area | Rischio |
|---|---|
| `users` popolata all'ingresso | crescita della tabella con utenti mai iscritti; `abilitato=false` deve restare il discriminante |
| [[Batch verifica abbonamenti]] | itera su **tutti** gli utenti: i nuovi record senza `dataScadenzaIscrizione` devono essere saltati (oggi lo sono già) |
| [[Integrazione VuTracker]] | un utente ora esiste anche senza abbonamento: la risposta deve restare `supporterAttivo=false`, non cambiare forma |
| Ordine dei listener | `InviteListener` e `DisclaimerListener` gestiscono **entrambi** `onGuildMemberJoin`, e la risoluzione dell'invito è asincrona: il censimento non deve dipendere dal suo completamento |
| `ddl-auto` | in `prod` è `validate`: ogni nuova tabella deve esistere **prima** dell'avvio, quindi via migration ([[Deploy e CI-CD]]) |
| Doppio censimento | il salvataggio all'ingresso deve essere idempotente: `discord_id` è `UNIQUE` |
| Commissioni pregresse | riallineare un referral **non** crea retroattivamente le [[Commissione pagamento|commissioni]] sui pagamenti già avvenuti |

## Stato

**Implementato sul branch `feature/versioneProdotto`**, in attesa di verifica funzionale su Discord.
Build e test verdi per le fasi 1 e 2; fase 3 da compilare.

| Fase | Contenuto | Stato |
|---|---|---|
| 1 | **Flyway**: `V1` schema, `V2` dati, baseline a V2, `ddl-auto: validate` in tutti i profili, `sql/` eliminata | ✅ verificata in locale (2026-07-26) |
| 2 | **Censimento all'ingresso**: `CensimentoUtenteService`, `DisclaimerListener` riscritto | ✅ build e 5 test verdi |
| 3 | **Attribuzione persistita**: `V3` (colonna `utilizzi` + tabella `referral_pendenti`), `AttribuzioneReferralService`, retry 2/5/15s, comando `!SyncReferral` | ⏳ da compilare |

### Cosa è stato eliminato

- `InviteUsageService` (tracciamento in RAM e recupero inefficace) — sostituito da
  `AttribuzioneReferralService`;
- `CommandBot.handleFixReferrals` e la voce *Fix Referral* dal menu `!Admin`;
- i file `sql/create_table.sql` e `sql/insert.sql`, il cui contenuto è in `V1` e `V2`.

### Decisioni prese con l'utente

1. `create_table.sql` e `insert.sql` **eliminati**: le migration `V<n>` sono sempre visibili e ordinate.
2. Mount `./sql` rimosso dai docker-compose: il container crea il database vuoto, allo schema pensa Flyway.
3. Censimento **senza filtri**: chiunque entra viene salvato in `users`.
4. **Nessun job schedulato**: il recupero è manuale via `!SyncReferral`, con lista e conferma.
5. `!SyncReferral` **sostituisce** la voce *Fix Referral*.

### Il vincolo che ha guidato la soluzione

L'ipotesi iniziale — «Discord a un certo punto aggiorna il dato, basta rileggerlo» — è stata
**verificata e scartata**: l'API non espone l'invito usato da un membro (vedi
[[Sistema referral e commissioni]]). Il recupero non può quindi rileggere il dato, ma solo interpretare
la differenza dei contatori: da qui la scelta di **non riallinearli mai sui fallimenti**, che è
l'invariante su cui si regge tutto ed è coperta da test.

## Voci correlate
- [[Sistema referral e commissioni]]
- [[Onboarding e disclaimer]]
- [[Comandi admin]]
- [[Referral agent]]
