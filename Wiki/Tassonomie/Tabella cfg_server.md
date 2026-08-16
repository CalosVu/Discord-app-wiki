---
tipo: tassonomia
titolo: Tabella cfg_server
alias: [cfg_server, server_config, configurazioni runtime, parametri]
tag: [dominio/configurazione]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Tabella cfg_server

L'elenco **completo** dei parametri di configurazione runtime: quelli modificabili dal database
senza deploy né riavvio. Per il funzionamento del meccanismo vedi [[Configurazione di server]].

## I parametri

| id | `nome_configurazione` | Valore iniziale | Default nel codice | Chi lo legge | Effetto |
|---|---|---|---|---|---|
| 1 | `N_TENTATIVI_VERIFICA` | `3` | `3` | `CryptoPaymentService` | numero massimo di tentativi di verifica crypto nella finestra |
| 2 | `TEMPO_LIMITE_VERIFICA` | `2` | `2` | `CryptoPaymentService` | ampiezza della finestra, in **ore** |
| — | `COMANDI_BOT_ABILITATI` | `true` | `true` | `ComandiBotService` | interruttore generale delle interazioni col bot |
| — | `LOG_CONSERVAZIONE_GIORNI` | `365` | `0` | `VerificaAbbonamentiBatch` | giorni di conservazione del [[Log operativo]]. `0` conserva tutto |
| — | `PIONIERI_ABILITATI` | `true` | `false` | `PianoUtenteService` | interruttore del meccanismo. A `false` tutti pagano `BASIC` |
| 3 | `PIONIERI` | `50` | `0` | `PianoUtenteService` | tetto dei posti pioniere. Default 0: se la chiave manca non nascono pionieri per sbaglio |
| — | `PIONIERI_ASSEGNATI` | quelli esistenti | `0` | `PianoUtenteService` | posti già consumati. **Non si decrementa mai** |
| 4 | `N_GIORNI_DOPO_SCADENZA` | `3` | `3` | `VerificaAbbonamentiBatch` | giorni di tolleranza dopo la scadenza prima del degrado |
| 5 | `N_ORE_DURATA_LINK_STRIPE` | `5` | `5` | `StripePaymentService` | validità del link di checkout per le donazioni, in ore |
| 6 | `MASTERCLASS_DURATA_LINK_ORE` | `3` | `3` | `MasterclassPaymentNotificationService` | validità del presigned URL R2 della masterclass, in ore |
| 7 | `PAGAMENTI_NUOVE_ISCRIZIONI_ABILITATE` | `true` | `true` | `PagamentiAbilitazioneService` | abilita il **primo** Supporter Member |
| 8 | `PAGAMENTI_RINNOVI_ABILITATI` | `true` | `true` | `PagamentiAbilitazioneService` | abilita i **rinnovi** Supporter Member |
| 9 | `DONAZIONI_LIBERE_ABILITATE` | `true` | `true` | `PagamentiAbilitazioneService` | abilita il [[Sostegno libero]] |
| — | `BATCH_VERIFICA_ABBONAMENTI` | `true` | `true` | `VerificaAbbonamentiBatch` | `false` = niente promemoria di rinnovo, scadenze, degradi di ruolo |
| — | `BACKUP_DB_ABILITATO` | `true` | `true` | `VerificaAbbonamentiBatch` | `false` = niente backup del database alle 22:00 |
| — | `RUOLO_ABBONATO` | `SUPPORTER_MEMBER` | `DISCORD_SUPPORTER_MEMBER_ROLE` | `RuoliDiscordService` | ruolo di chi ha un abbonamento attivo |
| — | `RUOLO_DONAZIONE` | `GOLD_SUPPORTER_MEMBER` | `DISCORD_GOLD_SUPPORTER_MEMBER_ROLE` | `RuoliDiscordService` | ruolo di chi dona senza nulla in cambio |
| — | `RUOLO_NEW_ENTRY` | `GUEST` | `DISCORD_GUEST_ROLE` | `RuoliDiscordService` | ruolo di chi entra nel server |
| — | `RUOLO_ADMIN` | `ADMIN` | `DISCORD_ADMIN_ROLE` | `RuoliDiscordService` | ruolo degli amministratori |
| — | `RUOLO_MODERATORE` | `MODERATORE` | — | ⚠️ **nessuno** | predisposto, nessuna funzionalità lo legge |
| — | `PERCENTUALE_STRIPE_SECONDARIO` | `30` | `50` | `StripeAccountSelector` | quota di incassi Stripe da tenere sull'account secondario |

I valori nella colonna «Valore iniziale» sono quelli della migration `V2`, tranne l'ultimo che
arriva da `V7`. In produzione possono essere diversi: `V2` è marcata come baseline e non viene
eseguita.

**`BATCH_VERIFICA_ABBONAMENTI` + `BACKUP_DB_ABILITATO`** governano il batch delle 22:00, il cui
cron `0 0 22 * * *` è fisso nel codice: prima di `V7` l'unico modo di fermarlo era spegnere
l'applicazione. Sono **due interruttori distinti** perché il backup è l'unica rete di sicurezza sui
dati e deve poter continuare anche quando si ferma la gestione degli abbonamenti:

| `BACKUP_DB_ABILITATO` | `BATCH_VERIFICA_ABBONAMENTI` | Alle 22:00 |
|---|---|---|
| `false` | `false` | nulla, il metodo esce subito |
| `true` | `false` | solo il backup del database |
| `false` | `true` | solo rinnovi, scadenze e degradi di ruolo |
| `true` | `true` | backup, poi rinnovi, scadenze e degradi |

Serve soprattutto negli ambienti di collaudo che girano su una copia dei dati di produzione, dove
il batch degraderebbe ruoli e azzererebbe le date di scadenza su utenti veri.

**Le cinque chiavi `RUOLO_*`** sono il contratto fra il codice e il server Discord. La chiave
descrive la **funzione**, il valore è il **nome** che quel ruolo ha su quel server:

| Chiave (funzione) | Valore su questa istanza |
|---|---|
| `RUOLO_ABBONATO` | `SUPPORTER_MEMBER` |
| `RUOLO_DONAZIONE` | `GOLD_SUPPORTER_MEMBER` |
| `RUOLO_NEW_ENTRY` | `GUEST` |
| `RUOLO_ADMIN` | `ADMIN` |
| `RUOLO_MODERATORE` | `MODERATORE` |

Il codice chiede `ruoloAbbonato()` e non sa come si chiami: nessun nome di ruolo compare nei
sorgenti. Portare il prodotto su un altro server significa cambiare questi cinque valori.

Le righe sono inserite da `V8` e devono esistere sempre; se una viene cancellata,
`RuoliDiscordService` la ricrea all'avvio con il valore della variabile d'ambiente. Le
`DISCORD_*_ROLE` restano solo come rete di sicurezza: la tabella è la fonte di verità.

I valori di fabbrica sono per definizione un'ipotesi, perciò `RuoliDiscordService` confronta le due
fonti a ogni avvio e segnala le differenze:

```
WARN  Ruolo RUOLO_SUPPORTER_MEMBER: a database vale 'SUPPORTER_MEMBER' ma l'ambiente
      dichiara 'Supporter'. Vale il valore a database: se non è quello giusto il bot
      non troverà il ruolo su Discord.
```

Il disallineamento si vede così all'avvio, non quando un utente resta senza ruolo dopo aver pagato.
Il servizio **non corregge** da sé: sovrascrivere cancellerebbe una personalizzazione voluta.

⚠️ Modificare una di queste chiavi **non rinomina il ruolo su Discord**: dice al bot con quale nome
cercarlo. Se il nome non corrisponde a un ruolo esistente sul server, l'assegnazione fallisce con
«Ruolo … non trovato nel server» nei log.

## Le tre righe che nessuno legge

`Wallet CrazyHorse`, `Wallet Emme`, `Wallet Tese`: chiavi con spazi e nomi propri, che usano la
tabella come blocco note. Nessun `getConfigurationValue` le richiede.

Hanno anche **valore e descrizione invertiti** — l'indirizzo del wallet sta in `descrizione`, la
rete in `valore_configurazione` — e non compaiono in `V2`: sono state inserite a mano in
produzione. Lasciate così per scelta esplicita durante la revisione del 2026-08-14.

> Erano cinque: `PERCENTUALE_COMMISSIONI_STRIPE` e `QUOTA_FISSA_COMM_STRIPE`, residui di un calcolo
> commissioni fatto a mano prima che la fee venisse letta da Stripe, sono state eliminate da `V9`
> ([[Riconciliazione della fee Stripe]]).

## Note per parametro

**`N_TENTATIVI_VERIFICA` + `TEMPO_LIMITE_VERIFICA`** — il conteggio include anche i tentativi
**riusciti**, non solo quelli errati; il messaggio all'utente cita valori fissi «3 tentativi in 2h»
anche se la configurazione cambia. Vedi [[Tentativo di verifica transazione]].

**`COMANDI_BOT_ABILITATI`** — a `false` il bot smette di rispondere a **qualunque** cosa l'utente
avvii: comandi testuali, bottoni, menu a tendina, finestre di inserimento. A ognuno risponde con il
testo `bot.disabilitato` e non fa altro. Serve a fermare tutto durante una manutenzione senza
spegnere il servizio.

Restano attivi di proposito i fatti che **non sono comandi**: il censimento di chi entra nel server,
la reazione al disclaimer, l'attribuzione dei referral, il [[Batch verifica abbonamenti]] e i
webhook dei pagamenti già avviati. Fermarli significherebbe perdere utenti e incassi, non sospendere
un servizio.

**Gli amministratori sono esenti**, su tutte le superfici e non solo sul comando `!Admin`: quel
comando apre un pannello fatto di bottoni e menu, che altrimenti si aprirebbe muto. Il ruolo viene
verificato **solo a bot sospeso** — finché l'interruttore è acceso non parte alcuna chiamata a
Discord.

Per **riaccendere** il bot si modifica comunque questa riga a database: nessun comando del pannello
admin scrive in `cfg_server`.

Se la chiave manca si assume `true`: una configurazione persa non deve zittire il solo canale con
cui gli utenti pagano e chiedono assistenza.

**`LOG_CONSERVAZIONE_GIORNI`** — il batch delle 22:00 cancella le righe di `sys_log_server` più
vecchie di tanti giorni. Il numero fa anche da interruttore: `0` conserva tutto, ed è il valore
assunto anche se la chiave manca o non contiene un numero — nessun log deve sparire per una
configurazione sbagliata. La pulizia avviene **dopo** il backup ([[Log operativo]]).

**`PIONIERI_ABILITATI`** — spegne l'intero meccanismo dei [[Membri pionieri]]: tutti gli utenti
tornano allo stesso livello e pagano `BASIC`, promo comprese. Nulla viene perso, è reversibile.

**`PIONIERI` e `PIONIERI_ASSEGNATI`** — il tetto dei posti pioniere e quelli già consumati. Alzare
il tetto riapre le assegnazioni; abbassarlo sotto il valore di `PIONIERI_ASSEGNATI` le chiude, senza
togliere nulla a chi il posto ce l'ha già. Il contatore lo incrementa il codice al pagamento: se
assegni un posto a mano scrivendo `membro_pioniere`, incrementalo anche tu ([[Membri pionieri]]).

**`N_GIORNI_DOPO_SCADENZA`** — abbassarlo rende il degrado più aggressivo; alzarlo lascia l'accesso
più a lungo dopo la scadenza. Vedi [[Batch verifica abbonamenti]].

**`N_ORE_DURATA_LINK_STRIPE`** — vale **solo** per i link delle donazioni. La durata delle sessioni
masterclass è **fissa nel codice** a 2 ore e non è configurabile.

**`MASTERCLASS_DURATA_LINK_ORE`** — più è breve, minore la finestra di ri-condivisione del video;
troppo breve rischia che l'acquirente non riesca a scaricare ([[Storage R2]]).

**I tre flag booleani** — la conversione è `Boolean::parseBoolean`: qualsiasi valore diverso da
`"true"` (case-insensitive) viene letto come `false`. Un `"1"` **non** vale `true`. Vedi
[[Blocco dei pagamenti]].

**`PERCENTUALE_STRIPE_SECONDARIO`** decide quanta parte degli incassi Stripe deve stare sul secondo
account: si intende **sugli euro**, non sul numero di transazioni. `50` riproduce la ripartizione
paritaria che era l'unico comportamento possibile prima di `V10`. Valori fuori da 0-100 vengono
ignorati con un warning e si ricade sul 50%. Nessun effetto finché il secondo account non ha le
chiavi. Vedi [[Bilanciamento degli account Stripe]] per la formula e i casi limite.

## Regole operative

```sql
-- Leggere
SELECT * FROM server_config;

-- Modificare (effetto immediato, nessun riavvio)
UPDATE server_config SET valore_configurazione = 'false'
 WHERE nome_configurazione = 'DONAZIONI_LIBERE_ABILITATE';
```

⚠️ Due avvertenze:

1. **Non cancellare una riga per disabilitare**: senza riga vale il default nel codice, che per i
   flag è `true`. Vale anche per `BATCH_VERIFICA_ABBONAMENTI`: cancellarlo **riaccende** il batch.
2. Ogni nuovo parametro va introdotto con una **migration Flyway**, non con un `INSERT` a mano
   ([[Schema del database]]).

Dal 2026-08-11 `nome_configurazione` ha il vincolo **`UNIQUE`** (`uq_server_config_nome`, aggiunto
da `V4` dopo aver deduplicato le righe esistenti): un `INSERT` duplicato ora fallisce invece di
creare una seconda riga che nessuno avrebbe letto.

## Voci correlate
- [[Configurazione di server]]
- [[Blocco dei pagamenti]]
- [[Batch verifica abbonamenti]]
- [[Schema del database]]
