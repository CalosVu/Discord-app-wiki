---
tipo: modulo
titolo: Storage R2
alias: [Cloudflare R2, presigned URL, R2StorageService]
tag: [dominio/masterclass, dominio/infrastruttura]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Storage R2

Il deposito dei video delle [[Masterclass]]: un **bucket privato** su Cloudflare R2, accessibile solo
tramite link firmati a scadenza.

R2 è S3-compatibile: il codice usa l'AWS SDK v2 con `endpointOverride` sull'endpoint R2, regione
`auto` e **path-style access** (consigliato per R2).

## Le due operazioni

| Metodo | Quando | Perché |
|---|---|---|
| `esisteOggetto(key)` | **prima** del checkout | evitare che qualcuno paghi per un file inesistente |
| `generaPresignedUrl(key, durata)` | **dopo** il pagamento | erogare il contenuto |

`esisteOggetto` fa una **HEAD**: `NoSuchKey` o 404 → `false`; ogni altro errore (403, rete) viene
**propagato**, per non confondere «il file manca» con «non riesco a raggiungere R2».

## Il link firmato

Generato al volo dopo il pagamento, con durata letta da `MASTERCLASS_DURATA_LINK_ORE`
([[Tabella server_config]], default 3 ore). Punta all'endpoint S3 API di R2, non al dominio pubblico
`r2.dev`.

Il limite tecnico di SigV4 è **7 giorni**: le poche ore usate sono ampiamente entro il limite.

Il link **non viene salvato** da nessuna parte, e i log non lo riportano mai per intero: contiene la
firma.

## I tre presupposti di sicurezza

1. **Il bucket deve restare privato**: nessun Public Development URL (`r2.dev`) attivo, nessun
   oggetto `public-read`. Senza questo, tutto il resto è inutile.
2. **La object key non deve essere indovinabile**: convenzione di includere un UUID nel nome
   (`masterclass/relatore3/a1b2c3-uuid.zip`).
3. **Le credenziali stanno solo nell'ambiente** ([[Credenziali R2]]), mai nel database né nel repo.

## Cosa il bot non fa

Il bot **non carica e non cancella** nulla su R2: l'upload è manuale (dashboard, `rclone`, `aws
cli`). L'unica scrittura possibile sarebbe un caricamento fuori dall'applicazione.

Nota implementativa: il client S3 usa `UrlConnectionHttpClient` invece del client Apache di default,
per evitare un conflitto di dipendenze con Apache HttpClient 5.

## Rischio residuo accettato

Nella finestra di validità il link **è condivisibile** e il file scaricabile: chi lo riceve entro la
scadenza può ridistribuire il video. Nessun DRM, nessun watermark. Evoluzioni valutate e non
implementate: watermark per-utente, streaming proxy con token monouso, Cloudflare Stream.

## Voci correlate
- [[Sistema masterclass]]
- [[Masterclass]]
- [[Credenziali R2]]
