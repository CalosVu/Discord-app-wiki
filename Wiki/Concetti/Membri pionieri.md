---
tipo: concetto
titolo: Membri pionieri
alias: [pioniere, membro_pioniere, PIONIERE]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Membri pionieri

I primi sostenitori del server, che pagano un prezzo agevolato a vita — finché non lasciano scadere
l'abbonamento. Flag `membro_pioniere` sull'[[Utente]].

## Il prezzo

| Piano | EUR | USD |
|---|---|---|
| `PIONIERE` | 30,00 | 35,00 |
| `BASIC` | 40,00 | 45,00 |

Vedi [[Catalogo servizi]] per il listino completo.

## Come si diventa pionieri

**Non automaticamente.** Ogni nuovo utente creato all'accettazione del disclaimer nasce con
`membroPioniere = false` e piano `BASIC`, esplicitamente. Il flag va messo **a mano** sul database.

Nei dati iniziali del repo, 73 utenti su 76 hanno il flag a `true`: sono i membri storici della
prima ondata.

## Il parametro `PIONIERI` non è usato

In [[Tabella server_config]] esiste la riga `PIONIERI = 50`, descritta come «numero utenti da
considerare come pionieri oltre 4 di staff». **Nessuna riga di codice la legge**: non esiste alcun
meccanismo che promuova automaticamente i primi N iscritti. È un residuo di un'idea non
implementata.

## Come si perde lo status

Il [[Batch verifica abbonamenti]], al momento del degrado (N giorni dopo la scadenza), esegue:

```java
utente.setMembroPioniere(false);
utente.setPianoApplicato(BASIC);
```

Il pioniere che lascia scadere l'abbonamento **perde il prezzo agevolato in modo definitivo**: non
esiste nessun codice che rimetta il flag a `true`. Solo un intervento manuale sul database può
ripristinarlo.

Vale la pena saperlo prima di rispondere a un utente che chiede perché il prezzo è aumentato dopo
una pausa.

## Effetto sulle promo

I pionieri sono **esclusi da tutte le [[Promozioni temporali]]**: `getPromoAttiva` ritorna subito
`Optional.empty()` se `membroPioniere` è `true`, perché hanno già un prezzo agevolato stabile.

## Voci correlate
- [[Catalogo servizi]]
- [[Utente]]
- [[Promozioni temporali]]
