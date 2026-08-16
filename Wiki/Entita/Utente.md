---
tipo: entita
titolo: Utente
alias: [User, users, membro]
tag: [dominio/utenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Utente

L'utente Discord censito nel sistema: è l'entità attorno a cui ruotano abbonamento, ruoli, referral
e pagamenti. Tabella `utenti`, entità `discord.access.app.entity.User`.

## Quando nasce

L'utente viene creato **all'ingresso nel server** (`DisclaimerListener.onGuildMemberJoin`), non
all'accettazione del disclaimer. Alla creazione:

- `numeroRinnovi = 0`, `membroPioniere = false`;
- nessuna scadenza e nessuna data di prima iscrizione;
- `pianoApplicato` = il piano **BASIC** del [[Catalogo servizi]];
- `referral` = il [[Referral agent]] dell'invito usato, **se già risolto** — la risoluzione è
  asincrona, quindi spesso viene assegnato poco dopo ([[Onboarding e disclaimer]]).

La creazione passa da un unico punto, `CensimentoUtenteService.censisciSeAssente`, ed è
**idempotente**: invocata su un utente esistente lo restituisce invariato, senza sovrascrivere
abbonamento, piano o referral. Lo stesso metodo è richiamato anche all'accettazione del disclaimer,
come rete di sicurezza per chi era già membro del server prima di questo flusso.

> [!warning] Storia / claim superate
> Fino al 2026-07-26 l'utente veniva creato **solo** all'accettazione del disclaimer: fra ingresso e
> reazione ✅ non esisteva alcuna riga in `utenti`, e chi non accettava mai non esisteva per
> l'applicazione. Il referral dedotto all'ingresso viveva in memoria in attesa di quel momento, e un
> riavvio nel frattempo lo perdeva. **Ora vale il censimento all'ingresso.**

> [!warning] Eliminate il 2026-08-13: `abilitato` e `disclaimer_id`
> **`abilitato`** sembrava dire «utente attivo». In realtà nasceva `false` al censimento, passava a
> `true` al primo pagamento e **non tornava mai indietro** — il batch delle 22:00 non lo toccava.
> Significava quindi «ha pagato almeno una volta nella vita», ed è il motivo per cui i 50 utenti con
> `abilitato = 1` coincidevano esattamente con i 50 che avevano un `payment_id`.
>
> I suoi due lettori erano `UserService.isUserEnabled` (nessun chiamante) e
> `CustomUserDetailsService`, cioè il flusso JWT che non è attivo. Quel controllo ora usa
> **la scadenza dell'abbonamento più i lifetime** ([[Sicurezza e autenticazione]]), che il batch
> tiene sempre aggiornata.
>
> **`disclaimer_id`** era scritto da `DisclaimerListener` e **letto da nessuno**: la verifica passa
> da `DiscordService.hasAcceptedDisclaimer`, che interroga `utenti_disclaimer` per `discord_id`.
> Spiega anche un dato che sembrava incoerente — 21 utenti con `disclaimer_id` ma `abilitato = 0`
> sono semplicemente persone che hanno accettato senza mai pagare.
>
> Il legame con [[Accettazione disclaimer]] resta, logico, tramite `discord_id`.

## Campi e loro significato

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | chiave naturale, `UNIQUE`; usata come FK da mezzo schema |
| `username` | `username` | l'**account** Discord (`user.getName()`, es. `ciccio`); scritto al censimento e non risincronizzato |
| `nomeVisualizzato` | `nome_visualizzato` | il nome della **lista membri** (`member.getEffectiveName()`, es. `Spiderman`); si aggiorna da solo, vedi sotto |
| `dataPrimaIscrizione` | `data_prima_iscrizione` | valorizzata al **primo** pagamento Supporter Member. Discrimina nuovo iscritto vs rinnovo ([[Blocco dei pagamenti]]) |
| `dataScadenzaIscrizione` | `data_scadenza_iscrizione` | scadenza dell'abbonamento; `null` dopo il degrado |
| `dataUltimaDonazione` | `data_ultima_donazione` | aggiornata da **entrambi** i tipi di pagamento |
| `numeroRinnovi` | `n_rinnovi` | incrementato a ogni pagamento Supporter Member (anche il primo) |
| `membroPioniere` | `membro_pioniere` | gode del prezzo agevolato **adesso**; azzerato dal degrado ([[Membri pionieri]]) |
| `pioniereStorico` | `pioniere_storico` | ha consumato un posto pioniere, **per sempre**: non viene mai riazzerato |
| `dataIngressoServer` | `data_ingresso_server` | primo ingresso nel server; ex `data_creazione_account` |
| `dataUpdate` | `data_update` | ultima scrittura della riga |
| `ultimoPagamento` | `payment_id` | 1-a-1 con l'ultimo [[Pagamento]] Supporter Member |
| `referral` | `referral_id` | il [[Referral agent]] con cui è entrato: base delle commissioni |
| `pianoApplicato` | `piano_applicato_id` | riga del [[Catalogo servizi]] che determina prezzo e durata |

## I due nomi, e perché servono entrambi

Discord ne ha tre; a database ne teniamo due.

| | Cosa contiene | Esempio | Quando cambia |
|---|---|---|---|
| `username` | l'**account** | `ciccio` | di rado |
| `nome_visualizzato` | ciò che appare nella **lista membri** | `Spiderman` | quando vuole l'utente, o un admin |

`getEffectiveName()` restituisce il nickname impostato sul server se c'è, altrimenti il display name
globale, altrimenti l'username: è esattamente la stringa che si legge nella lista a destra.

Il terzo — il display name globale da solo — non viene salvato: non serviva.

### Come resta aggiornato

Due meccanismi, perché nessuno dei due basta:

1. **`NomeMembroListener`** intercetta `GuildMemberUpdateNicknameEvent` e riscrive la riga
   nell'istante del cambio. Funziona grazie all'intent `GUILD_MEMBERS`, già attivo per l'ingresso
   dei nuovi membri;
2. **il [[Batch verifica abbonamenti]]** ricarica l'intera lista membri e riallinea tutto.

Il secondo non è ridondante: gli eventi emessi mentre il bot è spento — un deploy, un riavvio —
**Discord non li ripropone** alla riaccensione, e senza il giro notturno resterebbero persi per
sempre. È anche ciò che popola le righe esistenti alla prima esecuzione, senza `UPDATE` manuali.

Il riallineamento scrive **solo le righe cambiate**, e se Discord non risponde non tocca nulla:
azzerare i nomi per una chiamata fallita sarebbe peggio del disallineamento.

Chi ha lasciato il server **conserva l'ultimo nome noto**: non compare più fra i membri, quindi
nessuno lo sovrascrive.

## Ciclo di vita dell'abbonamento

1. **Censimento** all'ingresso nel server, ruolo di new entry.
2. **Primo pagamento** → scadenza = ora + `durataGiorniAbbonamento × mesi`, `dataPrimaIscrizione`
   valorizzata, ruolo `SUPPORTER_MEMBER` ([[Abbonamento Supporter Member]]). Qui viene assegnato il
   posto pioniere, se ne restano ([[Membri pionieri]]).
3. **Rinnovo anticipato** (scadenza futura) → i giorni si **sommano** a quelli residui.
4. **Rinnovo dopo la scadenza** → la scadenza riparte da adesso.
5. **Degrado**, N giorni dopo la scadenza → ruolo `GUEST`, `membroPioniere = false`, piano riportato
   a BASIC, `dataScadenzaIscrizione = null` ([[Batch verifica abbonamenti]]). `pioniereStorico`
   resta a `true`: il posto non torna disponibile.

## Trappole note

- Un utente **senza `pianoApplicato`** non può pagare: sia il flusso crypto sia quello Stripe
  falliscono con «non ha un piano associato». Capita ai record creati prima dell'introduzione del
  campo.
- Il degrado **non** azzera `numeroRinnovi`: resta il totale storico dei rinnovi, non quelli
  dell'abbonamento in corso.
- L'unico indicatore attendibile di abbonamento attivo è **`dataScadenzaIscrizione >= adesso`**,
  più l'appartenenza a [[Utente lifetime]]. Esisteva un campo `abilitato` che sembrava dire questo
  ma significava altro: eliminato il 2026-08-13, vedi sopra.
- Se l'utente **non è censito** e prova a pagare, il codice solleva `RuntimeException("Utente non
  censito!")`: succede a chi paga senza aver accettato il disclaimer da una sessione precedente.

## Voci correlate
- [[Abbonamento Supporter Member]]
- [[Ruoli Discord]]
- [[Utente lifetime]]
- [[Onboarding e disclaimer]]
