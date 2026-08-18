---
tipo: modulo
titolo: Pagamenti crypto Arbitrum
alias: [crypto, USDT, USDC, Web3j, Arbitrum]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app, Integrazione sistema pagamenti]
creato: 2026-07-25
aggiornato: 2026-08-17
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
6. **la transazione è recente**: il timestamp del blocco deve stare entro
   `VERIFICA_CRYPTO_FINESTRA_ORE` ore ([[Tabella cfg_server]]), oggi **24**. Vedi sotto — è l'unica
   difesa contro il riscatto di trasferimenti storici;
7. si estrae il trasferimento ERC-20 con **due strategie**:
   - **diretta** — il campo `to` punta al contratto USDT/USDC: si decodifica l'input data;
   - **fallback dai log** — il `to` è un contratto intermediario (prelievo da exchange, smart
     contract wallet): si scorrono i log cercando l'evento `Transfer` emesso dal contratto
     USDT/USDC verso il wallet del progetto;
8. il destinatario deve coincidere con `ARBITRUM_WALLET_ADDRESS`;
9. l'importo deve essere **maggiore o uguale** a `prezzo × mesi` — il sovra-pagamento è ammesso;
10. si salva il [[Pagamento]] con `dataPagamento` = **timestamp del blocco**, non l'ora corrente.

Il fallback dai log è ciò che rende accettabili i prelievi diretti da exchange, che altrimenti
fallirebbero tutti.

## ⏱️ La finestra temporale, e perché non si valida il mittente

**Il problema.** Per ottenere l'abbonamento basta conoscere l'**hash** di un trasferimento verso il
wallet del progetto, di importo sufficiente e non ancora registrato. Il mittente on-chain viene
letto e salvato in `pagamenti.wallet_mittente` ma **non è confrontato con l'utente**: nulla lega la
transazione a chi la sottomette. E i trasferimenti su Arbitrum sono pubblici, con il wallet mostrato
a ogni utente da `!Donazione`.

**Perché il mittente non è verificabile.** Sarebbe la difesa più solida, ed è stata tentata in
passato. Non funziona: chi paga **da un exchange** non controlla l'indirizzo da cui parte la
transazione. Dentro l'exchange il wallet USDT/USDC dell'utente è interno alla piattaforma, non un
indirizzo di catena; il trasferimento parte dal wallet dell'exchange. L'utente dichiarerebbe quindi
un indirizzo che nella transazione non compare, e ogni pagamento da exchange verrebbe rifiutato.

**La difesa adottata: 24 ore.** Chiude completamente il **riscatto storico** — senza vincolo
temporale qualunque trasferimento passato mai passato dal bot resta valido per sempre: pagamenti
anteriori al sistema, movimenti operativi, rimborsi.

**Perché 24 e non 2.** Misurato sugli 82 pagamenti crypto reali:

| Ritardo fra pagamento e verifica | Pagamenti |
|---|---|
| entro 30 minuti | 76 (92,7%) |
| 30 min – 2h | 2 |
| 2h – 2h30 | 1 |
| 2h30 – 6h | 1 |
| 6h – 24h | 2 |

Una soglia a 2h30 avrebbe rifiutato **3 pagamenti veri su 82**. E la differenza di sicurezza fra
2h30 e 24h è trascurabile, perché in entrambi i casi resta aperta la corsa (vedi sotto): la scelta
riguarda solo quanti utenti legittimi bloccare, a parità di protezione.

**Cosa resta scoperto: la corsa.** Chi monitora il wallet vede il trasferimento in pochi secondi e
può inviare l'hash **prima** di chi ha pagato — la vittima, quando arriva, legge «transazione già
verificata». La finestra non lo impedisce, e senza validazione del mittente non è chiudibile in
codice. La risposta è amministrativa: la vittima contatta un admin, che verifica a mano.

Il rate limiting non protegge da questo: serve **un solo** tentativo, e quello riuscito non viene
contato.

**Configurazione.** `VERIFICA_CRYPTO_FINESTRA_ORE`; `0` disattiva il controllo, ed è anche il valore
di ripiego se la chiave manca o non è un numero — rifiutare pagamenti veri per una riga mancante
sarebbe peggio del rischio che si riapre. Il rifiuto è loggato con `WARN`, quindi la soglia si
calibra guardando i log.

Agli utenti l'embed di pagamento consiglia di verificare **entro 2 ore**: orienta il comportamento
senza essere il limite tecnico.

## Il prezzo applicato

Riletto dal [[Catalogo servizi]] in base a `membroPioniere`: `PIONIERE.prezzoUsd` oppure
`BASIC.prezzoUsd`. Se c'è una promo attiva, il prezzo totale viene **diviso** per i mesi della promo
(perché la verifica moltiplica poi per i mesi) e i mesi sono forzati a quelli della promo
([[Promozioni temporali]]).

## Verifica dei prelievi admin

Lo stesso servizio espone `verifyAdminArbitrumTransaction`, usato quando un admin registra un
[[Prelievo]]: decodifica l'input della transazione e controlla che il destinatario sia quello
dichiarato.

## Il controllo anti-anticipo resta spento, di proposito

Esiste un metodo `isValidForUser` che rifiuterebbe le transazioni **antecedenti** alla scadenza
corrente («Donazione anticipata. Contattare un amministratore»). **Non viene mai chiamato, ed è una
scelta**: il rinnovo anticipato è permesso e i giorni si sommano a quelli residui
([[Abbonamento Supporter Member]]). Accenderlo rifiuterebbe chi rinnova prima della scadenza, che è
un comportamento legittimo e frequente.

Da non confondere con il vincolo temporale di sicurezza, che è un'altra cosa e **è attivo**: vedi la
finestra di 24 ore qui sopra.

## Storia / claim superate

> [!warning] Sostituito da fonte più attendibile
> [[Integrazione sistema pagamenti]] specificava **Solana**, verifica via **Solscan API** e importi
> in lamport, con corrispondenza **esatta** dell'importo. Il codice usa **Arbitrum One**,
> USDT/USDC via **Web3j**, e accetta importi **maggiori o uguali**. **Vale il codice.**

## Voci correlate
- [[Pagamento]]
- [[Tentativo di verifica transazione]]
- [[Comandi utente]]
