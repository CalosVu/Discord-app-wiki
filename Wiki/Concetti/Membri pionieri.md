---
tipo: concetto
titolo: Membri pionieri
alias: [pioniere, membro_pioniere, PIONIERE, posti pioniere]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-16
stato: stabile
---

# Membri pionieri

I primi sostenitori del server, che pagano un prezzo agevolato. I posti sono **a numero chiuso** e
non tornano mai disponibili: chi entra dal principio è premiato, e quando i posti finiscono il
gruppo può soltanto assottigliarsi.

## Il prezzo

| Piano | EUR | USD |
|---|---|---|
| `PIONIERE` | 30,00 | 35,00 |
| `BASIC` | 40,00 | 45,00 |

Vedi [[Catalogo servizi]] per il listino completo.

## Come si diventa pionieri

**Al primo pagamento andato a buon fine**, se restano posti liberi — non all'ingresso nel server e
non alla generazione del link di pagamento. Il posto lo occupa chi ha pagato davvero.

Ogni nuovo utente nasce con `membroPioniere = false` e piano `BASIC`; il posto glielo assegna
`PianoUtenteService.assegnaPostoPioniereSePossibile`, chiamato da `savePaymentAndUpdateUser`, che è
il punto attraversato da **tutti** i pagamenti, crypto e Stripe.

Resta possibile assegnare il flag a mano sul database — è così che si marca lo staff, che per
decisione esplicita **non occupa posti**.

## I due campi, e perché non ne basta uno

| Campo | Significato | Chi lo azzera |
|---|---|---|
| `utenti.membro_pioniere` | gode del prezzo pioniere **adesso** | il [[Batch verifica abbonamenti]] alla scadenza |
| `utenti.pioniere_storico` | ha consumato un posto, **per sempre** | nessuno |

Con il solo `membro_pioniere` la regola non si esprime: renderlo permanente farebbe pagare il prezzo
agevolato anche all'ex pioniere rientrato a tetto pieno, che invece deve pagare pieno.

## Le tre chiavi di configurazione

| Chiave di [[Tabella cfg_server]] | Cosa contiene |
|---|---|
| `PIONIERI_ABILITATI` | interruttore generale del meccanismo |
| `PIONIERI` | il tetto dei posti |
| `PIONIERI_ASSEGNATI` | i posti consumati finora |

Con `PIONIERI_ABILITATI` a `false` il concetto di pioniere sparisce: **tutti pagano `BASIC`**, anche
chi ha il flag, nessun posto viene più assegnato e le promo valgono per chiunque. Non si cancella
nulla — flag sugli utenti e contatore restano dove sono — quindi riaccendendolo si riparte
esattamente da dove si era rimasti.

> Il default in codice, se la chiave manca, è **spento**. È la scelta prudente sul lato del denaro:
> una configurazione persa non deve regalare sconti a nessuno.

Il contatore **non si decrementa mai**, nemmeno quando un pioniere scade. Non è un `COUNT` sul flag
di proposito: deve contare le sole assegnazioni fatte dal codice al pagamento, così chi viene
marcato a mano (lo staff) non consuma posti.

> ⚠️ Se assegni un posto a mano a un utente vero, **incrementa anche `PIONIERI_ASSEGNATI`**: il
> codice non se ne accorge e il conteggio si disallinea.

## Le quattro situazioni

| Chi paga | Posti liberi | Esito |
|---|---|---|
| pioniere con abbonamento attivo | irrilevante | prezzo `PIONIERE` |
| nuovo utente | sì | `PIONIERE`, consuma un posto |
| ex pioniere che rientra | sì | `PIONIERE`, **senza** consumare un nuovo posto: il suo era già contato |
| chiunque | no | `BASIC` |

## Come si perde lo status (ma non il posto)

Il [[Batch verifica abbonamenti]], al degrado, azzera `membro_pioniere` e riporta il piano a
`BASIC`. Il **posto resta consumato**: `pioniere_storico` non viene toccato e il contatore non
scende.

Chi rientra quando ci sono ancora posti liberi ritrova il prezzo agevolato senza intaccare il
contatore.

**Chi esce a tetto già pieno ha perso lo status per sempre**: al rientro paga `BASIC` come chiunque
altro, e nessun automatismo glielo restituisce. È la conseguenza voluta del numero chiuso — dopo il
cinquantesimo posto il gruppo non si ricostituisce.

L'unica cosa che riaprirebbe la porta è alzare `PIONIERI` sopra i posti consumati: si liberano posti
e chi rientra li trova, senza consumarne uno nuovo perché il suo era già contato. Vale la pena
saperlo prima di ritoccare il tetto.

## Effetto sulle promo

Lo decide la singola promo, con `cfg_promo.destinatari`, **letto insieme a `ruolo_richiesto`**:

| Valore | senza ruolo richiesto | con un ruolo richiesto |
|---|---|---|
| `ESCLUDI_PIONIERI` | **default**: non la vedono | la vedono, se hanno il ruolo |
| `INCLUDI_PIONIERI` | la vedono come tutti | la vedono, anche senza il ruolo |
| `SOLO_PIONIERI` | è riservata a loro | la vedono, anche senza il ruolo |

Quando una promo li ammette, i pionieri la ricevono **anche se costa più del loro prezzo agevolato**:
non c'è confronto fra promo e piano. La scelta si fa a monte, ammettendoli o no.

Il criterio è **avere diritto al prezzo pioniere**, non il flag `membro_pioniere`: comprende quindi
anche il nuovo utente che occuperebbe un posto libero pagando. Altrimenti gli si mostrerebbe la
promo e poi gli si assegnerebbe il posto a un prezzo diverso da quello pagato.

Vedi [[Promozioni temporali]] per le altre condizioni di applicabilità.

## La corsa sul traguardo

Il prezzo si mostra prima del pagamento. Se restano due posti e quattro persone aprono il link
insieme, tutte vedono il prezzo pioniere e tutte lo pagano: **prendono il posto comunque**, e il
tetto sfora di un'unità o due. È la scelta deliberata — nessuno paga un prezzo e ne riceve un
altro — ed è anche il motivo per cui l'incremento del contatore non è atomico.

## Voci correlate
- [[Catalogo servizi]]
- [[Utente]]
- [[Promozioni temporali]]
- [[Batch verifica abbonamenti]]
