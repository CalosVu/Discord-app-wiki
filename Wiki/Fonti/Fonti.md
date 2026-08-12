---
tipo: hub
titolo: Fonti
alias: [Gerarchia delle fonti]
tag: [meta/fonti]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Fonti

Elenco delle fonti da cui questa wiki è derivata e **ordine di attendibilità** con cui si risolvono
i conflitti (CLAUDE.md §3).

## Gerarchia delle fonti (dalla più alla meno attendibile)

| Rango | Fonte | Perché |
|---|---|---|
| 1 | **Codice sorgente su `main`** — [[Codice Discord-access-app]] | È ciò che gira in produzione: `main` viene deployato automaticamente ad ogni push |
| 2 | **Migration Flyway** (`db/migration/V<n>__*.sql`) | Versionate insieme al codice e applicate automaticamente all'avvio: sono lo schema reale |
| 3 | **Piani di sviluppo** — [[Piano sviluppo masterclass]], [[Piano sviluppo doppio Stripe]] | Contengono le **decisioni** e il *perché*, che il codice non esprime; ma descrivono anche parti non implementate o superate |
| 4 | **Runbook operativi** — [[Runbook cambio dominio]], [[Guida di deployment]], [[Guida SSL e DNS]], [[Guida Stripe CLI]] | Descrivono l'infrastruttura, non verificabile dal codice; il più recente prevale sul più vecchio |
| 5 | **Documentazione descrittiva iniziale** — [[DOC_PROGETTO]], [[Integrazione sistema pagamenti]] | Scritti a inizio progetto (2025), descrivono un sistema in larga parte **mai realizzato** o realizzato diversamente |

**Regola pratica:** se il codice e un documento si contraddicono, **vince il codice** e la claim del
documento va spostata in `## Storia / claim superate` sulla pagina interessata, non cancellata.

## Fonti ingerite

- [[Codice Discord-access-app]] — il repo applicativo: 5 moduli Maven, ~14.800 righe Java, schema SQL.
- [[DOC_PROGETTO]] — descrizione iniziale del progetto (2025-05). ⚠️ largamente superata.
- [[Integrazione sistema pagamenti]] — specifica tecnica iniziale dei pagamenti crypto (2025-06). ⚠️ largamente superata.
- [[Piano sviluppo masterclass]] — architettura e decisioni del sistema masterclass (2026-06).
- [[Piano sviluppo doppio Stripe]] — doppio account Stripe, blocco pagamenti, fix notifiche (2026-07).
- [[Guida di deployment]] — deploy su Hetzner, systemd, GitHub Actions, MySQL in Docker.
- [[Runbook cambio dominio]] — i 5 fronti da allineare a ogni cambio di dominio (2026-07).
- [[Guida SSL e DNS]] — setup nginx, Let's Encrypt, DNS, webhook Stripe.
- [[Guida Stripe CLI]] — testing dei webhook in locale.

## Fonti non ancora ingerite

Il debito di copertura è tracciato in `meta/aperture-ingest.md` (dump del DB di produzione, branch
non mergiati, materiale non tecnico, contenuto puntuale dei test).

## Voci correlate
- [[Panoramica]]
- [[index]]
