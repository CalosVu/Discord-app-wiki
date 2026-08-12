---
tipo: hub
titolo: Config-Credenziali
alias: [configurazioni, segreti]
tag: [dominio/configurazione]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Config-Credenziali

Riferimenti a configurazioni e credenziali: **dove** vivono, **come si chiamano**, chi le usa e come
si ruotano.

> ⚠️ **Regola inviolabile (CLAUDE.md §5.6): qui non compare MAI un valore.** Solo nomi di variabili,
> posizioni, formati e procedure. I valori reali stanno nel file d'ambiente sul server, escluso da
> git.

## Contenuto

- [[Variabili d'ambiente]] — l'inventario completo delle variabili lette dall'applicazione.
- [[Ambienti e profili Spring]] — i tre profili, cosa cambia in ciascuno, dove si legge il `.env`.
- [[Chiavi Stripe]] — le chiavi dei due account supporter e quelle per-relatore delle masterclass.
- [[Credenziali R2]] — accesso al bucket privato dei video.

## Configurazione a due livelli

Il sistema ha **due** posti dove si configura il comportamento, con proprietà diverse:

| Livello | Dove | Serve un riavvio? | Contiene segreti? |
|---|---|---|---|
| **Ambiente** | file `.env` sul server, letto all'avvio | **sì** | sì |
| **Runtime** | tabella `server_config` nel database | **no** | no |

Vedi [[Tabella server_config]] per il secondo livello.

## Le regole di igiene applicate nel codice

- Nessun segreto nel database: le chiavi Stripe dei relatori si leggono dall'ambiente, non da una
  colonna ([[Chiavi Stripe]]).
- Nessun segreto nella process list: la password del DB passa a `mysqldump` via variabile d'ambiente
  ([[Backup del database]]).
- Nessun segreto nei log: i presigned URL non vengono mai loggati per intero ([[Storage R2]]).
- Il file d'ambiente sul server va protetto con `chmod 600`.
- ⚠️ In `application.yml` restano, **nei commenti**, alcune chiavi Stripe **di test**: sono da
  rimuovere (segnalato in [[Piano sviluppo doppio Stripe]]).

## Voci correlate
- [[Tabella server_config]]
- [[Deploy e CI-CD]]
- [[Sicurezza e autenticazione]]
