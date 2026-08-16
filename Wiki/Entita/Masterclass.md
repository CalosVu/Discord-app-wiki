---
tipo: entita
titolo: Masterclass
alias: [masterclass, corso video]
tag: [dominio/masterclass]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-08-15
stato: stabile
---

# Masterclass

Il singolo contenuto video in vendita, appartenente a un [[Relatore]]. Tabella `masterclass`,
entità `Masterclass`.

## Come si pubblica

Procedura **manuale in due passi** (nessun comando del bot):

1. caricare il file su Cloudflare R2 (dashboard, `rclone` o `aws cli`) — vedi [[Storage R2]];
2. inserire la riga in `masterclass` via SQL, con la `r2_object_key` **esattamente uguale** al path
   del file caricato.

## Campi

| Campo | Colonna | Note |
|---|---|---|
| `relatore` | `relatore_id` | FK verso [[Relatore]] |
| `titolo` | `titolo` | mostrato nei menu; troncato a 100 caratteri nelle option Discord |
| `descrizione` | `descrizione` | testo dell'embed di dettaglio |
| `prezzoEur` | `prezzo_eur` | **unica** fonte del prezzo: mai preso dal client |
| `percentualeServer` | `percentuale_server` | quota trattenuta dal server, `NOT NULL`, per-masterclass |
| `r2ObjectKey` | `r2_object_key` | path completo del file con estensione (`.mp4`, `.zip`, …) |
| `attiva` | `attiva` | se `false` non è acquistabile e il relatore sparisce dal primo menu se non ne ha altre |
| `dataUpdate` | `data_update` | ultima scrittura della riga; ex `data_creazione` (`V18`) |

## La catena che porta al file giusto

Con N file su R2, non c'è nessuna ricerca: l'id viaggia immutabile nei metadata Stripe.

```
opzione del menu = masterclass_id → metadata della Checkout Session → webhook
    → findById → r2_object_key (un solo file) → presigned URL
```

L'id è impostato **lato server** nei metadata: l'utente non può alterarlo.

## Convenzione sulla object key

È consigliato includere una parte **non indovinabile** (UUID) nel nome del file, per esempio
`masterclass/relatore3/a1b2c3-uuid.zip`. È difesa in profondità: il bucket è già privato, ma una key
prevedibile faciliterebbe tentativi di enumerazione.

Prima di ogni checkout il sistema fa una **HEAD** su R2 per verificare che il file esista: se la key
è sbagliata, l'acquisto viene bloccato e gli admin notificati, così **nessuno paga a vuoto**.

## Limiti Discord da ricordare

I menu a tendina di Discord accettano al massimo **25 opzioni**: il codice tronca a 25 i relatori e
le masterclass, e a 24 nel menu con l'opzione aggiuntiva "Tutte". Oltre quel numero, gli elementi
in eccesso **non sono visibili** e non c'è paginazione.

## Voci correlate
- [[Relatore]]
- [[Pagamento masterclass]]
- [[Storage R2]]
- [[Sistema masterclass]]
