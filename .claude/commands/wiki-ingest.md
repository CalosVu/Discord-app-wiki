---
description: Ingerisce una fonte esterna nella wiki applicando la gerarchia delle fonti (profilo esistente)
argument-hint: "<fonte: percorso/nome del documento, o voce del backlog Fonti/>"
---

Ingerisci una **fonte** nella wiki (CLAUDE.md §8.1 Ingest).

Fonte indicata: **$ARGUMENTS**

1. **Individua la fonte**: se `$ARGUMENTS` è vuoto o generico, leggi il backlog in
   `Wiki/Fonti/Fonti.md` e chiedi quale ingerire. Risolvi i percorsi esterni via `.paths`.
2. **Leggi** la fonte grezza (preferisci l'estrazione testo). **Non modificare mai** la fonte.
3. **Discuti i takeaway chiave** con l'utente prima di scrivere in massa (ingest supervisionato,
   una fonte alla volta).
4. Crea/aggiorna la **pagina-fonte** in `Wiki/Fonti/` (§5.3): identificazione, rango nella
   gerarchia (§3), data, sintesi, pagine toccate.
5. **Integra** nella wiki: crea/aggiorna le pagine di contenuto; mantieni i cross-reference. Applica
   la **gerarchia delle fonti** (§3): annota col callout ciò che viene superato, non cancellarlo.
6. ⚠️ §5.6: se la fonte contiene segreti, nella wiki va solo il **riferimento**, mai il valore.
7. Registra nel **debito di ingest** (`Wiki/meta/aperture-ingest.md`) le parti della fonte
   **non** ancora riversate (capitoli/sezioni saltati), per il lazy ingest on-demand successivo.
8. **Aggiorna `index.md`** e **appendi a `Wiki/meta/log.md`**: `## [<data>] ingest | <fonte>`.
8. **Non** eseguire commit/push.
