---
tipo: tassonomia
titolo: Endpoint REST
alias: [endpoint, API, webhook]
tag: [dominio/api]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Endpoint REST

La superficie HTTP **completa** dell'applicazione. È deliberatamente minima: quasi tutta
l'interazione passa dal bot Discord, non dall'HTTP.

## Gli endpoint

| Metodo | Percorso | Chi lo chiama | Protezione |
|---|---|---|---|
| `POST` | `/api/webhooks/stripe` | Stripe (account PRIMARIO) | firma webhook del primario |
| `POST` | `/api/webhooks/stripe/secondario` | Stripe (account SECONDARIO) | firma webhook del secondario |
| `POST` | `/api/webhooks/stripe/masterclass/relatore/{relatoreId}` | Stripe (account del relatore) | firma webhook di quel relatore |
| `POST` | `/api/webhooks/stripe/masterclass` | Stripe Connect — modello **congelato** | firma webhook Connect |
| ~~`GET`~~ | ~~`/api/verifica-accesso/{discordId}`~~ | **rimosso** il 2026-08-12 ([[Integrazione VuTracker]]) | — |
| `GET` | `/payment/success?session_id=…&account=…` | il browser dell'utente | nessuna (pagina di cortesia) |
| `GET` | `/payment/cancel` | il browser dell'utente | nessuna |
| `GET` | `/swagger-ui.html`, `/api-docs` | sviluppatori | **disabilitati in `prod`** |

> [!warning] Actuator non esiste
> Questa tabella elencava `/actuator/health` e `/actuator/info` come «esposti solo questi due».
> **Non è mai stato vero**: la dipendenza `spring-boot-starter-actuator` non è nel progetto, non c'è
> alcuna property `management.*`, e quegli URL rispondono `404`. Verificato il 2026-08-18. Se un
> giorno servisse il monitoraggio, la dipendenza va aggiunta — e allora sì che gli endpoint vanno
> ristretti, perché di default ne espone più di due.

## Cosa mostra `/payment/success`

Importo, tipo di donazione e mesi. **Non l'ID Discord**, che fino al 2026-08-18 compariva in chiaro:
la pagina è pubblica, e chiunque avesse avuto il link — dalla cronologia, da uno screenshot, dai log
di un proxy — avrebbe saputo *chi* aveva pagato, quanto e per cosa. Il riepilogo con i dati
personali resta il DM del bot, dove l'utente è autenticato dall'essere sé stesso.

Il parametro `account` dice su quale dei due account Stripe è stata creata la sessione: dal solo
`session_id` non si capisce, e la pagina userebbe sempre la chiave del Primario — mostrando un
errore a chi ha pagato sul Secondario. Se manca o non è riconosciuto vale `PRIMARIO`, quindi i link
generati prima della modifica continuano a funzionare. Manipolarlo non dà accesso a nulla: al più fa
fallire la lettura della sessione.

Non esiste nessun endpoint di login, registrazione, gestione utenti o amministrazione: `/admin/**` è
configurato in Spring Security ma **nessun controller** è mappato lì
([[Sicurezza e autenticazione]]).

## Gli eventi Stripe gestiti

Su **tutti** gli endpoint webhook, solo due:

| Evento | Cosa innesca |
|---|---|
| `checkout.session.completed` | registrazione del pagamento, ruolo o erogazione del contenuto |
| `charge.updated` | riconciliazione della fee ([[Riconciliazione della fee Stripe]]) |

Qualunque altro evento viene solo loggato. **Entrambi** devono essere registrati nel Dashboard di
ogni account, altrimenti gli importi restano lordi per sempre.

## Come si distingue un pagamento masterclass su un endpoint supporter

Lo stesso account Stripe può consegnare all'endpoint supporter anche eventi di masterclass. Il
`WebhookController` controlla la presenza del metadata **`masterclass_id`** e in quel caso **esce
subito**, lasciando la gestione all'endpoint dedicato.

## L'endpoint dinamico per relatore

`/api/webhooks/stripe/masterclass/relatore/{relatoreId}` — il `relatoreId` nel percorso serve a
scegliere il webhook secret con cui verificare la firma. È il motivo per cui **l'id del relatore
deve combaciare in tre punti** ([[Relatore]]).

## Il proxy davanti

In `prod` l'applicazione ascolta su `127.0.0.1:8080`: tutti gli endpoint sono raggiungibili solo
attraverso nginx, che espone `https://discord.<dominio>` ([[Deploy e CI-CD]]).

⚠️ `curl -I` su un endpoint restituisce **403**: è una `HEAD`, e Spring accetta solo i metodi
mappati. Non è un errore di configurazione.

## Voci correlate
- [[Pagamenti Stripe]]
- [[Sistema masterclass]]
- [[Integrazione VuTracker]]
- [[Sicurezza e autenticazione]]
