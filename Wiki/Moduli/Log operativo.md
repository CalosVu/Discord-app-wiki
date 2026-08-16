---
tipo: modulo
titolo: Log operativo
alias: [sys_log_server, LogServer, LogServerService, log]
tag: [dominio/infrastruttura]
fonti: [Codice Discord-access-app]
creato: 2026-08-13
aggiornato: 2026-08-16
stato: stabile
---

# Log operativo

Il registro dei fatti che riguardano **denaro e accessi**: chi ha pagato e chi ha perso il ruolo.
Tabella `sys_log_server`, entità `LogServer`, scritture da `LogServerService`.

Da non confondere con i log applicativi su file (`/opt/discord-bot/logs`), che registrano tutto
quello che succede e ruotano: qui restano solo gli eventi che si vogliono poter ricostruire a
distanza di mesi.

## Cosa viene registrato

| Tipo evento | Quando | Dove nel codice |
|---|---|---|
| `DEGRADO_RUOLO` | il batch delle 22:00 toglie il ruolo a un abbonamento scaduto | `VerificaAbbonamentiBatch`, subito dopo il cambio ruolo |
| `PAGAMENTO` | un pagamento è registrato, in euro (Stripe) o in crypto (USDT) | `CryptoPaymentService.savePaymentAndUpdateUser` |

La scrittura dei pagamenti è messa in `savePaymentAndUpdateUser` perché è il **punto unico** da cui
passano entrambi i canali: le crypto lo chiamano direttamente, Stripe lo raggiunge tramite
`StripePaymentNotificationService`. Intercettare i due flussi separatamente avrebbe significato
dimenticarne uno il giorno che se ne aggiunge un terzo.

## Campi

| Campo | Note |
|---|---|
| `data_evento` | ora italiana, da `DateValidator.oreItaliane()` |
| `tipo_evento` | `ENUM` nativo: aggiungere un valore richiede una migration |
| `discord_id`, `username` | chi. L'username è quello **al momento dell'evento** |
| `descrizione` | riga già formattata e leggibile senza consultare altre tabelle |
| `importo`, `valuta`, `metodo_pagamento`, `riferimento` | solo per i pagamenti |

`riferimento` contiene l'hash della transazione per le crypto, l'id della sessione per Stripe.

## Due scelte di progetto

**Nessuna chiave esterna verso gli utenti.** Un log deve restare leggibile anche se l'utente viene
cancellato: è la ragione per cui si conserva anche l'`username` oltre al `discord_id`, che da solo,
mesi dopo, non dice nulla a chi legge.

**Il log non può far fallire l'operazione che registra.** Ogni scrittura è isolata in `try/catch`:
se il salvataggio va in errore, il fatto finisce nei log applicativi e il flusso prosegue. Perdere
una riga di log è meno grave che rifiutare un pagamento già incassato o lasciare un utente scaduto
con il ruolo attivo.

## Gli indici e le domande a cui rispondono

| Indice | Domanda |
|---|---|
| `idx_sys_log_data` | cosa è successo in questo periodo |
| `idx_sys_log_discord` | cosa è successo a questo utente |
| `idx_sys_log_tipo` | quanti eventi di questo tipo |

Le tre letture di `LogServerRepository` corrispondono a queste tre domande.

## Quanto si conserva

Il batch delle 22:00 cancella le righe più vecchie di `LOG_CONSERVAZIONE_GIORNI`
([[Tabella cfg_server]]), impostata a **365** — un anno.

Il numero fa anche da interruttore: **`0` conserva tutto**, ed è il valore assunto anche se la
chiave manca o non contiene un numero. Nessuna riga deve sparire per una configurazione sbagliata.

> La pulizia viene eseguita **dopo il backup**, non prima: così quello che si cancella resta
> comunque recuperabile dall'ultimo backup. Un errore nella pulizia non ferma il resto del batch.

## Storia / claim superate

> [!warning] Sostituisce `log_service`, che non è mai stata scritta
> Fino al 2026-08-13 esisteva `log_service` con l'entità `LogService` e il servizio
> `SecurityLogService`. **Nessuna classe iniettava quel servizio**: la tabella è rimasta vuota per
> tutta la vita del progetto (zero righe in produzione).
>
> Aveva inoltre tre difetti che ne rendevano poco utile il recupero:
> - **due colonne di testo**, `messaggio` *e* `message`, residuo di una rinomina mai completata;
> - nessun tipo di evento, nessun importo: solo un messaggio libero;
> - una chiave esterna verso `disclaimer_accept`, quindi si poteva registrare un evento **solo per
>   chi aveva accettato il disclaimer**.
>
> Essendo vuota, `V11` l'ha eliminata e ricreata invece di migrarla.

## Voci correlate
- [[Batch verifica abbonamenti]]
- [[Pagamento]]
- [[Schema del database]]
