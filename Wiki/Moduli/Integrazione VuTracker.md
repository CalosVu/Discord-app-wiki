---
tipo: modulo
titolo: Integrazione VuTracker
alias: [VuTracker, verifica accesso, API key]
tag: [dominio/integrazioni]
fonti: [Codice Discord-access-app, Runbook cambio dominio]
creato: 2026-07-25
aggiornato: 2026-08-12
stato: obsoleto
---

# Integrazione VuTracker

> [!warning] Integrazione rimossa il 2026-08-12
> **VuPass e VuTracker non comunicano più.** L'endpoint, il filtro API key e la chiave condivisa
> sono stati eliminati dal codice: i due prodotti sono indipendenti. Questa pagina resta come
> storia di com'era, perché il codice rimosso è ancora recuperabile da git e perché VuTracker,
> finché non viene aggiornato, continuerà a chiamare un endpoint che non esiste più.

## ⚠️ Conseguenza sul lato VuTracker

VuTracker interrogava questo endpoint al login Discord e ogni 6 ore. Finché lo fa, riceve `404` (il
controller non c'è più) e **nega l'accesso ai propri utenti**: la verifica dell'abbonamento va
sostituita con un meccanismo interno a VuTracker.

## Cosa è stato eliminato

| File | Ruolo |
|---|---|
| `VerificaAccessoController` | endpoint REST |
| `VerificaAccessoService` | logica di verifica |
| `VerificaAccessoDto` | DTO di risposta |
| `ApiKeyAuthFilter` | protezione con `X-API-Key` |

Più la property `vutracker.api-key` in `application.yml`, la riga `permitAll` su
`/api/verifica-accesso/**` e il `addFilterBefore` in `SecurityConfig`. La variabile
`VUTRACKER_API_KEY` non serve più in `.env` / `.env.prod` ([[Variabili d'ambiente]]).

## Com'era — l'endpoint

```
GET /api/verifica-accesso/{discordId}
Header: X-API-Key: <chiave condivisa>
```

Risposta: `ResponseDto<VerificaAccessoDto>` con `discordId`, `supporterAttivo`, `ruolo`, `scadenza`,
`username`.

## Com'era — la logica di verifica

Tre casi, valutati in ordine:

1. il Discord ID è in `utenti_lifetime` → `supporterAttivo = true`, `ruolo = "LIFETIME"`,
   `scadenza = null` ([[Utente lifetime]]);
2. l'[[Utente]] esiste e `dataScadenzaIscrizione >= adesso` (ora italiana) →
   `supporterAttivo = true`, `ruolo = "SUPPORTER_MEMBER"`, con la scadenza;
3. altrimenti → `supporterAttivo = false`.

Il criterio era **la scadenza sul database**, non il ruolo Discord: un utente a cui il bot non era
riuscito ad assegnare il ruolo risultava comunque attivo per VuTracker, e viceversa.

## Com'era — la protezione

L'endpoint era `permitAll` lato Spring Security, coperto da `ApiKeyAuthFilter`, attivo **solo** sui
percorsi che iniziavano con `/api/verifica-accesso`: confronto dell'header `X-API-Key` con
`vutracker.api-key`, `401` se la chiave lato server era vuota (fail-closed) o non coincideva, con
log dell'IP chiamante. Il confronto era una `equals` semplice, non a tempo costante.

Le due variabili da tenere allineate erano `VUTRACKER_API_KEY` qui e `DISCORD_ACCESS_APP_API_KEY`
su VuTracker.

## Voci correlate
- [[Utente]]
- [[Utente lifetime]]
- [[Sicurezza e autenticazione]]
- [[Endpoint REST]]
