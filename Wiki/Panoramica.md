---
tipo: hub
titolo: Panoramica
alias: [VuPass, Discord-access-app]
tag: [progetto/panoramica]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-31
stato: stabile
---

# Panoramica — VuPass

Sintesi di alto livello del prodotto e mappa della wiki.

## Di cosa si tratta

**VuPass** è il prodotto che gestisce gli accessi a pagamento a una community Discord: applicazione
Java 21 / Spring Boot 3.2.3 con bot JDA 5.5.1. Fa parte della famiglia **VuTradingFarm**, insieme a
*VuTracker* (portfolio) e *VuMarkets* (produzione e pubblicazione di contenuti social).

Il bot parla con gli utenti in messaggio privato: verifica l'accettazione del disclaimer, incassa
abbonamenti *Supporter Member* via **Stripe** (due account bilanciati) e **crypto USDT/USDC su
Arbitrum**, assegna e revoca i [[Ruoli Discord]], traccia referral e commissioni agenti, vende
**masterclass video** dei relatori (Cloudflare R2 + Stripe) ed espone un endpoint REST con cui
*VuTracker* verifica se un utente ha un abbonamento attivo.

> **Prodotto e istanza sono due cose diverse.** VuPass è il software; **InWestors** è la community
> Discord che ne ospita la prima istanza in produzione. Nei messaggi rivolti agli utenti compare il
> nome della community, non quello del prodotto.
> Il repository si chiama tuttora `Discord-access-app`.

## Le quattro platee

Il sistema serve quattro tipi di interlocutore, ognuno con i propri comandi in DM al bot:

| Platea | Cosa fa | Pagina |
|---|---|---|
| **Utente** | accetta il disclaimer, dona/si abbona, verifica la transazione, compra masterclass | [[Comandi utente]] |
| **Admin** | report finanziari, prelievi, scadenze, fix referral, report masterclass | [[Comandi admin]] |
| **Agente** | consulta le proprie commissioni sui referiti | [[Comandi agenti]] |
| **Relatore** | consulta le vendite delle proprie masterclass | [[Comandi relatori]] |

Il riconoscimento della platea non è uniforme: l'admin è chi ha il **ruolo Discord** admin sulla
guild, mentre agente e relatore sono chi risulta censito nelle tabelle `agenti` e `relatori`
(fonte: codice `DiscordService.isAdmin`, `AgentiService.findByDiscordId`,
`RelatoreRepository.findByDiscordId`).

## I due modelli di ricavo

1. **Abbonamento al server** — [[Abbonamento Supporter Member]] (a pagamento ricorrente manuale) e
   [[Sostegno libero]] (donazione una-tantum con badge). Due canali di pagamento in parallelo:
   [[Pagamenti Stripe]] e [[Pagamenti crypto Arbitrum]].
2. **Vendita di contenuti** — il [[Sistema masterclass]]: video ospitati su [[Storage R2]] e venduti
   per conto dei [[Relatore|relatori]], erogati via link firmato a scadenza.

## Come è organizzata la wiki

Vedi [[index]] per il catalogo completo. Le categorie principali:

- **Entita/** — gli oggetti del dominio e le tabelle che li rappresentano ([[Entita]]).
- **Concetti/** — i meccanismi trasversali: ruoli, promo, commissioni, idempotenza ([[Concetti]]).
- **Moduli/** — i flussi e le aree funzionali: bot, pagamenti, batch, deploy ([[Moduli]]).
- **Tassonomie/** — gli elenchi codificati: [[Tabella server_config]], [[Enum di dominio]],
  [[Endpoint REST]], [[Schema del database]] ([[Tassonomie]]).
- **Config-Credenziali/** — riferimenti a configurazioni e segreti, mai i valori
  ([[Config-Credenziali]]).
- **Interventi/** — il tracciamento dei lavori sul codice ([[Interventi]]).
- **Fonti/** — la provenienza di ogni contenuto e la gerarchia di attendibilità ([[Fonti]]).

Le convenzioni sono descritte in `CLAUDE.md`; la cronologia del manutentore è in `meta/log.md`.

## Voci correlate
- [[index]]
- [[Architettura dei moduli Maven]]
- [[Deploy e CI-CD]]
