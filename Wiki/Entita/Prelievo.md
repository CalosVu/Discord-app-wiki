---
tipo: entita
titolo: Prelievo
alias: [track_prelievi, TrackPrelievi, uscita, pagamenti_prelievi]
tag: [dominio/pagamenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-20
stato: stabile
---

# Prelievo

Un'uscita di denaro registrata da un admin: serve a tenere il **saldo** allineato a quanto è
realmente rimasto sui conti. Tabella `pagamenti_prelievi`, entità `TrackPrelievi`.

Dal 2026-08-20 si gestisce **interamente dal bot** — creazione, modifica, cambio di stato,
cancellazione — perché il prodotto andrà a clienti che non avranno accesso al database.

## Come si registra

`!Admin` → **📥 Prelievi** → *Nuovo*. Si sceglie il canale da un menu, non si digita:

```
🪙 Crypto · USDT     🪙 Crypto · USDC
💳 Stripe Primario · EUR     💳 Stripe Secondario · EUR
```

Poi si apre una finestra i cui campi **dipendono dalla scelta**:

| Campo | Crypto | Stripe |
|---|---|---|
| Importo | ✅ | ✅ |
| Data — vuoto = oggi | ✅ | ✅ |
| Wallet destinatario | ✅ | — |
| Hash — vuoto se non ancora eseguito | ✅ | — |
| Note | ✅ | ✅ |

> [!info] Perché metodo e valuta stanno nel menu e non nella finestra
> Discord ammette **cinque campi per finestra**, uno per riga. Chiedendo lì anche metodo e valuta
> ne servirebbero sette per il crypto. Scegliendoli prima ne restano cinque esatti — ed è anche il
> motivo per cui non si può più sbagliare a scrivere `STRIPE_PRIMARIO`.

Aggiungere una valuta significa aggiungere una voce a quel menu, senza toccare le finestre.

## Lo stato non si chiede: si deduce

| Situazione | Stato assegnato |
|---|---|
| Data futura, oppure crypto senza hash | `IN_ATTESA` |
| Tutto il resto | `COMPLETATO` |

È così che si registra **un movimento non ancora eseguito**: lo si annota oggi, resta fuori dai
saldi — le query di somma filtrano su `COMPLETATO` — e quando è fatto lo si porta a completato con
un bottone.

## Gestione: modificare, annullare, cancellare

`!Admin` → **📥 Prelievi** → *Ultimi 10* oppure *Cerca per periodo* (che accetta anche date future,
per ritrovare i movimenti programmati). Scelto un prelievo si apre la sua scheda con tre azioni:

| Azione | Cosa fa |
|---|---|
| ✏️ **Modifica** | riapre la finestra **già compilata**: si corregge una cifra, non si riscrive tutto |
| 🔁 **Stato** | i quattro stati dell'enum, incluso `FALLITO` |
| 🗑️ **Elimina** | cancella la riga, con conferma |

**Annullare o cancellare non sono la stessa cosa.** Portare a `FALLITO` toglie il movimento dai
saldi lasciandolo nello storico: è la scelta giusta per un prelievo che non è andato a buon fine.
L'eliminazione è definitiva e serve all'errore appena commesso — il messaggio di conferma lo dice.

Metodo e valuta non sono modificabili: cambiarli cambierebbe il senso del movimento, e la strada
pulita è eliminare e rifare.

## Cosa NON fa più: la verifica on-chain

Fino al 2026-08-20 il salvataggio chiamava `verifyAdminArbitrumTransaction`, che decodificava la
transazione e verificava il destinatario. È stata **tolta**: l'amministratore registra un movimento
che ha già fatto o che sta per fare, e il bot non ha titolo per rifiutarlo.

Quella verifica, unita a `transaction_hash NOT NULL`, rendeva i prelievi **Stripe impossibili**: un
bonifico non ha un hash Arbitrum, e bisognava riciclarne uno vero di un'altra transazione.

## Validazioni rimaste

1. **autorizzazione**: `discordService.isAdmin(...)` a ogni ingresso, menu compresi;
2. **importo** positivo e sotto 1.000.000, con la virgola accettata come separatore;
3. **formato** di hash e wallet, *se valorizzati*: `0x` + 64 e `0x` + 40 esadecimali;
4. **hash non già registrato**, per non contare due volte lo stesso movimento;
5. **valuta** fra `EUR`, `USDT`, `USDC`.

## Ogni operazione lascia traccia

Creazione, modifica, cambio di stato e cancellazione finiscono nel [[Log operativo]] con il tipo
`PRELIEVO`, l'amministratore che l'ha eseguita e — per le modifiche — **cosa è cambiato**
(«importo 100,00 → 150,00»). Chi amministra dal bot non vede il database: quella riga è l'unico
modo di ricostruire un errore.

## Campi

`importo`, `valuta`, `metodoPagamento`, `stripeAccount`, `transactionHash`, `walletDestinatario`,
`dataPrelievo`, `descrizione`, `note`, `stato`, `idDiscordAdmin`, `dataUpdate`.

> [!warning] `descrizione` e `note` convivono, e `transaction_hash` conteneva testo
> Nello storico scritto a mano le due colonne dicono cose diverse, quindi nessuna è stata unificata
> nell'altra. **Il form del bot compila solo `note`**; `descrizione` resta per lo storico.
>
> `transaction_hash` era `NOT NULL`, e dovendo scriverci qualcosa ci è finito del testo: su 47
> prelievi, **37 contenevano descrizioni** — `Ritiro` 25 volte, `Pagamento da saldo cc` 9,
> `Rimasto su Blofin` 3 — e solo due righe avevano hash veri. Una colonna obbligatoria non produce
> dati: produce riempitivi. La `V32` ha accodato quei testi alla descrizione (senza duplicarli
> dove già comparivano) e ha svuotato la colonna, che ora significa una cosa sola.

> [!caution] Manca il vincolo di unicità sull'hash
> Era previsto nella `V32` ma **due righe storiche condividono un hash vero** (id 24 e 25) e vanno
> decise a mano: potrebbero essere due voci contabili coperte da un solo trasferimento, oppure un
> doppione. Nel frattempo il duplicato è intercettato dal servizio prima del salvataggio, quindi
> dal bot non si può creare; resta possibile scrivendo direttamente a database.

## Voci correlate
- [[Pagamento]]
- [[Reportistica]]
- [[Comandi admin]]
- [[Log operativo]]
- [[Bilanciamento degli account Stripe]]
