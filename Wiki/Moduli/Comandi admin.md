---
tipo: modulo
titolo: Comandi admin
alias: [menu Admin, pannello di controllo]
tag: [dominio/bot, dominio/comandi, dominio/admin]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
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

| Voce | Cosa fa |
|---|---|
| **Salva Prelievo** | modale a 5 campi per registrare un'uscita → [[Prelievo]] |
| **Report Saldo** | tre sezioni: Crypto, Stripe **Lillo**, Stripe **Danny** — depositi, prelievi, saldo |
| **Report Pagamenti** | modale con range di date → totali e numero transazioni, crypto e Stripe |
| **Report Completo** | come sopra, più saldo netto del periodo e abbonati attivi |
| **Scadenze Mese** | elenco degli utenti in scadenza nel mese corrente, con data |
| **Report Agente** | selezione agente → periodo → **lo stesso report** che vede l'agente |
| **Report Masterclass** | selezione relatore → masterclass → periodo → vendite |
| **Profitti Masterclass** | selezione periodo → profitti globali con breakdown per relatore |

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

## Dettaglio: Salva Prelievo

Modale con **importo**, **metodo pagamento**, **wallet destinatario**, **hash transazione**,
**descrizione**. Il campo metodo accetta `CRYPTO`, `STRIPE_LILLO` o `STRIPE_DANNY`: per Stripe serve
a imputare il prelievo all'account giusto ([[Bilanciamento degli account Stripe]]).

⚠️ La verifica on-chain dell'hash viene eseguita **anche per i prelievi Stripe**: vedi [[Prelievo]]
per i dettagli delle validazioni.

## Dettaglio: i report per periodo

Le date si inseriscono come `gg/mm/aaaa` e sono validate: la data di inizio non può essere più
vecchia di **1 anno**, la data di fine non può essere nel **futuro**, e l'inizio non può superare la
fine. Vedi [[Reportistica]] per il significato dei numeri.

## Dettaglio: Report Agente

Serve a vedere **esattamente** ciò che vede l'agente con `!mieiref`: gli embed sono costruiti dalla
stessa funzione condivisa, così le due viste non possono divergere. Il percorso è
agente → periodo (mese corrente o precedente) → due embed, Stripe in EUR e crypto in USD.

## Cosa NON si può fare dal bot

Non esistono comandi per: creare o modificare [[Agente|agenti]], [[Relatore|relatori]],
[[Masterclass]], [[Utente lifetime]], voci del [[Catalogo servizi]] o parametri di
[[Tabella server_config]]. Tutte queste operazioni si fanno **a mano via SQL** sul database.

## Voci correlate
- [[Reportistica]]
- [[Comandi agenti]]
- [[Comandi relatori]]
- [[Prelievo]]
