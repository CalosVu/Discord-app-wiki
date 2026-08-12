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
| `GET` | `/payment/success?session_id=…` | il browser dell'utente | nessuna (pagina di cortesia) |
| `GET` | `/payment/cancel` | il browser dell'utente | nessuna |
| `GET` | `/swagger-ui.html`, `/api-docs` | sviluppatori | **disabilitati in `prod`** |
| `GET` | `/actuator/health`, `/actuator/info` | monitoraggio | esposti solo questi due |

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
