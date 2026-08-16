---
tipo: entita
titolo: Catalogo servizi
alias: [cfg_piani, cfg_promo, Piano, piani, listino]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-16
stato: stabile
---

# Catalogo servizi

Il listino sta in **due tabelle**: `cfg_piani` per i piani stabili, `cfg_promo` per le offerte a
tempo ([[Promozioni temporali]]).

Fino a `V23` erano una sola, `cfg_catalogo_servizi`, dove una riga `PROMO` conviveva con le righe
`BASIC` e `PIONIERE`. Su dodici colonne metà valevano solo per un tipo di riga, e su una riga
`PIONIERE` un campo come `destinatari` non significava nulla.

## I piani — `cfg_piani`

| Piano | EUR/mese | USD/mese | Durata |
|---|---|---|---|
| `BASIC` | 40,00 | 45,00 | 30 giorni per mese pagato |
| `PIONIERE` | 30,00 | 35,00 | 30 giorni per mese pagato |

`prezzo_eur` è usato dal canale Stripe, `prezzo_usd` dal canale crypto: sono **due listini
distinti**, non una conversione.

| Campo | Note |
|---|---|
| `nome` | `UNIQUE`. `BASIC` e `PIONIERE` sono nomi riservati, cercati dal codice |
| `descrizione` | testo libero per chi legge la tabella; il codice non lo usa |
| `prezzo_eur` / `prezzo_usd` | prezzo **mensile** |
| `durata_giorni_abbonamento` | giorni aggiunti alla scadenza per ogni mese pagato |
| `ruolo_richiesto` | ruolo Discord necessario per usare il piano; `NULL` = vale per tutti |
| `attivo` | solo i piani attivi vengono proposti |

### Perché il nome è `UNIQUE`

Il codice cerca i piani per nome e si aspetta **una riga sola**: `findByNome` restituisce un
`Optional`, e con due righe Spring Data non ne sceglie una — solleva un'eccezione.

Prima della separazione il vincolo non era applicabile, perché le righe `PROMO` dovevano poter
essere più d'una nella stessa tabella. Bastava quindi inserire un secondo `BASIC` attivo — per
provare un prezzo, o per copia-incolla — e **ogni pagamento sarebbe fallito**, su entrambi i canali,
con un errore che parlava di «result size» senza dire dove guardare. Che lo scenario fosse
realistico lo dimostravano le due righe `PROMO` quasi identiche già a database.

## Le promo — `cfg_promo`

Nome libero, nessun vincolo: la stessa riga si riusa negli anni cambiando date e prezzi. Struttura e
condizioni di applicabilità in [[Promozioni temporali]].

## Come viene scelto il prezzo

Da un punto solo, `PianoUtenteService`, per **entrambi** i canali:

1. se esiste una promo valida per l'utente, **sovrascrive** prezzo e numero di mesi;
2. altrimenti chi ha diritto al prezzo pioniere prende `PIONIERE` ([[Membri pionieri]]);
3. altrimenti si guarda fra i piani utilizzabili — quelli senza ruolo richiesto, più quelli il cui
   ruolo l'utente possiede — e **vince il più conveniente**, confrontando il prezzo in euro.

`utenti.piano_applicato` **non decide il prezzo**: registra il piano in vigore, e viene riscritto
quando l'utente ottiene il posto pioniere o quando il batch lo degrada.

Da `V23` la sua chiave esterna punta ai soli piani. Prima la tabella conteneva anche le promo, e
assegnarne una come piano applicato avrebbe prodotto un abbonamento di **zero giorni**, perché sulle
promo `durata_giorni_abbonamento` valeva `0`.

## `ruolo_richiesto`: cosa metterci e cosa no

Se valorizzato, il piano o la promo valgono **solo** per chi possiede quel ruolo su Discord. Se è
`NULL` valgono per tutti, ed è il caso di `BASIC` e `PIONIERE`.

> ⚠️ **Non vanno messi qui i ruoli del ciclo di vita** — new entry, abbonato, donazione. Cambiano
> proprio quando l'utente paga: scrivendo il ruolo di new entry su `BASIC`, quel piano diventerebbe
> irraggiungibile al primo rinnovo; scrivendoci quello dell'abbonato, irraggiungibile al primo
> acquisto. Nessuno dei due valori funziona.
>
> La colonna serve per **appartenenze stabili** — `STUDENTE`, `PARTNER` — che l'utente ha o non ha
> indipendentemente dall'abbonamento.

`PIONIERE` non si sceglie per ruolo ma per il flag `membro_pioniere` sull'utente, ed è escluso dal
confronto sui prezzi: altrimenti, costando meno di `BASIC`, vincerebbe sempre.

### Discord viene interrogato solo se serve

Sapere i ruoli di un utente richiede una chiamata di rete a Discord. Finché **nessuna** riga
valorizza `ruolo_richiesto` — la situazione attuale — quella chiamata non parte affatto e il prezzo
si calcola solo dal database, come è sempre stato.

Quando invece serve e **fallisce** (Discord irraggiungibile, utente uscito dal server), il prezzo
non viene indovinato: l'utente riceve un invito a riprovare. Un prezzo scelto d'ufficio sarebbe
troppo alto per chi aveva diritto a un'agevolazione, o troppo basso per gli altri.

## Trappola risolta: c'erano due sorgenti per lo stesso prezzo

Fino ad agosto 2026 Stripe leggeva `pianoApplicato` e crypto rileggeva il catalogo da
`membroPioniere`. Su due utenti reali i campi divergevano — pionieri con piano `BASIC` — e quei due
pagavano **35 USD in crypto e 40 € con Stripe**. Le loro righe non sono state corrette per scelta:
la regola nuova vale da qui in avanti, e con la sorgente unica il caso non si ripresenta.

## Voci correlate
- [[Promozioni temporali]]
- [[Membri pionieri]]
- [[Abbonamento Supporter Member]]
