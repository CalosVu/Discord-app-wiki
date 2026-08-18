---
tipo: concetto
titolo: Blocco dei pagamenti
alias: [flag pagamenti, pagamenti sospesi]
tag: [dominio/pagamenti, dominio/configurazione]
fonti: [Codice Discord-access-app, Piano sviluppo doppio Stripe]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Blocco dei pagamenti

Tre interruttori in [[Tabella cfg_server]] che permettono di **sospendere a runtime** un tipo di
incasso, senza deploy e senza riavvio.

## I tre flag

| Flag | Blocca | Discriminante |
|---|---|---|
| `PAGAMENTI_NUOVE_ISCRIZIONI_ABILITATE` | il **primo** Supporter Member | `dataPrimaIscrizione == null` |
| `PAGAMENTI_RINNOVI_ABILITATI` | i **rinnovi** Supporter Member | `dataPrimaIscrizione != null` |
| `DONAZIONI_LIBERE_ABILITATE` | il [[Sostegno libero]] | — |

Le tre righe sono **obbligatorie**: non si cancellano e l'applicazione non parte se mancano
([[Tabella cfg_server]]). Fino ad agosto 2026 il codice ripiegava su `true`, quindi una riga mancante
apriva i pagamenti in silenzio — ora quel caso non esiste.

## Cross-canale per scelta

Ogni flag agisce **sia su Stripe sia su crypto**: nasconde il pulsante corrispondente in entrambi i
flussi, impedisce la generazione del link Stripe e impedisce la verifica della transazione crypto.
È stata una decisione esplicita — un solo flag per tipo di operazione, nessuno sdoppiamento per
canale (fonte: [[Piano sviluppo doppio Stripe]] Fase 1).

## Difesa su tre livelli

1. **Rendering** — i pulsanti vengono costruiti includendo solo le opzioni consentite. Se non ne
   resta nessuna, l'utente riceve direttamente il messaggio di sospensione. Il controllo a monte
   (`isAlmenoUnPagamentoAbilitato`) evita persino di far scegliere fra Crypto e Stripe.
2. **Handler** — `pagamentoConsentito` ricontrolla il flag al click. Serve contro i **pulsanti
   vecchi**: i messaggi Discord restano cliccabili per sempre, anche mesi dopo.
3. **Webhook (guardia soft)** — se un pagamento arriva mentre il suo tipo è disabilitato (link
   generato prima della chiusura e pagato entro la validità), il pagamento viene **comunque
   processato** e il ruolo assegnato, ma la notifica agli admin è preceduta da:

   > ⚠️ ATTENZIONE: pagamento ricevuto mentre questo tipo di pagamento era DISABILITATO
   > (link generato prima della chiusura). Ruolo assegnato comunque.

   La scelta è deliberata: chi ha pagato in buona fede non deve restare senza accesso.

## Come si usa in pratica

```sql
UPDATE server_config SET valore_configurazione = 'false'
 WHERE nome_configurazione = 'PAGAMENTI_NUOVE_ISCRIZIONI_ABILITATE';
```

Effetto **immediato** (nessuna cache, vedi [[Configurazione di server]]). Per riaprire, `'true'`.

⚠️ Non cancellare la riga per bloccare: senza riga vale il default `true`.

## Voci correlate
- [[Tabella cfg_server]]
- [[Pagamenti Stripe]]
- [[Pagamenti crypto Arbitrum]]
