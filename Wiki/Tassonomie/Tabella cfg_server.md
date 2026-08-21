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

Sono **tutte obbligatorie**: elencate in `cfg_server_obbligatorie`, non cancellabili, verificate
all'avvio. La colonna «Tipo» è quella dichiarata lì, e un valore che non la rispetta **blocca il
boot**.

| `nome_configurazione` | Valore | Tipo | Chi lo legge | Effetto |
|---|---|---|---|---|
| `N_TENTATIVI_VERIFICA` | `3` | INTERO | `CryptoPaymentService` | tentativi di verifica crypto nella finestra |
| `TEMPO_LIMITE_VERIFICA` | `2` | INTERO | `CryptoPaymentService` | ampiezza della finestra dei tentativi, in **ore** |
| `VERIFICA_CRYPTO_FINESTRA_ORE` | `24` | INTERO | `CryptoPaymentService` | ore entro cui una transazione è verificabile. `0` disattiva |
| `COMANDI_BOT_ABILITATI` | `true` | BOOLEANO | `ComandiBotService` | interruttore generale delle interazioni col bot |
| `LOG_CONSERVAZIONE_GIORNI` | `365` | INTERO | `VerificaAbbonamentiBatch` | conservazione del [[Log operativo]]. `0` conserva tutto |
| `PRELIEVI_UTENTI_AUTORIZZATI` | vuoto | LISTA_ID_DISCORD | `AutorizzazioniAdminService` | chi vede la voce [[Prelievo\|Prelievi]] del menu admin. **Vuoto = tutti gli admin** |
| `NOTIFICHE_ADMIN_AUTORIZZATI` | vuoto | LISTA_ID_DISCORD | `DiscordService` | chi riceve in DM le notifiche di **pagamento** e **degrado** ([[Notifiche agli amministratori]]). **Vuoto = tutti gli admin**. Gli avvisi tecnici arrivano comunque a tutti |
| `REPORT_UTENTI_AUTORIZZATI` | vuoto | LISTA_ID_DISCORD | `AutorizzazioniAdminService` | chi apre Report Saldo, Pagamenti e Completo ([[Reportistica]]). **Vuoto = tutti gli admin**. Gli altri report del menu restano di tutti |
| `PIONIERI_ABILITATI` | `true` | BOOLEANO | `PianoUtenteService` | a `false` tutti pagano `BASIC` |
| `PIONIERI` | `50` | INTERO | `PianoUtenteService` | tetto dei posti pioniere. `0` = nessun pioniere, mai |
| `PIONIERI_ASSEGNATI` | quelli esistenti | INTERO | `PianoUtenteService` | posti consumati. **Non si decrementa mai** |
| `N_GIORNI_DOPO_SCADENZA` | `3` | INTERO | `VerificaAbbonamentiBatch` | tolleranza dopo la scadenza prima del degrado |
| `N_ORE_DURATA_LINK_STRIPE` | `5` | INTERO | `StripePaymentService` | validità del link di checkout delle donazioni |
| `MASTERCLASS_DURATA_LINK_ORE` | `3` | INTERO | `MasterclassPaymentNotificationService` | validità del presigned URL R2 |
| `PAGAMENTI_NUOVE_ISCRIZIONI_ABILITATE` | `true` | BOOLEANO | `PagamentiAbilitazioneService` | abilita il **primo** Supporter Member |
| `PAGAMENTI_RINNOVI_ABILITATI` | `true` | BOOLEANO | `PagamentiAbilitazioneService` | abilita i **rinnovi** |
| `DONAZIONI_LIBERE_ABILITATE` | `true` | BOOLEANO | `PagamentiAbilitazioneService` | abilita il [[Sostegno libero]] |
| `BATCH_VERIFICA_ABBONAMENTI` | `true` | BOOLEANO | `VerificaAbbonamentiBatch` | promemoria, scadenze, degradi di ruolo |
| `BACKUP_DB_ABILITATO` | `true` | BOOLEANO | `VerificaAbbonamentiBatch` | backup del database alle 22:00 |
| `PERCENTUALE_STRIPE_SECONDARIO` | `30` | INTERO | `StripeAccountSelector` | quota di incassi sull'account secondario |
| `RUOLO_ABBONATO` | `SUPPORTER_MEMBER` | TESTO | `RuoliDiscordService` | ruolo di chi ha un abbonamento attivo |
| `RUOLO_DONAZIONE` | `GOLD_SUPPORTER_MEMBER` | TESTO | `RuoliDiscordService` | ruolo di chi dona senza nulla in cambio |
| `RUOLO_NEW_ENTRY` | `GUEST` | TESTO | `RuoliDiscordService` | ruolo di chi entra nel server |
| `RUOLO_ADMIN` | `ADMIN` | TESTO | `RuoliDiscordService` | ruolo degli amministratori |
| `RUOLO_MODERATORE` | `MODERATORE` | TESTO | ⚠️ **nessuno** | predisposto, nessuna funzionalità lo legge |

Più le tre annotazioni `[VU] Wallet …`, che **non** sono configurazione: vedi in fondo.

I valori in colonna sono quelli delle migration. In produzione possono essere diversi: `V2` è marcata
come baseline e non viene eseguita.

> **Non esistono più valori di ripiego nel codice.** `getConfigurationValue` non accetta un default e
> solleva se la chiave manca: la tabella «Default nel codice» che stava qui è stata rimossa perché
> quei valori non ci sono più.

**`BATCH_VERIFICA_ABBONAMENTI` + `BACKUP_DB_ABILITATO`** governano il batch delle 22:00, il cui
cron `0 0 22 * * *` è fisso nel codice: prima di `V7` l'unico modo di fermarlo era spegnere
l'applicazione. Sono **due interruttori distinti** perché il backup è l'unica rete di sicurezza sui
dati e deve poter continuare anche quando si ferma la gestione degli abbonamenti:

| `BACKUP_DB_ABILITATO` | `BATCH_VERIFICA_ABBONAMENTI` | Alle 22:00 |
|---|---|---|
| `false` | `false` | solo pulizia del log e riallineamento dei nomi |
| `true` | `false` | backup, pulizia del log, riallineamento dei nomi |
| `false` | `true` | pulizia, nomi, poi rinnovi, scadenze e degradi |
| `true` | `true` | tutto |

Pulizia del log e riallineamento dei nomi **non dipendono da questi due flag**: hanno i propri
criteri (`LOG_CONSERVAZIONE_GIORNI` e la lista membri di Discord), quindi il batch non esce mai
subito del tutto. Vedi [[Batch verifica abbonamenti]].

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

Le righe sono inserite da `V8` e la tabella è **l'unica fonte**.

> [!warning] Le variabili `DISCORD_*_ROLE` non esistono più
> Fino ad agosto 2026 c'era una seconda fonte: quattro variabili d'ambiente usate come ripiego, e
> `RuoliDiscordService` ricreava da quelle una riga cancellata, confrontando le due fonti a ogni
> avvio per segnalare le divergenze.
>
> Rimosse con `V29`: risolvevano un problema che non esiste più — ora la riga **non si può
> cancellare** e l'avvio fallisce se manca. Due fonti potevano soprattutto **divergere**, ed era
> proprio per questo che serviva il confronto all'avvio.
>
> `DISCORD_SUPPORTER_MEMBER_ROLE`, `DISCORD_GOLD_SUPPORTER_MEMBER_ROLE`, `DISCORD_GUEST_ROLE` e
> `DISCORD_ADMIN_ROLE` si possono togliere dal `.env`: non le legge più nessuno.

Il disallineamento si vede così all'avvio, non quando un utente resta senza ruolo dopo aver pagato.
Il servizio **non corregge** da sé: sovrascrivere cancellerebbe una personalizzazione voluta.

⚠️ Modificare una di queste chiavi **non rinomina il ruolo su Discord**: dice al bot con quale nome
cercarlo. Se il nome non corrisponde a un ruolo esistente sul server, l'assegnazione fallisce con
«Ruolo … non trovato nel server» nei log.

## 🔒 Le configurazioni obbligatorie non si cancellano, e senza di esse l'app non parte

Da `V29` valgono due regole insieme:

1. **`cfg_server_obbligatorie`** elenca le chiavi che il codice legge. Una chiave esterna con
   `ON DELETE RESTRICT` verso `cfg_server` fa **rifiutare da MySQL** la cancellazione della riga
   corrispondente — per qualunque utente, **root compreso**;
2. **`ConfigurazioneObbligatoria`** verifica all'avvio che ogni chiave elencata esista e contenga un
   valore del tipo dichiarato. Se manca qualcosa, **l'applicazione non parte**.

I valori di ripiego nel codice sono stati **rimossi**: `getConfigurationValue` non accetta più un
terzo parametro e solleva se la chiave manca.

### Perché non basta dire «non cancellare»

L'applicazione non si romperebbe: con i vecchi ripieghi partiva comunque. Il problema è che **il
ripiego non coincideva con il valore desiderato**, e in due casi spegneva una protezione:

| Chiave cancellata | Vecchio ripiego | Conseguenza silenziosa |
|---|---|---|
| `VERIFICA_CRYPTO_FINESTRA_ORE` | `0` | il controllo temporale sulle transazioni crypto **si spegneva** ([[Pagamenti crypto Arbitrum]]) |
| `PIONIERI_ABILITATI` | `false` | sistema pionieri spento, tutti al prezzo pieno |
| `PIONIERI` | `0` | nessun posto pioniere disponibile |
| `PERCENTUALE_STRIPE_SECONDARIO` | `50` | ripartizione fra i due account diversa |

Nessun errore, nessun log: solo un comportamento diverso da quello atteso. È il caso peggiore, perché
non se ne accorge nessuno.

> **Per disattivare una funzione si usa il suo valore** (`false`, `0`), **non il `DELETE`.** Ogni
> interruttore è progettato per questo.

### La tabella è anche l'inventario

`cfg_server_obbligatorie` contiene nome, **tipo** e una nota, ed è la
**sola fonte**: il codice legge l'elenco da lì invece di tenerne una copia in Java. Con due elenchi
separati, aggiungere una chiave in un posto e dimenticarla nell'altro avrebbe prodotto una
configurazione obbligatoria ma cancellabile, o viceversa.

Ne segue che **per rendere obbligatoria una configurazione basta una migration**, senza toccare
codice.

I tipi disponibili, e cosa accettano:

| Tipo | Valori validi |
|---|---|
| `INTERO` | cifre, anche negative. Lo zero è ammesso, e su diverse chiavi significa «disattivato» |
| `BOOLEANO` | esattamente `true` o `false`: né `si`, né `1`, né `on` |
| `TESTO` | testo **non vuoto** — è il caso dei nomi dei ruoli Discord |
| `LISTA_ID_DISCORD` | ID Discord separati da virgola, **oppure vuoto** |

L'ultimo è nato con la `V33` per `PRELIEVI_UTENTI_AUTORIZZATI`, dove il vuoto è il valore
predefinito e significa «tutti gli amministratori»: con `TESTO` l'avvio si sarebbe bloccato. Valida
anche il formato — 17-20 cifre — così incollare la menzione `@Calos` invece dell'ID si scopre
all'avvio, e non il giorno in cui qualcuno non riesce ad aprire i prelievi.

La `V34` ha aggiunto `NOTIFICHE_ADMIN_AUTORIZZATI` e la `V35` `REPORT_UTENTI_AUTORIZZATI`, con la
stessa convenzione. Le tre chiavi sono **indipendenti**: si può leggere i report senza poter
registrare prelievi, ricevere le notifiche degli incassi senza vedere i saldi, e così via. Tutte
*restringono* fra gli amministratori e non promuovono nessuno.

Prelievi e report passano da `AutorizzazioniAdminService`; le notifiche sono lette dentro
`DiscordService`, perché farle passare di lì creerebbe una dipendenza circolare — quel servizio
serve proprio a sapere chi è amministratore.

### Come si aggiunge una riga

L'ordine conta: la chiave esterna va **da `cfg_server_obbligatorie` verso `cfg_server`**, quindi la
riga «figlia» non può precedere la «padre».

```sql
-- Configurazione dell'applicazione (obbligatoria):
INSERT INTO cfg_server (nome_configurazione, valore_configurazione, descrizione)
VALUES ('NUOVA_CHIAVE', '10', 'a cosa serve');                        -- 1° la padre

INSERT INTO cfg_server_obbligatorie (nome_configurazione, tipo, note)
VALUES ('NUOVA_CHIAVE', 'INTERO', 'nota per chi legge');              -- 2° la figlia

-- Annotazione operativa (cancellabile): solo la prima riga, con prefisso [VU]
INSERT INTO cfg_server (nome_configurazione, valore_configurazione, descrizione)
VALUES ('[VU] Qualcosa', 'valore', 'appunto');
```

⚠️ **Se il codice legge una chiave che non è fra le obbligatorie**, la verifica d'avvio non la
controlla e l'errore si manifesta a runtime, nel momento in cui serve.

### Il prefisso `[VU]` è una convenzione, non un meccanismo

Verificato sul database: una riga **senza** `[VU]` e non elencata fra le obbligatorie **si cancella
senza problemi**. L'unica cosa che impedisce il `DELETE` è la presenza in `cfg_server_obbligatorie`.

Il prefisso serve alla lettura: aprendo `cfg_server` distingui a occhio le tue annotazioni dalla
configurazione dell'applicazione, senza incrociare l'altra tabella.

### Perché una chiave esterna e non un trigger

Il primo tentativo era un trigger `BEFORE DELETE`. **MySQL lo rifiuta** con l'errore `1419` quando il
binary logging è attivo e l'utente non ha il privilegio `SUPER` — il caso sia in locale sia in
produzione, e concedere `SUPER` all'utente applicativo sarebbe peggio del problema che risolve.

La chiave esterna ottiene lo stesso risultato senza privilegi speciali. Lezione che vale oltre questo
caso: **i trigger MySQL non sono creabili con i privilegi ordinari** quando il binlog è attivo.

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

**`VERIFICA_CRYPTO_FINESTRA_ORE`** — una transazione crypto è verificabile solo entro tante ore dal
blocco che la contiene. È **l'unica difesa** contro il riscatto di trasferimenti storici verso il
wallet del progetto, dato che il mittente on-chain non è verificabile per chi paga da un exchange
([[Pagamenti crypto Arbitrum]]).

Il valore `24` non è arbitrario: sugli 82 pagamenti reali il 92,7% viene verificato entro 30 minuti,
ma 3 su 82 sono arrivati dopo 2h30. `0` disattiva il controllo — ed essendo la chiave obbligatoria,
uno zero lì significa che **qualcuno l'ha scelto**, non che manca una riga.

**`LOG_CONSERVAZIONE_GIORNI`** — il batch delle 22:00 cancella le righe di `sys_log_server` più
vecchie di tanti giorni. Il numero fa anche da interruttore: `0` conserva tutto. La pulizia avviene
**dopo** il backup ([[Log operativo]]).

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
