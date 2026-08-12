---
tipo: entita
titolo: Referral pendente
alias: [referral_pendenti, ReferralPendente, attribuzione in attesa]
tag: [dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-26
aggiornato: 2026-07-26
stato: stabile
---

# Referral pendente

Un [[Utente]] entrato nel server per il quale **non è stato possibile determinare l'invito usato**, e
quindi il [[Referral agent]] da attribuirgli. Tabella `referral_pendenti`, introdotta dalla migration
`V3`.

È la coda di lavoro del comando `!SyncReferral` ([[Comandi admin]]).

## Struttura

| Campo | Colonna | Note |
|---|---|---|
| `discordId` | `discord_id` | `UNIQUE` + FK verso `users.discord_id`: una sola riga per utente |
| `username` | `username` | snapshot, per rendere leggibile il report del comando |
| `dataIngresso` | `data_ingresso` | definisce l'ordine con cui si tentano le attribuzioni |
| `tentativi` | `tentativi` | quante volte si è già provato |
| `ultimoTentativo` | `ultimo_tentativo` | quando |
| `motivo` | `motivo` | `NESSUN_DELTA` \| `AMBIGUO` → [[Enum di dominio]] |

## Il ciclo di vita

1. **Nasce** quando il confronto dei contatori degli inviti non dà esito univoco al momento
   dell'ingresso ([[Sistema referral e commissioni]]).
2. **Sopravvive** ai riavvii, a differenza del tracciamento in memoria di prima.
3. **Muore** appena l'attribuzione va a buon fine — dal retry automatico, dall'accettazione del
   disclaimer o da `!SyncReferral`.

## Perché la sua esistenza congela i contatori

Finché esiste almeno una riga qui, l'allineamento della baseline
(`referral_agent.utilizzi`) all'avvio del bot **viene saltato**. È deliberato: allineare in quel
momento cancellerebbe proprio la differenza che serve a recuperare questi utenti.

È l'invariante su cui si regge tutto il meccanismo, ed è coperta da test.

## I due motivi, e perché la distinzione conta

| Motivo | Significato | Recuperabile |
|---|---|---|
| `NESSUN_DELTA` | nessun invito risultava incrementato: contatore non ancora propagato da Discord | ✅ sì, da un nuovo tentativo |
| `AMBIGUO` | più inviti incrementati, o meno incrementi che utenti in attesa | ❌ no, l'informazione non esiste da nessuna parte |

Solo il primo caso innesca i **retry automatici** a 2, 5 e 15 secondi: sul secondo riprovare non
servirebbe a nulla.

## Voci correlate
- [[Sistema referral e commissioni]]
- [[Referral agent]]
- [[Comandi admin]]
- [[Onboarding e disclaimer]]
