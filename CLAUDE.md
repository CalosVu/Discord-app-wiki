# CLAUDE.md — Schema della LLM Wiki di VuPass

> Questo file è lo **schema** della wiki: dice all'agente come la wiki è strutturata, quali
> convenzioni seguire e quali workflow eseguire per registrare/ingerire conoscenza, rispondere a
> domande e mantenere la knowledge base. È la configurazione che trasforma l'agente da chatbot
> generico a **manutentore disciplinato della wiki**.
>
> Schema e wiki **co-evolvono**: quando emerge una convenzione migliore, aggiorna questo file e
> registra la modifica in `log.md`.
>
> Profilo di questa wiki: **esistente** (nuovo = authored-first, la wiki cresce col progetto;
> esistente = ingest-first, la wiki è derivata da fonti). Generato da `/wiki-init` il 2026-07-25.

---

## 0. Avvio sessione: portabilità, percorsi e memoria  (LEGGI PER PRIMO)

**All'inizio di ogni sessione, l'agente DEVE:**
1. **Leggere `./.paths`** (se manca, avvisare l'utente di crearlo da `./.paths.example`). Definisce
   le variabili di percorso locali. In bash: `set -a; . ./.paths; set +a` (poi `$NOME_VAR`).
2. **Leggere `./.claude/memory/MEMORY.md`** e i file di memoria rilevanti. La memoria di progetto
   **vive nel repo** (`./.claude/memory/`), committata e condivisa — NON nella home di Claude.

**Regole di portabilità (inviolabili):**
- **Mai** scrivere percorsi assoluti macchina-specifici (es. `C:\Users\<nome>\...`) nei file
  **committati** (`CLAUDE.md`, `.claude/memory/`, pagine wiki, `.claude/settings.json`).
- Risorse **interne al repo** (wiki, `assets/`) → sempre **percorsi relativi** alla radice del repo.
- Risorse **esterne** (codice sorgente, DB, documenti locali) → **variabile** `${NOME}` definita in
  `.paths`. Serve un nuovo percorso esterno → aggiungilo a `.paths.example` (template condiviso) e
  chiedi all'utente di valorizzarlo nel proprio `.paths`.

**Cosa è committato vs per-utente:**

| Committato (condiviso) | Per-utente (in `.gitignore`) |
|---|---|
| `CLAUDE.md`, `.claude/memory/`, `.claude/settings.json` | `.paths`, `.env`, file di segreti |
| `.paths.example`, `README.md`, `.gitignore` | `.claude/settings.local.json` |
| Wiki (`Wiki/`) | `Wiki/.obsidian/workspace*.json` |

> ⚠️ Committare `CLAUDE.md`, `.claude/` e `.claude/memory/` è una **scelta di questo progetto** che
> sovrascrive la regola globale che di norma li esclude. Resta valido: **nessun `git commit`/`push`
> senza richiesta esplicita dell'utente.**

---

## 1. Di cosa parla la wiki (dominio)

**VuPass** è il prodotto che gestisce gli accessi a pagamento a una community Discord: applicazione
Java 21 / Spring Boot 3.2.3, parte della famiglia **VuTradingFarm** insieme a *VuTracker* e
*VuMarkets*. Il repository si chiama ancora `Discord-access-app`.

La prima istanza in produzione serve la community **InWestors** (trading/finanza) — da non
confondere col prodotto: InWestors è il server Discord gestito, VuPass è il software che lo gestisce.

Il cuore è un bot JDA che parla con gli utenti in messaggio privato: verifica l'accettazione del
disclaimer, incassa abbonamenti *Supporter Member* via **Stripe** (due account bilanciati) e
**crypto USDT/USDC su Arbitrum**, assegna e revoca i ruoli Discord, traccia referral e commissioni
agenti, vende **masterclass video** dei relatori (Cloudflare R2 + Stripe) ed espone un endpoint REST
con cui *VuTracker* verifica se un utente ha un abbonamento attivo.

La wiki descrive **la business logic realmente implementata**: comandi utente/admin/agente/relatore,
flussi di pagamento, batch schedulati, tabella di configurazione runtime, modello dati e deploy.

La wiki è una **knowledge base** del progetto: spiega *cosa fa*, *come funzionano* i suoi concetti,
entità, moduli e processi, e *come si tengono insieme*. Lingua della wiki: **italiano**. I termini
tecnici originali vanno mantenuti tra parentesi quando utile.

---

## 2. Architettura: i tre livelli

### 2.1 Fonti grezze (immutabili — sola lettura)

L'agente **legge** dalle fonti ma **non le modifica mai**. Sono la fonte di verità. Le fonti
concrete di questo progetto e la loro priorità sono elencate in `Wiki/Fonti/Fonti.md` e i
percorsi esterni in `.paths` (codice sorgente della app, cartella documentazione).

### 2.2 La wiki (generata dall'LLM — di proprietà dell'agente)

Directory `./Wiki/` (vault Obsidian). L'agente **possiede interamente** questo livello: crea
pagine, le aggiorna, mantiene cross-reference e coerenza. L'utente legge e indirizza; l'agente scrive.

### 2.3 Lo schema (questo file)

`./CLAUDE.md`. Configurazione co-evolutiva. Quando cambi una convenzione, aggiorna qui e logga.

---

## 3. ⚠️ Gerarchia delle fonti e gestione dei conflitti (REGOLA CARDINE)

Le fonti hanno una **precedenza**. Quando due si contraddicono, vince quella di rango più alto.
L'ordine di priorità di questo progetto è definito in `Wiki/Fonti/Fonti.md`. Criterio adottato:
**il codice sorgente su `main` > gli script SQL del repo > i piani di sviluppo > la documentazione
descrittiva più vecchia**. Vale il principio generale: **la realtà osservata/verificata > la
documentazione**.

Quando una nuova fonte contraddice la wiki esistente, la pagina va **aggiornata col dato più
attendibile** e la versione superata va **annotata, non cancellata**, con questo callout:

```markdown
> [!warning] Sostituito da fonte più attendibile
> La fonte «A» affermava: «X». La fonte «B» ([[…]]) indica invece: «Y». **Vale Y.**
```

Ogni affermazione fattuale nella wiki deve essere **tracciabile alla sua origine** (§5.4).

**Contraddizioni e claim superate (non sovrascrivere alla cieca):**
- Se una nuova fonte **contraddice** una claim esistente e nessuna delle due è chiaramente
  superata, non cancellare: aggiungi in pagina una sezione `## Contraddizioni / divergenze` con
  entrambe le posizioni e la fonte di ciascuna. Registra l'evento in `meta/log.md`.
- Se una nuova fonte **supera** una claim obsoleta (dato più recente/attendibile), aggiorna la
  claim e sposta la versione vecchia in `## Storia / claim superate` con la fonte originale.

---

## 4. Convenzioni delle cartelle

```
Wiki/
├── index.md            # CATALOGO (orientato ai contenuti) — §6, visibile al lettore
├── Panoramica.md       # Pagina hub / sintesi di alto livello
├── Entita/             # "cose" del dominio: utenti, pagamenti, masterclass, agenti…
├── Concetti/           # meccanismi trasversali: ruoli, promo, idempotenza, fee…
├── Moduli/             # aree funzionali e flussi: comandi, pagamenti, batch, deploy…
├── Tassonomie/         # elenchi codificati: server_config, enum, stati
├── Config-Credenziali/ # RIFERIMENTI a configurazioni e credenziali (§5.6 — mai valori)
├── Interventi/         # tracciamento lavori sul codice (bug/difetti/MEV)
├── Fonti/              # un riassunto per ogni fonte ingerita
├── assets/             # Immagini e allegati (embed ![[...]])
└── meta/               # File di servizio del manutentore (nascosti al lettore Obsidian)
    ├── log.md          #   CRONOLOGIA (append-only) — §7
    └── aperture-ingest.md  # debito di ingest — §8.1.1
```

> `meta/` è escluso dalla navigazione Obsidian del lettore via `.obsidian/app.json`
> (`userIgnoreFilters`). `CLAUDE.md` e `tools/` stanno fuori dal vault, quindi il lettore non li vede.

**Criterio di smistamento** (a quale cartella appartiene una pagina): scegli la cartella del
**ruolo primario** della nozione; se potrebbe stare in due, scegline una **canonica** e crea
cross-reference dall'altra. **Non duplicare**: una nozione = una pagina canonica.

Tassonomia di partenza (adattala al dominio in `Fonti/Fonti.md` e §1):
- **Entita/** → "cose" e oggetti del dominio (sostantivi).
- **Concetti/** → idee/meccanismi trasversali.
- **Moduli/** → aree funzionali e processi (verbi/flussi).
- **Tassonomie/** → elenchi codificati (stati, causali, codici).
- **Config-Credenziali/** → *riferimenti* a configurazioni e credenziali (§5.6 — mai valori).
- **Fonti/** → un riassunto per ogni fonte ingerita.

---

## 5. Convenzioni delle pagine

### 5.1 Frontmatter (YAML) — obbligatorio su ogni pagina
```yaml
---
tipo: entita | concetto | modulo | tassonomia | config | fonte | intervento | hub
titolo: Nome leggibile della pagina
alias: [sinonimi, sigle]
tag: [dominio/sottodominio]
fonti: []          # provenienza dei contenuti (pagine-fonte, file di codice, decisioni)
creato: 2026-07-25
aggiornato: 2026-07-25
stato: bozza | in-revisione | stabile | obsoleto
---
```
Aggiorna `aggiornato` ad ogni modifica e aggiungi le nuove origini a `fonti`. Le date sono sempre
**assolute** (`YYYY-MM-DD`), mai relative. Il tipo deve essere coerente con la cartella (il linter
lo verifica). Le chiavi del frontmatter restano in inglese/italiano come qui; i valori nella lingua
della wiki.

### 5.2 Struttura tipica di una pagina
- `# Titolo` (H1, = `titolo`).
- **Definizione in una frase** in apertura (cosa è / a cosa serve).
- Corpo con sezioni (`##`).
- **Collegamenti** `[[Altra pagina]]` liberi nel testo. Linka generosamente: un `[[Nome]]` verso
  una pagina non ancora creata è lecito — segnala qualcosa da scrivere, non un errore.
- **Sezione "Voci correlate"** in fondo.
- **Citazioni** dell'origine (§5.4).

### 5.3 Pagina-fonte (in `Fonti/`)
Per ogni fonte esterna ingerita: identificazione, rango nella gerarchia (§3), data di ingest,
sintesi dei contenuti chiave, elenco delle pagine wiki che ha creato/aggiornato.

### 5.4 Citazioni
Ogni affermazione fattuale è tracciabile all'origine. Usa link wiki con riferimento puntuale quando
possibile: `(fonte: [[Nome-fonte]] §X)`, oppure per il codice `(fonte: codice \`percorso/file:riga\`)`,
oppure `(decisione: [[Decisioni/…]])`.

### 5.5 Nomi e wikilink
- Nomi file = titolo leggibile in italiano (accenti ammessi: Obsidian li gestisce).
- **Cartelle in ASCII** (es. `Entita`, non `Entità`) per compatibilità cross-tool.
- Una sola pagina canonica per nozione; i sinonimi vanno in `alias`, non in pagine doppie.

### 5.6 ⚠️ Credenziali e configurazioni sensibili — SOLO RIFERIMENTI, MAI VALORI
La wiki può finire in un repo condiviso via git: **non deve MAI contenere segreti in chiaro**
(password, token, chiavi, stringhe di connessione con credenziali). Le pagine `Config-Credenziali/`
documentano:
- **dove** vive il segreto (secret manager, variabile d'ambiente, file locale in `.gitignore`);
- il **nome** della variabile/chiave (es. `DB_PASSWORD`), **non** il valore;
- **struttura**, ambiente, owner, procedura e cadenza di **rotazione**, chi ha accesso.

I valori reali restano fuori da git: `.paths`/`.env`/secret manager. Se trovi un segreto in chiaro
in una pagina, **segnalalo e rimuovilo** (ricordando che resta nella cronologia git finché non si
riscrive la storia).

### 5.7 Fatto atomico = una sola pagina
Un dato **atomico** (una credenziale come riferimento, un IP, un percorso file, un comando, un
endpoint, una coordinata) vive in **una sola** pagina — la sua fonte naturale — e le altre pagine lo
**linkano** invece di ricopiarlo. Se ti accorgi di dover ripetere lo stesso dato in più pagine,
l'asse di taglio è sbagliato: valuta una pagina unica per quell'asse (es. una pagina "ambienti" che
raccoglie host/percorsi, le altre vi rimandano). Il lint **non** rileva i fatti duplicati: alla
modifica del dato, le copie divergono in silenzio.

---

## 6. `index.md` — il catalogo (orientato ai contenuti)
Catalogo di **tutto** ciò che c'è nella wiki, per categoria. Ogni voce: link alla pagina +
riassunto in una riga. L'agente **aggiorna `index.md` ad ogni creazione/rinomina di pagina**. In
fase di **query** legge prima `index.md` per individuare le pagine rilevanti, poi entra in
profondità: a questa scala l'indice sostituisce il RAG a embedding.

## 7. `meta/log.md` — il diario (cronologico, append-only)
Registro di cosa è successo e quando, in `Wiki/meta/log.md`. **Append-only**: non riscrivere
la storia. Ogni voce inizia con un prefisso costante, così è interrogabile con unix
(`grep "^## \[" Wiki/meta/log.md | tail -5`):
```
## [YYYY-MM-DD] <tipo> | <titolo>
```
dove `<tipo>` ∈ `ingest | query | lint | manutenzione | intervento`. Corpo: cosa fatto, pagine
toccate, origine, decisioni/aperti.

---

## 8. Workflow

### 8.1 Ingest (ingestione di una fonte)
1. **Leggi** la fonte grezza (preferire estrazione testo).
2. **Discuti** i takeaway chiave con l'utente prima di scrivere in massa (ingest supervisionato,
   una fonte alla volta).
3. Crea/aggiorna la **pagina-fonte** in `Fonti/` (§5.3).
4. **Integra** nella wiki: crea/aggiorna pagine; mantieni i cross-reference. Una fonte può toccare
   molte pagine.
5. **Applica la gerarchia delle fonti** (§3): usa `## Contraddizioni / divergenze` o
   `## Storia / claim superate` per ciò che viene contraddetto/superato.
6. Registra in `meta/aperture-ingest.md` le parti **non** ingerite (capitoli/sezioni saltati).
7. **Aggiorna `index.md`**; **appendi a `meta/log.md`** una voce `ingest`.

#### 8.1.1 Lazy ingest on-demand
Non serve ingerire subito interi documenti. Ciò che salti va nel **debito di ingest**
(`meta/aperture-ingest.md`). Quando una query (§8.2) richiede materiale non ancora coperto:
1. Individua la voce nel registro (fonte + range + argomento).
2. Con l'**ok esplicito** dell'utente, leggi **solo** quella parte della fonte.
3. Sintetizza la risposta e **filala nelle pagine wiki** (nuove o aggiornate).
4. Marca la voce `✅ INGERITA <data> → [[pagina]]` (o `🟡 PARZIALE`); aggiorna `index.md` e
   appendi a `meta/log.md` una voce `ingest` (indicando che il trigger è stata la query).

### 8.2 Query (domanda alla wiki)
1. Leggi `index.md`, individua le pagine rilevanti, entra in profondità.
2. Sintetizza la risposta **con citazioni** (§5.4). Se l'informazione non è nella wiki, **dillo**
   esplicitamente invece di inventare.
3. **Compounding**: se la risposta produce conoscenza nuova e duratura, **proponi di archiviarla**
   come nuova pagina invece di lasciarla sparire nella chat. Se rilevante, logga una voce `query`.

### 8.3 Lint (health-check periodico)
Esegui `WIKI_DIR=Wiki python tools/lint-wiki.py` (opzioni: `--paths` per singoli file,
`--json`, `--strict`). Il linter classifica in **ERROR** (link rotti, frontmatter mancante/incoerente,
cross-vault, placeholder → exit 1) e **WARNING** (orfani, stub, claim datate → non bloccanti).
Correggi gli ERROR; per i WARNING e i controlli qualitativi (contraddizioni, cross-reference
mancanti, gap di copertura) valuta e proponi. Appendi a `meta/log.md` una voce `lint`.

> Un **hook `pre-commit`** (se abilitato con `git config core.hooksPath tools/hooks`) esegue il
> linter sui file wiki in staging e **blocca i commit con ERROR** (bypass: `git commit --no-verify`).

---

## 9. Regole operative per l'agente
- **La wiki la scrive e mantiene l'agente**, non l'utente a mano. L'utente cura le fonti/indirizzo
  e pone le domande.
- **Non modificare mai le fonti grezze.** In particolare: **non modificare mai il codice** del repo
  `Discord-access-app` da questo repo wiki. Qui si documenta, non si sviluppa.
- **Aggiornamento proattivo (regola soft):** a fine di un lavoro significativo (nuova feature,
  regola di business, decisione, configurazione), **proponi** all'utente di aggiornare la wiki e,
  con il suo ok, falla — oltre ai comandi on-demand `/wiki-…` che l'utente può invocare.
- **Credenziali (§5.6): solo riferimenti, mai valori.** Vigila che nessun segreto finisca committato.
- **Lingua delle pagine e della conversazione: italiano.**
- **Git**: nessun `git commit`/`push` senza richiesta esplicita. I file per-utente (`.paths`,
  `.env`, segreti, `.claude/settings.local.json`) restano esclusi via `.gitignore`.
- **Memoria** in `./.claude/memory/`, indicizzata in `MEMORY.md`; mai percorsi assoluti — usa `${VAR}`.
- **Fatto atomico = una pagina** (§5.7); **contraddizioni strutturate** (§3), non sovrascrivere.
- **Coerenza prima di tutto**: una nozione = una pagina canonica; aggiorna i cross-reference; tieni
  `index.md` e `meta/log.md` allineati ad ogni operazione; il linter (§8.3) non deve avere ERROR.

## Modulo interventi (tracciamento lavori sul codice)
La wiki traccia anche gli **interventi** sul codice (bug/difetti/MEV) in `Wiki/Interventi/`
(un intervento = una pagina, `tipo: intervento`). Comando `/wiki-interventi`.
- **Precedenti = predittore di regressioni**: prima di intervenire, cerca interventi simili in
  `Interventi/` per componente/file. Elenca le regressioni plausibili.
- **Frontmatter flat** (no YAML annidato): `difetto`, `task`, `release_target`, `componenti`,
  `file_toccati`, `utility_usate`, e campi deploy `deploy_ambiente|deploy_macchina|deploy_ruolo|`
  `deploy_percorso|deploy_url_servito|log_percorso|url_test`. Ometti i non pertinenti; per artefatti
  su macchine diverse usa liste allineate per indice.
- **⚠️ Regressioni**: se una fix può introdurne una, **segnalalo e verificalo** (altri usi del codice
  toccato) prima di chiudere. Non eseguo il codice: il review umano resta obbligatorio.
- Immagini in `assets/` (embed `![[...]]`, ignorate dal linter). Chiudi aggiornando `index.md` e
  `meta/log.md` (voce `intervento`).

## 10. Comandi slash di progetto (in `.claude/commands/`, prefisso `wiki-`)
Condivisi via git; velocizzano i flussi ricorrenti. Nessuno esegue commit/push.
- /wiki-chiedi — interroga la wiki e risponde con citazioni; propone di archiviare la risposta
- /wiki-ingest — ingerisce una fonte esterna applicando la gerarchia delle fonti
- /wiki-update-wiki — health-check e manutenzione (lint): orfani, link rotti, indice, frontmatter
- /wiki-interventi — registra/analizza un intervento sul codice, con deploy e regressioni
