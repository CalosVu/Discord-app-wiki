---
name: portabilita-percorsi
description: Il progetto è condiviso via git; percorsi-macchina in .paths, mai assoluti nei file committati; memoria nel repo; segreti mai in chiaro.
metadata:
  type: project
---

Questa wiki è pensata per essere **condivisa tra più utenti via git**: tutto ciò che serve a
riprodurre l'ambiente (wiki, `CLAUDE.md`, `.claude/settings.json`, `.claude/memory/`) è committato,
così chi fa checkout e avvia `claude` nella cartella del repo ottiene **le stesse regole e memoria**.

I **percorsi assoluti macchina-specifici** NON vanno mai nei file condivisi: stanno solo in `.paths`
(per-utente, in `.gitignore`), copiato da `.paths.example`. Nei file condivisi si scrivono come
`${NOME_VARIABILE}` e si risolvono leggendo `.paths` all'avvio.

**Why:** un percorso assoluto hardcodato (es. `C:\Users\<nome>\...`) romperebbe il progetto per ogni
altro utente. L'astrazione via `.paths` rende il repo portabile.

**How to apply:**
- All'avvio sessione leggi `.paths` e `.claude/memory/MEMORY.md` (vedi `CLAUDE.md` §0).
- Nei file committati usa percorsi **relativi** (risorse interne) e `${VAR}` (risorse esterne); mai assoluti.
- ⚠️ **Segreti mai in chiaro** nei file committati (vedi `CLAUDE.md` §5.6): solo riferimenti.
- File per-utente da non committare: `.paths`, `.env`, segreti, `.claude/settings.local.json`,
  `<WikiDir>/.obsidian/workspace*.json`.
