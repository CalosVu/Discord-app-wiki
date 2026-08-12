# Discord-app-wiki

**LLM Wiki** di **VuPass** — il prodotto della famiglia VuTradingFarm che gestisce gli accessi a
pagamento a una community Discord. Il repository del codice si chiama
[Discord-access-app](https://github.com/CalosVu/Discord-access-app). La wiki descrive la business
logic realmente implementata (comandi, pagamenti, batch, modello dati,
configurazione, deploy), scritta e mantenuta da Claude Code secondo lo schema in `CLAUDE.md`.

Il vault è un **vault Obsidian**: si apre con Obsidian puntandolo alla cartella `Wiki/`, oppure si
legge come normali file Markdown.

## Setup (una volta per macchina)

```bash
git clone <questo-repo> Discord-app-wiki
cd Discord-app-wiki
cp .paths.example .paths      # poi apri .paths e metti i percorsi reali della TUA macchina
claude                        # avvia Claude Code nella cartella del repo
```

`.paths` è per-utente (in `.gitignore`) e definisce dove si trovano le fonti esterne:

| Variabile | Cosa punta |
|---|---|
| `DISCORD_APP_SRC` | il repo del codice applicativo — fonte di verità della wiki |
| `DISCORD_APP_DOCS` | la cartella con la documentazione tecnica e i materiali di progetto |

Per convenzione questo repo è **sibling** del repo del codice: i comandi installati là
(`/wiki-chiedi`, `/wiki-aggiorna`) cercano la wiki in `../Discord-app-wiki`.

## Struttura

```
CLAUDE.md          schema della wiki: convenzioni, gerarchia delle fonti, workflow
Wiki/              il vault Obsidian
  index.md         catalogo di tutte le pagine
  Panoramica.md    punto di partenza per la lettura
  Entita/          gli oggetti del dominio e le loro tabelle
  Concetti/        i meccanismi trasversali
  Moduli/          i flussi e le aree funzionali
  Tassonomie/      elenchi codificati: config, enum, endpoint, schema DB
  Config-Credenziali/  riferimenti a configurazioni e segreti (mai valori)
  Interventi/      tracciamento dei lavori sul codice
  Fonti/           provenienza dei contenuti e attendibilità
  meta/            file di servizio del manutentore (nascosti in Obsidian)
tools/lint-wiki.py health check della wiki
```

## Comandi

Da questo repo:

| Comando | Cosa fa |
|---|---|
| `/wiki-chiedi <domanda>` | risponde usando la wiki, con citazioni |
| `/wiki-ingest <fonte>` | ingerisce una nuova fonte applicando la gerarchia di attendibilità |
| `/wiki-update-wiki` | lint e manutenzione: link rotti, orfani, frontmatter, indice |
| `/wiki-interventi <id o descrizione>` | registra o analizza un intervento sul codice |

Dal repo del codice: `/wiki-chiedi` e `/wiki-aggiorna` (riporta qui il lavoro appena svolto).

## Lint

```bash
WIKI_DIR=Wiki PYTHONIOENCODING=utf-8 python tools/lint-wiki.py
```

Un hook `pre-commit` (attivato con `git config core.hooksPath tools/hooks`) esegue il lint sui file
wiki in staging e **blocca i commit con ERROR**. Bypass di emergenza: `git commit --no-verify`.

## Due regole da rispettare

1. **Mai segreti in chiaro.** Le pagine `Config-Credenziali/` documentano nome della variabile,
   posizione e rotazione — **non** i valori (`CLAUDE.md` §5.6).
2. **Il codice è la fonte di verità.** Se una pagina e il codice divergono, vince il codice: la
   claim superata si annota, non si cancella (`CLAUDE.md` §3).
