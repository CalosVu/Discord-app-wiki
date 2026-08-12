---
tipo: hub
titolo: Interventi
alias: [ticket, fix, bug]
tag: [meta/interventi]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Interventi

Il tracciamento dei lavori sul codice: bug, difetti, manutenzioni evolutive. Un intervento = una
pagina in questa cartella, con `tipo: intervento`.

Si registrano con `/wiki-interventi` (da questo repo) oppure con `/wiki-aggiorna` dal repo del
codice.

## Perché tracciarli

**Gli interventi passati sono il miglior predittore delle regressioni future.** Prima di toccare un
componente, si cercano qui gli interventi che lo hanno già interessato: i punti che si sono rotti una
volta tendono a rompersi di nuovo.

## Cosa registrare in una pagina-intervento

Frontmatter **flat** (nessun YAML annidato), con i campi pertinenti fra:
`difetto`, `task`, `release_target`, `componenti`, `file_toccati`, `utility_usate`, e i campi deploy
`deploy_ambiente`, `deploy_macchina`, `deploy_ruolo`, `deploy_percorso`, `deploy_url_servito`,
`log_percorso`, `url_test`.

Corpo: `## In sintesi`, opzionale `## Screenshot` (embed da `assets/`), `## Analisi`, `## Deploy`,
`## Regressioni potenziali`.

## Interventi registrati

- [[2026-07-25 Referral non attribuito e Fix Referral inefficace]] — analisi dei tre difetti
  dell'attribuzione referral e piano per persistere il tracciamento. **In analisi**, nessuna modifica
  applicata.

## Punti caldi noti di questo progetto

Da tenere sotto controllo in ogni intervento che li sfiori:

| Area | Perché è delicata |
|---|---|
| `savePaymentAndUpdateUser` | è **l'unico** punto di salvataggio per crypto **e** Stripe: una modifica tocca entrambi i canali ([[Pagamento]]) |
| `getPromoAttiva` | **duplicato in tre classi**: va modificato in tutte ([[Promozioni temporali]]) |
| Enum Java ↔ colonne MySQL | in `prod` `ddl-auto: validate` blocca il boot se il tipo non combacia ([[Schema del database]]) |
| Migrazioni DB | non automatiche: `ALTER TABLE` a mano **prima** del deploy ([[Deploy e CI-CD]]) |
| Eventi webhook Stripe | servono **entrambi** (`checkout.session.completed` + `charge.updated`), su **ogni** account ([[Riconciliazione della fee Stripe]]) |
| Id del relatore | deve combaciare in URL webhook, DB e variabili d'ambiente ([[Relatore]]) |
| Push su `main` | è un **deploy in produzione**: annotare lo SHA stabile prima del merge |

## Voci correlate
- [[Panoramica]]
- [[Deploy e CI-CD]]
- [[Codice Discord-access-app]]
