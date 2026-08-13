---
tipo: modulo
titolo: Pagamenti crypto Arbitrum
alias: [crypto, USDT, USDC, Web3j, Arbitrum]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Integrazione sistema pagamenti]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Pagamenti crypto Arbitrum

Il canale di pagamento in criptovaluta: l'utente invia **USDT o USDC su Arbitrum One** al wallet del
progetto, poi comunica l'hash della transazione al bot, che la verifica **on-chain** con Web3j.

Non c'è nessun gateway: il sistema legge direttamente la blockchain tramite un nodo RPC
(`WEB3J_CLIENT_ADDRESS`).

## I due token accettati

| Token | Contratto su Arbitrum One |
|---|---|
| USDT | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` |
| USDC (nativo Circle) | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |

Entrambi con **6 decimali** (non 18 come ETH): è il moltiplicatore usato nel confronto degli importi.

## La sequenza di verifica

**Controlli formali** (prima di toccare la blockchain):

1. formato dell'hash: `0x` + 64 esadecimali;
2. numero di mesi fra 1 e 24;
3. **rate limiting** su [[Tentativo di verifica transazione]];
4. hash non già presente in `pagamenti` (`tx_hash` è `UNIQUE`).

**Verifica on-chain:**

5. la transazione e la sua receipt esistono, e lo stato è OK;
6. si estrae il trasferimento ERC-20 con **due strategie**:
   - **diretta** — il campo `to` punta al contratto USDT/USDC: si decodifica l'input data;
   - **fallback dai log** — il `to` è un contratto intermediario (prelievo da exchange, smart
     contract wallet): si scorrono i log cercando l'evento `Transfer` emesso dal contratto
     USDT/USDC verso il wallet del progetto;
7. il destinatario deve coincidere con `ARBITRUM_WALLET_ADDRESS`;
8. l'importo deve essere **maggiore o uguale** a `prezzo × mesi` — il sovra-pagamento è ammesso;
9. si salva il [[Pagamento]] con `dataPagamento` = **timestamp del blocco**, non l'ora corrente.

Il fallback dai log è ciò che rende accettabili i prelievi diretti da exchange, che altrimenti
fallirebbero tutti.

## Il prezzo applicato

Riletto dal [[Catalogo servizi]] in base a `membroPioniere`: `PIONIERE.prezzoUsd` oppure
`BASIC.prezzoUsd`. Se c'è una promo attiva, il prezzo totale viene **diviso** per i mesi della promo
(perché la verifica moltiplica poi per i mesi) e i mesi sono forzati a quelli della promo
([[Promozioni temporali]]).

## Verifica dei prelievi admin

Lo stesso servizio espone `verifyAdminArbitrumTransaction`, usato quando un admin registra un
[[Prelievo]]: decodifica l'input della transazione e controlla che il destinatario sia quello
dichiarato.

## ⚠️ Il controllo anti-anticipo non è attivo

Esiste un metodo `isValidForUser` che rifiuterebbe le transazioni **antecedenti** alla scadenza
corrente («Donazione anticipata. Contattare un amministratore»). **Non viene mai chiamato**: il
rinnovo anticipato è quindi permesso, e i giorni si sommano
([[Abbonamento Supporter Member]]).

## Storia / claim superate

> [!warning] Sostituito da fonte più attendibile
> [[Integrazione sistema pagamenti]] specificava **Solana**, verifica via **Solscan API** e importi
> in lamport, con corrispondenza **esatta** dell'importo. Il codice usa **Arbitrum One**,
> USDT/USDC via **Web3j**, e accetta importi **maggiori o uguali**. **Vale il codice.**

## Voci correlate
- [[Pagamento]]
- [[Tentativo di verifica transazione]]
- [[Comandi utente]]
