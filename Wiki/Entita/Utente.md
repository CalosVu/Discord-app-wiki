---
tipo: entita
titolo: Utente
alias: [User, users, membro]
tag: [dominio/utenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Utente

L'utente Discord censito nel sistema: è l'entità attorno a cui ruotano abbonamento, ruoli, referral
e pagamenti. Tabella `users`, entità `discord.access.app.entity.User`.

## Quando nasce

L'utente viene creato **all'ingresso nel server** (`DisclaimerListener.onGuildMemberJoin`), non
all'accettazione del disclaimer. Alla creazione:

- `abilitato = false`, `numeroRinnovi = 0`, `membroPioniere = false`;
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
> reazione ✅ non esisteva alcuna riga in `users`, e chi non accettava mai non esisteva per
> l'applicazione. Il referral dedotto all'ingresso viveva in memoria in attesa di quel momento, e un
> riavvio nel frattempo lo perdeva. **Ora vale il censimento all'ingresso.**

## Campi e loro significato

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | chiave naturale, `UNIQUE`; usata come FK da mezzo schema |
| `username` | `username` | nome Discord al momento del censimento; non viene risincronizzato |
| `dataPrimaIscrizione` | `data_prima_iscrizione` | valorizzata al **primo** pagamento Supporter Member. Discrimina nuovo iscritto vs rinnovo ([[Blocco dei pagamenti]]) |
| `dataScadenzaIscrizione` | `data_scadenza_iscrizione` | scadenza dell'abbonamento; `null` dopo il degrado |
| `dataUltimaDonazione` | `data_ultima_donazione` | aggiornata da **entrambi** i tipi di pagamento |
| `numeroRinnovi` | `n_rinnovi` | incrementato a ogni pagamento Supporter Member (anche il primo) |
| `abilitato` | `abilitato` | messo a `true` al primo Supporter Member; **non** viene rimesso a `false` dal degrado |
| `membroPioniere` | `membro_pioniere` | prezzo agevolato; azzerato dal degrado ([[Membri pionieri]]) |
| `disclaimerAccept` | `disclaimer_id` | 1-a-1 con [[Accettazione disclaimer]] |
| `ultimoPagamento` | `payment_id` | 1-a-1 con l'ultimo [[Pagamento]] Supporter Member |
| `referral` | `referral_id` | il [[Referral agent]] con cui è entrato: base delle commissioni |
| `pianoApplicato` | `piano_applicato_id` | riga del [[Catalogo servizi]] che determina prezzo e durata |
| `dataCreazioneAccount` | `data_creazione_account` | `@CreationTimestamp` |

## Ciclo di vita dell'abbonamento

1. **Censimento** all'accettazione del disclaimer, ruolo `GUEST`.
2. **Primo pagamento** → scadenza = ora + `durataGiorniAbbonamento × mesi`, `dataPrimaIscrizione`
   valorizzata, ruolo `SUPPORTER_MEMBER` ([[Abbonamento Supporter Member]]).
3. **Rinnovo anticipato** (scadenza futura) → i giorni si **sommano** a quelli residui.
4. **Rinnovo dopo la scadenza** → la scadenza riparte da adesso.
5. **Degrado**, N giorni dopo la scadenza → ruolo `GUEST`, `membroPioniere = false`, piano riportato
   a BASIC, `dataScadenzaIscrizione = null` ([[Batch verifica abbonamenti]]).

## Trappole note

- Un utente **senza `pianoApplicato`** non può pagare: sia il flusso crypto sia quello Stripe
  falliscono con «non ha un piano associato». Capita ai record creati prima dell'introduzione del
  campo.
- Il degrado **non** tocca `abilitato` né `numeroRinnovi`: `abilitato` resta `true` per sempre e non
  va usato come indicatore di abbonamento attivo. L'indicatore corretto è
  `dataScadenzaIscrizione >= adesso` (è quello che usa [[Integrazione VuTracker]]).
- Se l'utente **non è censito** e prova a pagare, il codice solleva `RuntimeException("Utente non
  censito!")`: succede a chi paga senza aver accettato il disclaimer da una sessione precedente.

## Voci correlate
- [[Abbonamento Supporter Member]]
- [[Ruoli Discord]]
- [[Utente lifetime]]
- [[Onboarding e disclaimer]]
