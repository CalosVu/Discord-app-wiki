---
tipo: concetto
titolo: Notifiche agli amministratori
alias: [notificaAdmin, DM agli admin, NOTIFICHE_ADMIN_AUTORIZZATI]
tag: [dominio/admin]
fonti: [Codice Discord-access-app]
creato: 2026-08-20
aggiornato: 2026-08-20
stato: stabile
---

# Notifiche agli amministratori

Il bot scrive in privato agli amministratori quando succede qualcosa che li riguarda. Da
**2026-08-20** i messaggi sono di due specie, con destinatari diversi.

## Le due specie

| Specie | Metodo | Chi le riceve | Esempi |
|---|---|---|---|
| **Eventi utente** | `notificaAdminEventiUtente` | gli ID in `NOTIFICHE_ADMIN_AUTORIZZATI`, o tutti gli admin se l'elenco è vuoto | un utente paga o rinnova, una [[Sostegno libero\|donazione libera]], un abbonamento scaduto che fa degradare il ruolo |
| **Avvisi tecnici** | `notificaAdmin` | **sempre tutti** gli amministratori | [[Ruoli Discord\|ruolo non assegnato]], errore di checkout, file R2 mancante di una masterclass |

La distinzione è deliberata: un evento utente è un fatto di gestione, e chi non se ne occupa non
deve ritrovarsi la casella piena. Un avviso tecnico è un **guasto**, e va visto da chiunque possa
rimediare — restringerlo significherebbe rischiare che nessuno dei presenti lo legga.

## L'elenco restringe, non allarga

`NOTIFICHE_ADMIN_AUTORIZZATI` ([[Tabella cfg_server]]) contiene ID Discord separati da virgola.
Vale la stessa convenzione di `PRELIEVI_UTENTI_AUTORIZZATI`:

- il filtro si applica **dentro** l'insieme di chi ha il ruolo admin: un ID in elenco che non è
  amministratore non riceve nulla;
- **elenco vuoto = tutti gli amministratori**, cioè il comportamento precedente alla chiave. Chi
  aggiorna e non tocca niente continua a ricevere le notifiche come sempre;
- se la chiave è illeggibile si ripiega su «tutti»: un errore di configurazione può far arrivare
  una notifica di troppo, non farne sparire una.

Le due chiavi sono indipendenti — si può ricevere le notifiche degli incassi senza poter registrare
[[Prelievo|prelievi]], e viceversa.

## Come si trova il destinatario

`ruoloAdmin(guild)` risolve il ruolo per nome (`RUOLO_ADMIN`), poi `findMembersWithRoles` carica i
membri che ce l'hanno. Se sul server esistono **due ruoli con lo stesso nome** viene usato il primo
e l'ambiguità finisce nei log come errore: è una condizione da sanare su Discord, perché decide sia
chi è amministratore sia chi riceve le notifiche.

Gli invii falliti passano da `logInvioFallito`: DM chiusi (`50007`) e nessun server in comune
(`50278`) diventano un `WARN` di una riga, il resto un errore con lo stack trace.

## Voci correlate
- [[Comandi admin]]
- [[Tabella cfg_server]]
- [[Ruoli Discord]]
- [[Prelievo]]
