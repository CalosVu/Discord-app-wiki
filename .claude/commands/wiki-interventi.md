---
description: Registra/analizza un intervento sul codice (ticket ricco con deploy e regressioni) — modulo opzionale
argument-hint: "<id difetto/task o descrizione dell'intervento>"
---

Analizza o registra un **intervento** sul codice del progetto (CLAUDE.md §Modulo interventi).

Input dell'utente: **$ARGUMENTS**

## 1. Contesto
1. Leggi `.paths` per i percorsi esterni (codice sorgente, eventuali cartelle task/info). Se manca
   o ha valori da compilare, fermati e chiedi all'utente di compilarlo.
2. Se esiste il testo del ticket/task (issue tracker o mail di richiesta), leggilo. Non inventare requisiti.

## 2. Cerca precedenti (predizione regressioni)
Cerca in `Wiki/Interventi/` interventi **storici simili** per componente/file/tipo di
operazione: sono il miglior predittore di regressioni. Elenca le regressioni plausibili derivate.

## 3. Analisi a codice
Leggi il codice sorgente rilevante (via `.paths`). Restituisci: piano d'azione, **file da toccare**,
utility da usare, **regressioni potenziali** dai precedenti, bozza di pagina-intervento.

## 4. Registra l'intervento (a lavoro svolto)
Crea `Wiki/Interventi/<ID>--<slug>.md` (prefisso ID difetto/task ammesso nel nome per
tracciabilità). Frontmatter `tipo: intervento` con **proprietà flat** (no YAML annidato):
`difetto`, `task`, `release_target`, `componenti`, `file_toccati`, `utility_usate`, e i campi deploy:
`deploy_ambiente`, `deploy_macchina`, `deploy_ruolo`, `deploy_percorso`, `deploy_url_servito`,
`log_percorso`, `url_test`. Ometti i non pertinenti. Se l'intervento tocca più artefatti su macchine
diverse, `deploy_macchina`/`deploy_percorso` possono essere **liste allineate per indice**.

Corpo: `## In sintesi`, opzionale `## Screenshot` (embed `![[...]]` in `assets/`, Prima/Dopo),
`## Analisi`, `## Deploy` (tabella artefatto→macchina→percorso), `## Regressioni potenziali`.

## 5. ⚠️ Regressioni (regola critica)
Se la fix introduce (o può introdurre) una regressione — side-effect su altre pagine/funzioni,
codice/CSS/JS condivisi — **segnalalo esplicitamente e verificalo** (controlla gli altri usi del
codice toccato) prima di considerare l'intervento concluso. Mai dare per scontata l'assenza di
regressioni. Non eseguo il codice: il review umano resta obbligatorio.

## 6. Chiudi
Aggiorna `Wiki/index.md`, appendi a `Wiki/meta/log.md` una voce `intervento`, e
**cita** codice/fonti. **Non** eseguire commit/push.
