---
description: Health-check e manutenzione della wiki (lint) — orfani, link rotti, indice, frontmatter
---

Esegui la **manutenzione/lint** della wiki (CLAUDE.md §8.3).

1. Esegui lo script dalla radice del repo:
   `WIKI_DIR=Wiki PYTHONIOENCODING=utf-8 python tools/lint-wiki.py`.
2. **Interpreta l'output** e proponi/applica le correzioni a basso rischio:
   - **Link rotti** reali → correggi (rinomina file o alias `[[file|testo]]`), escludendo i
     placeholder dei template.
   - **Pagine orfane** → aggiungi cross-reference contestuali dalle pagine correlate.
   - **Pagine mancanti dall'indice** → aggiungile a `Wiki/index.md`.
   - **Anomalie frontmatter** → sistema.
3. **Segnala** eventuali **contraddizioni** o claim datati da rivedere (gerarchia §3).
4. Verifica §5.6: **nessun segreto in chiaro** nelle pagine `Config-Credenziali/` o altrove.
5. Appendi a `Wiki/meta/log.md`: `## [<data>] lint | <sintesi>`.
6. **Non** eseguire commit/push.
