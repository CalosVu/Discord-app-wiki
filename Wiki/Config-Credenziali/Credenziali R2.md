---
tipo: config
titolo: Credenziali R2
alias: [R2 access key, Cloudflare credentials]
tag: [dominio/configurazione, dominio/masterclass]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Credenziali R2

L'accesso al bucket privato Cloudflare R2 che ospita i video delle [[Masterclass]].

> ⚠️ Solo nomi di variabili, mai valori (CLAUDE.md §5.6).

## Le quattro variabili

| Variabile | Contenuto | Segreto? |
|---|---|---|
| `R2_ENDPOINT` | endpoint S3 API: `https://<account_id>.r2.cloudflarestorage.com` | no, ma rivela l'account id |
| `R2_BUCKET` | nome del bucket (privato) | no |
| `R2_ACCESS_KEY_ID` | id del token R2 | parzialmente |
| `R2_SECRET_ACCESS_KEY` | **segreto**: firma i presigned URL | **sì** |

Sono lette in `R2Config` (`@ConfigurationProperties(prefix = "r2")`) e usate solo da
`R2StorageService` ([[Storage R2]]).

## Cosa comporta la compromissione

Con queste credenziali si può **generare autonomamente un presigned URL** per qualunque oggetto del
bucket, senza passare dall'applicazione e senza pagare. Sono quindi la chiave dell'intero contenuto
delle masterclass, e vanno trattate come il segreto più sensibile del sistema insieme al token del
bot.

## Rotazione

1. creare un **nuovo** API token R2 nel dashboard Cloudflare;
2. aggiornare `R2_ACCESS_KEY_ID` e `R2_SECRET_ACCESS_KEY`;
3. **riavviare** l'applicazione (le credenziali sono lette all'avvio e usate per costruire il
   presigner);
4. revocare il token vecchio.

⚠️ I presigned URL già emessi con il token vecchio **restano validi fino alla loro scadenza**: la
revoca non li invalida retroattivamente. Con durata di 3 ore la finestra è breve, ma esiste.

## I presupposti di configurazione del bucket

Non sono nell'applicazione ma sul pannello Cloudflare, e sono **necessari** perché il modello di
sicurezza tenga:

- il bucket deve essere **privato**: nessun **Public Development URL** (`r2.dev`) attivo;
- nessun oggetto con ACL `public-read`;
- un solo bucket per tutti i relatori (scelta esplicita).

Se il Public Development URL fosse attivo, i file sarebbero raggiungibili senza firma e tutto il
resto — presigned, scadenze, pagamento — sarebbe inutile.

## Permessi minimi

L'applicazione fa **solo** `HeadObject` e `GetObject` (tramite firma). Non carica e non cancella
nulla: un token in **sola lettura** è sufficiente. L'upload dei video avviene fuori
dall'applicazione.

## Voci correlate
- [[Storage R2]]
- [[Masterclass]]
- [[Variabili d'ambiente]]
