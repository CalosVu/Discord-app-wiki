---
tipo: fonte
titolo: Integrazione sistema pagamenti
alias: [IntegrazioneSistemaPagamenti]
tag: [fonte/documento]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: obsoleto
---

# Integrazione sistema pagamenti

Specifica tecnica iniziale del sistema di abbonamenti e verifica crypto. **Fonte di rango 5**:
l'impianto concettuale è sopravvissuto, i dettagli tecnici no.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/IntegrazioneSistemaPagamenti.md`
- **Data:** giugno 2025
- **Titolo interno:** «Specifica tecnica — Integrazione sistema di gestione abbonamenti e verifica
  crypto per bot Discord»

## Cosa è sopravvissuto nel codice

- L'**impianto dello scheduler giornaliero** che controlla le scadenze, avvisa e degrada il ruolo:
  realizzato in [[Batch verifica abbonamenti]] (con parametri diversi, vedi sotto).
- Il **calcolo della scadenza** distinto tra prima iscrizione e rinnovo, con
  `durata_giorni_abbonamento` letta dal catalogo: vedi [[Abbonamento Supporter Member]].
- La **prevenzione dello spam sui tentativi di verifica**, con salvataggio in
  `user_verify_transaction`: vedi [[Tentativo di verifica transazione]].
- Le tabelle `users`, `payments`, `catalogo_servizi`, `user_verify_transaction` esistono ancora,
  seppure con campi diversi ([[Schema del database]]).

## ⚠️ Claim superate dal codice

| Claim del documento | Realtà nel codice |
|---|---|
| Blockchain **Solana**, verifica via **Solscan API**, importi in SOL/lamport | La rete è **Arbitrum One**, i token **USDT/USDC** (ERC-20, 6 decimali), la verifica è via **Web3j** su nodo RPC. Vedi [[Pagamenti crypto Arbitrum]] |
| Comandi `!iscrizione` e `!verifica_iscrizione` | I comandi reali sono `!Donazione` e `!verifica-transazione` ([[Comandi utente]]) |
| Scheduler **alle 04:00** | Cron reale `0 0 22 * * *` — le 22:00 UTC, corrispondenti alla mezzanotte italiana ([[Batch verifica abbonamenti]]) |
| Rinnovo entro **5 giorni**, poi degrado | Il ritardo tollerato è configurabile: `N_GIORNI_DOPO_SCADENZA`, oggi **3** ([[Tabella server_config]]) |
| Massimo **3 tentativi ogni 24h** | Finestra e numero sono configurabili: `N_TENTATIVI_VERIFICA` = 3 in `TEMPO_LIMITE_VERIFICA` = 2 ore |
| L'importo deve corrispondere **esattamente** | Il codice accetta importi **maggiori o uguali** all'atteso (sovra-pagamento ammesso) |
| Campo `numero_tentativi` in `user_verify_transaction` | Non esiste: i tentativi si contano con una query sulla finestra temporale |
| Tabella `tracking_user`, campo `email` su `users` | Non esistono |

## Come usarlo

Utile per capire **l'intento originale** delle regole di abbonamento (perché esistono la finestra
tentativi, il degrado ritardato, la distinzione prima-iscrizione/rinnovo). I valori e le tecnologie
vanno sempre riletti dal [[Codice Discord-access-app]].

## Voci correlate
- [[Fonti]]
- [[DOC_PROGETTO]]
