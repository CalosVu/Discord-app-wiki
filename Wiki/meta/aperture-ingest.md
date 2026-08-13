---
tipo: meta
titolo: Aperture di ingest — debito di copertura
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Aperture di ingest — cosa non è ancora stato ingerito

> File di servizio del manutentore, in `meta/` (nascosto al lettore Obsidian).
> Registro del **debito di ingest**: parti di fonti (capitoli, sezioni, allegati) non ancora
> riversate nella wiki. Trasforma il "saltato" in debito **tracciato** invece che dimenticato.

## Scopo (CLAUDE.md §8.1.1 — lazy ingest on-demand)
1. **Sapere dove cercare** quando una query tocca materiale non ancora coperto.
2. **Evitare di rileggere** interi documenti: una volta ingerito un capitolo on-demand, si marca qui.
3. Rendere esplicito ciò che manca, così la copertura cresce in modo governato.

## Come si usa
Quando una query richiede contenuti non ingeriti:
1. Individua la voce qui sotto (fonte + range + argomento).
2. Con l'ok dell'utente, leggi **solo** quella parte della fonte.
3. Sintetizza la risposta e **filala nelle pagine wiki** (nuove o aggiornate).
4. Marca la voce: `✅ INGERITA 2026-07-25 → [[pagina-creata]]` (o `🟡 PARZIALE` con note).
5. Aggiorna `index.md` e appendi a `meta/log.md` una voce `ingest` (trigger: la query).

---

## Backlog

### Branch feature non mergiati su `main`
📁 `${DISCORD_APP_SRC}` (repo git) · pagina-fonte: [[Codice Discord-access-app]]
- **Branch aperti diversi da `main`** — in fase di init si è deciso di documentare **solo ciò che è
  in produzione**. Quando un branch viene mergiato, il suo contenuto va ingerito con `/wiki-aggiorna`
  dal repo del codice. Quando rileggere: al merge, o su domanda su una feature "non ancora attiva".

### Dump del database di produzione
📁 `${DISCORD_APP_DOCS}/Backup_db/dump-discord_db-202508121959.sql`
- **Schema e dati reali (agosto 2025)** — utile per validare lo [[Schema del database]] documentato
  contro quello realmente in produzione, e per conoscere volumi/valori reali di
  [[Tabella cfg_server]], `catalogo_servizi`, `agenti`, `relatori`. Non ingerito: contiene dati
  personali degli utenti. Quando rileggere: verifica di uno scostamento schema, o domanda su dati
  storici reali.

### Script di supporto
📁 `${DISCORD_APP_DOCS}/API/getFees.py`
- **Script Python per il recupero delle fee** — non collegato all'applicazione Java. Quando
  rileggere: domanda su calcolo/estrazione fee fuori dall'app.

### Materiale non tecnico della cartella documentazione
📁 `${DISCORD_APP_DOCS}/` · sottocartelle escluse per scelta esplicita in fase di init
- **`Marketing/`, `Loghi/`, `Live/`, `Lezioni/`, `Strategie/`, `Indicatore/`** — video `.mp4`/`.mkv`,
  immagini, `.psd`, PDF promozionali. Non testo tecnico: la wiki li citerebbe solo come inventario.
  Quando rileggere: se serve documentare il materiale delle masterclass o la comunicazione.
- **`TaxStripe/`** — fatture Stripe Tax in PDF (2025-08 → 2025-12). Documenti contabili, non logica
  applicativa. Quando rileggere: domanda su fiscalità/fatturazione Stripe.
- **`stripe_1.29.0_windows_x86_64/` + zip** — binario della Stripe CLI, coperto concettualmente da
  [[Guida Stripe CLI]]. Nessun contenuto da ingerire.
- **`WinSCP.ini`, `message.txt`** — configurazione locale di WinSCP e bozza di messaggio. Nessun
  valore documentale; `WinSCP.ini` può contenere credenziali di sessione: **non aprire**.

### Test JUnit
📁 `${DISCORD_APP_SRC}/discord-access-service/src/test/`
- **Contenuto puntuale dei test** — ne è documentata l'esistenza e lo scopo in
  [[Sicurezza e autenticazione]] e [[Bilanciamento degli account Stripe]], ma non i singoli casi.
  Quando rileggere: modifica a una delle logiche coperte (selettore account, validatori pagamenti,
  notifiche).
