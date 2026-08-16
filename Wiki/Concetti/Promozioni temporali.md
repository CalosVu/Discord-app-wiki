---
tipo: concetto
titolo: Promozioni temporali
alias: [promo, PROMO, promozione]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-16
stato: stabile
---

# Promozioni temporali

Un'offerta **a tempo** che sovrascrive prezzo e durata dell'[[Abbonamento Supporter Member]]. Vive
nella tabella `cfg_promo` ([[Catalogo servizi]]): se ne possono creare quante se ne vuole, ognuna con
la propria finestra di validità e il proprio pubblico.

Il nome è libero e non ha vincoli di unicità: la stessa riga si riusa negli anni cambiando date e
prezzi. Fino a `V23` le promo stavano nella tabella dei piani e si riconoscevano dalla stringa
`'PROMO'` nel nome — una convenzione che andava tenuta allineata fra la query di ricerca e quella
del batch, e che bastava violare per rendere una promo invisibile o eterna.

Esempio dai dati iniziali: 130 € / 149 USD per **4 mesi** (invece di 160 €), valida dal 31/03/2026
al 15/08/2026.

## Cosa si decide quando si crea una promo

| Campo | Cosa stabilisce |
|---|---|
| `data_inizio` / `data_fine` | **quanto dura**: fuori da questa finestra la promo non viene proposta a nessuno |
| `destinatari` | come tratta i [[Membri pionieri]]: `ESCLUDI_PIONIERI`, `INCLUDI_PIONIERI`, `SOLO_PIONIERI` |
| `rinnovo` | **chi può usarla**: `false` = solo chi non ha mai pagato; `true` = anche chi sta rinnovando |
| `referral` | se valorizzato, l'offerta vale **solo** per chi è entrato con quel codice invito |
| `ruolo_richiesto` | ruolo Discord necessario; `NULL` = nessun vincolo di ruolo |
| `prezzo_eur` / `prezzo_usd` | il **totale** del periodo, non il mensile |
| `numero_mesi` | i mesi coperti, che vengono **forzati**: l'utente non li sceglie |

Le date scritte qui sono `DATETIME` e valgono alla lettera. Erano `TIMESTAMP` fino a `V23`, e in
quella forma MySQL le convertiva secondo il fuso della connessione: su un server in UTC la finestra
poteva risultare spostata di un'ora rispetto a come era stata inserita.

## Le quattro condizioni di applicabilità

`PianoUtenteService.promoAttiva(utente)` ritorna una promo solo se **tutte** sono vere:

1. i `destinatari` della promo comprendono l'utente: `ESCLUDI_PIONIERI` (default) lo ammette solo se
   **non** ha diritto al prezzo pioniere, `SOLO_PIONIERI` solo se ce l'ha, `TUTTI` sempre
   ([[Membri pionieri]]). Attenzione: «avere diritto» include anche chi pioniere non è ancora ma lo
   diventerebbe pagando, perché ci sono posti liberi;
2. la promo ha `numeroMesi` valorizzato;
3. se l'utente sta **rinnovando** (`numeroRinnovi > 0`), la promo deve avere `rinnovo = true`. Con
   `rinnovo = false` l'offerta è riservata a chi non ha mai pagato;
4. se la promo ha un `referral`, l'utente deve essere entrato **con quello stesso** referral
   ([[Referral agent]]).

La query di partenza filtra già su `attivo = true` e `adesso` compreso fra `data_inizio` e
`data_fine`.

## Chi fa parte del pubblico

`ruolo_richiesto` e `destinatari` **non sono condizioni indipendenti** e si valutano insieme:

> Il **ruolo** definisce il pubblico. `destinatari` decide soltanto dei **pionieri che quel pubblico
> non comprende già**.

| `destinatari` | senza `ruolo_richiesto` | con `ruolo_richiesto = Studente` |
|---|---|---|
| `ESCLUDI_PIONIERI` *(default)* | tutti tranne i pionieri | tutti gli studenti, **anche se pionieri** |
| `INCLUDI_PIONIERI` | chiunque | studenti **e** pionieri, anche non studenti |
| `SOLO_PIONIERI` | solo i pionieri | studenti **e** pionieri |

Due conseguenze da tenere a mente:

- **con un ruolo richiesto, `ESCLUDI_PIONIERI` non esclude nessuno.** Va letto come «non aggiungere
  i pionieri», non come «togliere i pionieri»: il ruolo comanda, e uno studente pioniere entra come
  ogni altro studente. La sottrazione avviene solo quando non c'è un ruolo, perché lì il pubblico
  sarebbe altrimenti tutti;
- **con un ruolo richiesto, `SOLO_PIONIERI` e `INCLUDI_PIONIERI` coincidono.** È voluto: la
  differenza fra «aggiungi i pionieri» e «solo i pionieri» ha senso solo quando non esiste un altro
  pubblico da cui distinguerli.

## Precedenza fra più promo

Se più promo risultano valide contemporaneamente, vince quella **specifica per referral** sulla
generica:

```java
.min(Comparator.comparingInt(p -> p.getReferral() == null ? 1 : 0))
```

Fra due promo generiche o due promo con lo stesso referral, la scelta è **non deterministica**
(dipende dall'ordine restituito dal database). Conviene evitare sovrapposizioni.

## La promo vince sempre sul piano

Quando una promo è applicabile **sovrascrive il piano**, anche se costa di più. Le due cose
rispondono a domande diverse: il piano è quanto si paga a ogni rinnovo, la promo è un'offerta
circoscritta nel tempo.

Non c'è quindi alcun confronto di prezzo fra promo e piano — quello esiste solo *fra piani*
([[Catalogo servizi]]). Se i pionieri devono restare sul loro prezzo agevolato, la scelta si fa a
monte con `ESCLUDI_PIONIERI`: ammetterli e poi applicare il minore sarebbe la stessa decisione presa
due volte.

## Effetto sul flusso di pagamento

| Canale | Effetto |
|---|---|
| **Stripe** | il campo "numero mesi" della modale **non viene mostrato**: mesi e prezzo totale arrivano dalla promo. Se la modale è già aperta, il valore inserito viene comunque ignorato |
| **Crypto** | il prezzo totale viene **diviso** per il numero di mesi, perché la verifica on-chain moltiplica poi per i mesi; `nMesi` viene forzato al valore della promo |

Gli embed mostrano un blocco «🔥 PROMO IN CORSO!» con data di fine e mesi coperti.

## La duplicazione è stata rimossa

`getPromoAttiva` era **replicato identico in tre classi** — `CommandBot`,
`OnButtonInteractionListener`, `CryptoPaymentService` — e accanto a lui la scelta del piano era
addirittura *divergente*: il ramo Stripe leggeva `utente.pianoApplicato`, quello crypto
`utente.membroPioniere`. Bastava che i due campi non concordassero, ed è successo, perché lo stesso
utente pagasse due prezzi diversi a seconda del canale.

Oggi la decisione sta tutta in `PianoUtenteService` ([[Membri pionieri]]).

## Disattivazione automatica

Il [[Batch verifica abbonamenti]], a ogni esecuzione, cerca le promo con `data_fine` passata e le
porta ad `attivo = false`. La promo scade quindi da sola, ma solo dopo il primo giro del batch
successivo alla scadenza.

La selezione ora la fa il database (`findAllByAttivoTrueAndDataFineBefore`). Prima il batch cercava
`nome_servizio = 'PROMO'` con un confronto esatto: una promo rinominata sarebbe rimasta **attiva per
sempre**, perché nessuno l'avrebbe più trovata per disattivarla.

## Voci correlate
- [[Catalogo servizi]]
- [[Membri pionieri]]
- [[Abbonamento Supporter Member]]
