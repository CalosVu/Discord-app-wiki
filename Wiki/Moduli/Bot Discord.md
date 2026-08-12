---
tipo: modulo
titolo: Bot Discord
alias: [JDA, DiscordBot, listener]
tag: [dominio/bot]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Bot Discord

Il bot JDA 5.5.1 è il canale principale di interazione: tutti i comandi funzionali arrivano in
**messaggio privato**, non nei canali della guild.

## Due istanze JDA

Attenzione: nel sistema esistono **due costruzioni di JDA distinte**.

| Dove | Cosa fa | Intent |
|---|---|---|
| `DiscordConfig` (`@Configuration`) | crea il **bean** `JDA` iniettato nei servizi (`DiscordService`) | `GUILD_MEMBERS`, `GUILD_MESSAGES`, `DIRECT_MESSAGES` |
| `DiscordBot` (`@PostConstruct`) | crea l'istanza che **registra i listener** e pinna il disclaimer | `GUILD_MEMBERS`, `GUILD_PRESENCES`, `MESSAGE_CONTENT`, `GUILD_MESSAGES`, `GUILD_MESSAGE_REACTIONS`, `GUILD_INVITES` |

Sono due connessioni al gateway con lo stesso token. Chi tocca gli intent deve sapere che la
configurazione **rilevante per i listener** è quella in `DiscordBot`: aggiungerli in `DiscordConfig`
non ha effetto sugli eventi ricevuti.

## I cinque listener

| Listener | Eventi | Ruolo |
|---|---|---|
| `InviteListener` | `onReady`, `onGuildInviteCreate`, `onGuildMemberJoin` | tracciamento inviti → [[Sistema referral e commissioni]] |
| `DisclaimerListener` | `onGuildMemberJoin`, reazione aggiunta/rimossa | ruolo GUEST, censimento utente → [[Onboarding e disclaimer]] |
| `MessageReceivedListener` | `onMessageReceived` | routing dei comandi testuali in DM |
| `OnButtonInteractionListener` | `onButtonInteraction`, `onModalInteraction` | pulsanti e modali dei pagamenti |
| `MenuSelectionListener` | `onStringSelectInteraction`, `onModalInteraction` | menu a tendina admin, agenti, masterclass |

Due listener implementano `onModalInteraction`: ciascuno gestisce i propri `modalId` e ignora gli
altri.

## Il disclaimer pinnato

All'avvio, `pinDisclaimerIfMissing` legge gli ultimi 100 messaggi del canale disclaimer e confronta
il testo con quello nel codice (`Constants.txtDisclaimer`), spezzato in blocchi da **1.725
caratteri** (limite dei messaggi Discord). Se coincide non fa nulla; altrimenti cancella i vecchi
messaggi del bot, reinvia le parti e le **pinna in ordine inverso**, così l'ordine di lettura
risulta corretto.

Serve che il bot abbia i permessi `MESSAGE_MANAGE` e `MESSAGE_HISTORY` sul canale: altrimenti logga
un errore e rinuncia.

## Il testo del disclaimer è nel codice

`Constants.txtDisclaimer` contiene l'intero regolamento (comportamento, contenuti, pubblicità,
sicurezza file, informazioni finanziarie, moderazione, rischi, cause di espulsione). Modificarlo
richiede **un deploy**: non è configurabile a runtime.

## Convenzione dei comandi

Tutti i comandi iniziano con `!`, il confronto è **case-insensitive** (`equalsIgnoreCase`), e la
condizione `!event.isFromGuild()` limita l'ascolto ai messaggi privati. Non sono usate le slash
command di Discord.

## Voci correlate
- [[Comandi utente]]
- [[Comandi admin]]
- [[Onboarding e disclaimer]]
- [[Ruoli Discord]]
