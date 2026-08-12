---
description: Interroga la wiki e risponde con citazioni; propone di archiviare la risposta come pagina
argument-hint: "<domanda>"
---

Rispondi a una **domanda** usando la wiki (CLAUDE.md §8.2).

Domanda: **$ARGUMENTS**

1. Leggi `Wiki/index.md` per individuare le pagine rilevanti, poi **aprile e leggile**
   (entra in profondità, non fermarti all'indice).
2. Sintetizza una risposta chiara **con citazioni** alle pagine e alle origini (§5.4). Se
   l'informazione non è nella wiki, **dillo** esplicitamente invece di inventare.
3. **Compounding**: se la risposta produce conoscenza nuova e duratura, **proponi** di archiviarla
   come nuova pagina nella cartella giusta; se l'utente accetta, creala e aggiorna `index.md`.
4. Se la domanda è significativa, appendi a `Wiki/meta/log.md`: `## [<data>] query | <domanda sintetica>`.
5. **Lazy ingest** (profilo esistente): se la risposta richiede materiale non ancora ingerito,
   cerca la voce in `Wiki/meta/aperture-ingest.md`; con l'ok dell'utente leggilo on-demand,
   filalo nelle pagine wiki e marca la voce `✅ INGERITA`.
5. **Non** eseguire commit/push.
