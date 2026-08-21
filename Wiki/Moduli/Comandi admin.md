---
tipo: modulo
titolo: Comandi admin
alias: [menu Admin, pannello di controllo]
tag: [dominio/bot, dominio/comandi, dominio/admin]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-20
stato: stabile
---

# Comandi admin

Le funzioni riservate a chi ha il ruolo admin sulla guild. Il controllo è
`discordService.isAdmin(discordId)`, che verifica il ruolo **in tempo reale su Discord**
([[Ruoli Discord]]): non esiste una tabella di amministratori.

## Come si apre il pannello

| Comando | Nota |
|---|---|
| `!Admin` | apre il menu a tendina «pannello di controllo» |
| `!open-…` | **qualsiasi** comando che inizia con `!open-` apre lo stesso menu |
| `!report_masterclass` | scorciatoia diretta al report masterclass per relatore |
| `!profitti_masterclass` | scorciatoia diretta ai profitti globali masterclass |
| `!SyncReferral` | attribuzione manuale dei referral non risolti (vedi sotto) |

Chi non è admin e scrive `!Admin` non riceve **nessuna risposta**: il comando è silenziosamente
ignorato.

## Le otto voci del menu

Quattro voci sono **riservate**: compaiono solo a chi è elencato nella chiave corrispondente di
[[Tabella cfg_server]] — `PRELIEVI_UTENTI_AUTORIZZATI` per i prelievi,
`REPORT_UTENTI_AUTORIZZATI` per i tre report economici. Elenco vuoto significa «tutti gli
amministratori», ed è il valore predefinito. Il controllo è ripetuto dentro ogni handler, perché un
componente Discord già inviato resta cliccabile.

| Voce | Riservata | Cosa fa |
|---|---|---|
| **Prelievi** | 🔒 | gestione completa: crea, elenca, modifica, annulla, cancella → [[Prelievo]] |
| **Report Saldo** | 🔒 | Crypto e Stripe — depositi, prelievi, saldo *ad adesso*. Con **due** conti Stripe le sezioni diventano Primario e Secondario, ognuna col titolo che mostra quota attuale e obiettivo di ripartizione |
| **Report Pagamenti** | 🔒 | menu dei periodi (o date a mano) → **l'elenco di chi ha pagato**, dal più recente: data, utente, importo, canale, abbonamento o donazione, email. In coda i totali per canale |
| **Report Completo** | 🔒 | menu dei periodi (o date a mano) → entrate per canale con media e confronto sul periodo precedente, composizione abbonamenti/donazioni, prelievi, saldo del periodo, nuovi iscritti e rinnovi |
| **Scadenze Mese** | | elenco degli utenti in scadenza nel mese corrente, con data |
| **Report Agente** | | selezione agente → periodo → **lo stesso report** che vede l'agente |
| **Report Masterclass** | | selezione relatore → masterclass → periodo → vendite |
| **Profitti Masterclass** | | selezione periodo → profitti globali con breakdown per relatore |

> [!warning] Storia / claim superate
> Fino al 2026-07-26 il menu aveva **nove** voci: la nona era *Fix Referral*, che prometteva di
> riattribuire gli utenti senza invito ma **non poteva funzionare** (analisi in
> [[2026-07-25 Referral non attribuito e Fix Referral inefficace]]). È stata rimossa e sostituita dal
> comando `!SyncReferral`.

## Dettaglio: `!SyncReferral`

Attribuzione manuale dei referral rimasti irrisolti ([[Sistema referral e commissioni]]). Flusso a due
passi, con conferma:

```
!SyncReferral
  ├─ nessun utente in attesa → «Nessun utente senza referral: sync non necessario» e finisce
  └─ N utenti in attesa      → embed con:
                                • elenco (username, data ingresso, tentativi, motivo)
                                • inviti con utilizzi non attribuiti, con la differenza
                                • ESITO PREVISTO, calcolato prima di agire
                               + pulsanti [▶️ Avvia Sync] [✖️ Annulla]
```

L'«esito previsto» dice in anticipo se l'attribuzione è possibile o se il caso è ambiguo: si evita di
lanciare un'operazione che non farà nulla. A sync eseguito, il report finale distingue **attribuiti**
(con l'invito a cui sono stati assegnati) e **rimasti in attesa** (con il motivo).

Non esiste nessun job schedulato: l'operazione parte solo su richiesta.

Dopo ogni operazione il menu viene **rinviato in chat** (`resendMenu`), così non serve ridigitare
`!Admin`.

## Dettaglio: Prelievi

Non è più una singola finestra di inserimento ma una **gestione completa** — creare, elencare,
modificare, annullare, cancellare — perché il prodotto andrà a clienti senza accesso al database.

```
📥 Prelievi
   ├─ ➕ Nuovo → menu canale/valuta → finestra (campi diversi per crypto e Stripe)
   ├─ 🕒 Ultimi 10
   └─ 📅 Cerca per periodo
          └─ scheda del movimento → ✏️ Modifica · 🔁 Stato · 🗑️ Elimina
```

Il canale si sceglie da un menu (`🪙 Crypto · USDT`, `💳 Stripe Primario · EUR`, …), non si scrive:
serve anche a stare dentro il limite di cinque campi per finestra. Per Stripe non vengono chiesti
hash e wallet, che un bonifico non ha.

⚠️ **La verifica on-chain è stata rimossa** il 2026-08-20, insieme all'obbligo di hash e wallet.
Rendeva i prelievi Stripe impossibili senza dati inventati, e su un movimento che l'amministratore
ha già eseguito non aggiungeva nulla. Vedi [[Prelievo]] per validazioni, stati e tracciamento.

## Dettaglio: i report per periodo

Le date si inseriscono come `gg/mm/aaaa` e sono validate: la data di inizio non può essere più
vecchia di **1 anno**, la data di fine non può essere nel **futuro**, e l'inizio non può superare la
fine. Vedi [[Reportistica]] per il significato dei numeri.

## Dettaglio: Report Agente

Serve a vedere **esattamente** ciò che vede l'agente con `!mieiref`: gli embed sono costruiti dalla
stessa funzione condivisa, così le due viste non possono divergere. Il percorso è
agente → periodo (mese corrente o precedente) → due embed, Stripe in EUR e crypto in USD.

## Restano attivi a bot sospeso

`COMANDI_BOT_ABILITATI` a `false` zittisce il bot per tutti, ma **non per gli amministratori**:
comandi, bottoni, menu e finestre continuano a funzionare per chi ha il ruolo. Serve a poter
lavorare mentre il bot è chiuso agli utenti ([[Comandi utente]]).

Per **riaccenderlo** si passa comunque dal database — vedi qui sotto.

## Cosa NON si può fare dal bot

Non esistono comandi per: creare o modificare [[Agente|agenti]], [[Relatore|relatori]],
[[Masterclass]], [[Utente lifetime]], voci del [[Catalogo servizi]] o parametri di
[[Tabella cfg_server]]. Tutte queste operazioni si fanno **a mano via SQL** sul database.

I [[Prelievo|prelievi]] sono la prima eccezione: dal 2026-08-20 hanno una gestione completa dal
bot. È il modello a cui dovranno adeguarsi le altre voci quando il prodotto verrà venduto, perché
un cliente non avrà un client SQL a cui appoggiarsi.

## Voci correlate
- [[Reportistica]]
- [[Comandi agenti]]
- [[Comandi relatori]]
- [[Prelievo]]
