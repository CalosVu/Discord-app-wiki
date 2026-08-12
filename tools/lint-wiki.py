# -*- coding: utf-8 -*-
"""wiki-lint — health check di una LLM Wiki (blueprint generico).

Esegue i controlli del workflow (CLAUDE.md §8.3 Lint) in modo deterministico e
ri-eseguibile.

Controlli:
- frontmatter obbligatorio (titolo, tipo, stato, creato, aggiornato)
- coerenza tra `tipo` frontmatter e cartella
- formato date YYYY-MM-DD
- wikilink rotti (target inesistente nel grafo)
- placeholder/cross-vault sospetti
- pagine orfane (nessun link entrante), escluse fonti/hub/index/log
- pagine stub (corpo troppo corto)
- claim potenzialmente datate (`stato: stabile` + `aggiornato` molto vecchio)

Uso (dalla radice del repo):
    WIKI_DIR=Wiki python tools/lint-wiki.py            # scan completo, exit 1 se ERROR
    WIKI_DIR=Wiki python tools/lint-wiki.py --paths f1.md f2.md   # solo alcuni (pre-commit)
    WIKI_DIR=Wiki python tools/lint-wiki.py --json     # output JSON parsabile
    WIKI_DIR=Wiki python tools/lint-wiki.py --strict   # i WARNING diventano ERROR

Se WIKI_DIR non è impostata, rileva la cartella (a un livello) che contiene index.md.
Severità: ERROR → exit 1 (blocca il pre-commit); WARNING → exit 0. Solo stdlib.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def detect_wiki_root() -> Path:
    env = os.environ.get("WIKI_DIR")
    if env and (REPO_ROOT / env).is_dir():
        return REPO_ROOT / env
    for entry in sorted(REPO_ROOT.iterdir()):
        if entry.is_dir() and (entry / "index.md").is_file():
            return entry
    sys.exit("wiki-lint: vault non trovato. Imposta WIKI_DIR=<cartella che contiene index.md>.")


WIKI_ROOT = detect_wiki_root()
META_ROOT = WIKI_ROOT / "meta"

# chiavi frontmatter (italiano) — CLAUDE.md §5.1
REQUIRED_FM = ("titolo", "tipo", "stato", "creato", "aggiornato")
VALID_TYPES = {
    # profilo esistente
    "entita", "concetto", "modulo", "tassonomia",
    # profilo nuovo
    "sezione", "business-logic", "config", "decisione", "nota",
    # comuni / moduli
    "fonte", "intervento", "ticket", "persona", "hub", "index", "log", "meta",
}
VALID_STATUS = {"bozza", "in-revisione", "stabile", "completa", "obsoleto", "stub"}
# cartella -> tipo atteso (coerenza); le cartelle non mappate non vengono controllate
FOLDER_TYPE = {
    "Entita": "entita", "Concetti": "concetto", "Moduli": "modulo", "Tassonomie": "tassonomia",
    "Sezioni": "sezione", "BusinessLogic": "business-logic", "Config-Credenziali": "config",
    "Decisioni": "decisione", "Fonti": "fonte", "Interventi": "intervento",
    "Persone": "persona", "Sistemi": "sistema", "Processi": "processo",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[\[([^\]\|#\\]+?)(?:#[^\]\|\\]*)?(?:\|[^\]\\]+)?\]\]")
CROSSVAULT_RE = re.compile(r"\[\[(?:\.\./){3,}|\[\[/")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
IMG_EMBED_RE = re.compile(r"!\[\[[^\]\n]+?\.(?:png|jpe?g|gif|webp|svg|bmp)\]\]", re.IGNORECASE)

ORPHAN_EXCLUDED = {"index", "log", "aperture-ingest", "glossario", "readme", "claude", "panoramica"}
PLACEHOLDER_EXCLUDED_PAGES = {"aperture-ingest"}
PLACEHOLDER_PATTERNS = {"...", "pagina-creata", "pagina-wiki", "slug", "nome-pagina", "altra pagina"}

STUB_LINES_THRESHOLD = 12
STALE_DAYS = int(os.environ.get("WIKI_STALE_DAYS", "180"))  # 'stabile' + aggiornato più vecchio → warning


@dataclass
class Finding:
    severity: str
    file: str
    rule: str
    message: str

    def to_dict(self) -> dict:
        return {"severity": self.severity, "file": self.file, "rule": self.rule, "message": self.message}


@dataclass
class Page:
    path: Path
    slug: str
    category: str
    body: str
    frontmatter: dict
    links_out: set
    nlines_body: int


def strip_inline_code(text: str) -> str:
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)


def parse_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = text
    fm: dict = {}
    m = FM_RE.match(text)
    if m:
        body = text[m.end():]
        for line in m.group(1).split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("- "):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
    body_for_links = IMG_EMBED_RE.sub(" ", strip_inline_code(body))
    links = {ml.group(1).strip().lower().split("/")[-1] for ml in LINK_RE.finditer(body_for_links)}
    return Page(path=path, slug=path.stem.lower(), category=path.parent.name, body=body,
                frontmatter=fm, links_out=links,
                nlines_body=sum(1 for ln in body.splitlines() if ln.strip()))


def collect_pages(paths=None) -> list:
    if paths is None:
        paths = [p for p in WIKI_ROOT.rglob("*.md") if META_ROOT not in p.parents]
    return [parse_page(p) for p in paths if p.exists() and p.suffix == ".md"]


def build_known_slugs() -> set:
    slugs = {p.stem.lower() for p in WIKI_ROOT.rglob("*.md")}
    slugs.update({"claude", "index", "readme"})
    return slugs


def build_inbound(pages) -> dict:
    inbound = defaultdict(set)
    for p in pages:
        for tgt in p.links_out:
            inbound[tgt].add(p.slug)
    return inbound


def rel(p: Page) -> str:
    return p.path.relative_to(REPO_ROOT).as_posix()


def check_frontmatter(p: Page):
    out = []
    for k in REQUIRED_FM:
        if not p.frontmatter.get(k):
            out.append(Finding("ERROR", rel(p), "frontmatter-missing",
                               f"Campo obbligatorio `{k}` mancante dal frontmatter YAML (CLAUDE.md §5.1)."))
    tipo = p.frontmatter.get("tipo", "").strip().lower()
    if tipo and tipo not in VALID_TYPES:
        out.append(Finding("ERROR", rel(p), "frontmatter-type",
                           f"`tipo` non valido: `{tipo}`. Ammessi: {', '.join(sorted(VALID_TYPES))}."))
    exp = FOLDER_TYPE.get(p.category)
    if exp and tipo and tipo != exp and tipo != "hub":
        out.append(Finding("ERROR", rel(p), "frontmatter-type-mismatch",
                           f"Il file è in `{p.category}/` ma dichiara `tipo: {tipo}` (atteso `{exp}`). "
                           f"Sposta il file o correggi il tipo."))
    stato = p.frontmatter.get("stato", "").strip().lower()
    if stato and stato not in VALID_STATUS:
        out.append(Finding("ERROR", rel(p), "frontmatter-status",
                           f"`stato` non valido: `{stato}`. Ammessi: {', '.join(sorted(VALID_STATUS))}."))
    for k in ("creato", "aggiornato"):
        v = p.frontmatter.get(k, "").strip().strip('"').strip("'")
        if v and not DATE_RE.match(v):
            out.append(Finding("ERROR", rel(p), "frontmatter-date",
                               f"Data non valida in `{k}`: `{v}`. Usare `YYYY-MM-DD`."))
    return out


def check_broken_links(p: Page, known: set):
    out = []
    is_meta = p.slug in PLACEHOLDER_EXCLUDED_PAGES
    for tgt in p.links_out:
        if tgt in known:
            continue
        if tgt in PLACEHOLDER_PATTERNS:
            if not is_meta:
                out.append(Finding("ERROR", rel(p), "placeholder-link",
                                   f"Wikilink placeholder `[[{tgt}]]` in una pagina di contenuto: "
                                   f"sostituisci col nome reale o rimuovi."))
            continue
        sev = "WARNING" if is_meta else "ERROR"
        out.append(Finding(sev, rel(p), "broken-link",
                           f"Wikilink rotto: `[[{tgt}]]` non corrisponde ad alcuna pagina. "
                           f"Crea la pagina, correggi il refuso o rimuovi il link."))
    return out


def check_cross_vault(p: Page):
    out = []
    for m in CROSSVAULT_RE.finditer(strip_inline_code(p.body)):
        out.append(Finding("ERROR", rel(p), "cross-vault-wikilink",
                           "Wikilink che esce dal vault (3+ `../` o `/` iniziale): non navigabile in "
                           "Obsidian. Converti in link Markdown `[testo](path.md)`."))
    return out


def check_orphan(p: Page, inbound: dict):
    tipo = p.frontmatter.get("tipo", "").strip().lower()
    if tipo in ("fonte", "hub"):
        return []
    if p.slug in ORPHAN_EXCLUDED:
        return []
    if inbound.get(p.slug):
        return []
    return [Finding("WARNING", rel(p), "orphan",
                    "Pagina orfana: nessun wikilink entrante. Aggiungi almeno un link da una pagina "
                    "hub/correlata (CLAUDE.md §5.2) o valuta la rimozione.")]


def check_stub(p: Page):
    tipo = p.frontmatter.get("tipo", "").strip().lower()
    if p.nlines_body >= STUB_LINES_THRESHOLD or tipo in ("persona", "fonte", "hub"):
        return []
    return [Finding("WARNING", rel(p), "stub",
                    f"Pagina stub: solo {p.nlines_body} righe (soglia {STUB_LINES_THRESHOLD}). "
                    f"Integra dalla fonte o dichiara esplicitamente il limite di copertura.")]


def check_stale(p: Page):
    if p.frontmatter.get("stato", "").strip().lower() != "stabile":
        return []
    if p.frontmatter.get("tipo", "").strip().lower() == "persona":
        return []
    upd = p.frontmatter.get("aggiornato", "").strip().strip('"').strip("'")
    if not upd or not DATE_RE.match(upd):
        return []
    try:
        d = datetime.date.fromisoformat(upd)
    except ValueError:
        return []
    if (datetime.date.today() - d).days > STALE_DAYS:
        return [Finding("WARNING", rel(p), "stale-stable",
                        f"`stato: stabile` ma `aggiornato: {upd}` (> {STALE_DAYS} giorni fa). "
                        f"Verifica se fonti più recenti la integrano/smentiscono.")]
    return []


def run(paths):
    all_pages = collect_pages()
    known = build_known_slugs()
    inbound = build_inbound(all_pages)
    target = collect_pages(paths) if paths else all_pages
    findings = []
    for p in target:
        findings += check_frontmatter(p)
        findings += check_broken_links(p, known)
        findings += check_cross_vault(p)
        findings += check_orphan(p, inbound)
        findings += check_stub(p)
        findings += check_stale(p)
    return findings


def format_text(findings) -> str:
    if not findings:
        return "OK  wiki-lint: nessun problema trovato.\n"
    by_sev = defaultdict(list)
    for f in findings:
        by_sev[f.severity].append(f)
    out = []
    headers = {"ERROR": "ERRORI ({n}) — bloccano il commit",
               "WARNING": "AVVERTIMENTI ({n}) — non bloccanti"}
    for sev in ("ERROR", "WARNING"):
        items = by_sev.get(sev, [])
        if not items:
            continue
        out.append("")
        out.append(headers[sev].format(n=len(items)))
        out.append("-" * 60)
        for f in items:
            out.append(f"  * {f.file}")
            out.append(f"    [{f.rule}] {f.message}")
    n_err, n_warn = len(by_sev.get("ERROR", [])), len(by_sev.get("WARNING", []))
    out.append("-" * 60)
    out.append(f"Riepilogo: {n_err} error(i), {n_warn} avvertiment(i).")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="wiki-lint — health check LLM Wiki")
    ap.add_argument("--paths", nargs="*", help="check solo questi path")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--strict", action="store_true", help="i WARNING diventano ERROR")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    paths = None
    if args.paths:
        paths = []
        for p in args.paths:
            pp = Path(p)
            if not pp.is_absolute():
                pp = REPO_ROOT / pp
            if pp.suffix == ".md" and WIKI_ROOT in pp.parents and META_ROOT not in pp.parents:
                paths.append(pp)
        if not paths:
            print("wiki-lint: nessun file markdown del vault tra quelli passati.")
            return 0

    findings = run(paths)
    if args.json:
        print(json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2))
    else:
        print(format_text(findings))

    has_error = any(f.severity == "ERROR" for f in findings)
    has_warn = any(f.severity == "WARNING" for f in findings)
    return 1 if (has_error or (args.strict and has_warn)) else 0


if __name__ == "__main__":
    sys.exit(main())
