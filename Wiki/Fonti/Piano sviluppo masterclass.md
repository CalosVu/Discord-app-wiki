---
tipo: fonte
titolo: Piano sviluppo masterclass
alias: [PianoSviluppoMasterclass]
tag: [fonte/documento, dominio/masterclass]
fonti: []
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Piano sviluppo masterclass

Documento di architettura e decisioni del [[Sistema masterclass]]. **Fonte di rango 3**: è la sola
fonte che spiega il *perché* delle scelte, ma descrive anche il modello Connect oggi **congelato**.

## Identificazione

- **Percorso:** `${DISCORD_APP_DOCS}/PianoSviluppoMasterclass.md` (~52 KB, 13 capitoli)
- **Data:** giugno 2026, con §13 aggiunta il 2026-06-13
- **Stato dichiarato:** fasi 1-7 implementate e testate end-to-end in locale

## Decisioni che valgono ancora

| # | Decisione | Dove è realizzata |
|---|---|---|
| 1 | **Modello attivo: "chiave per relatore"** (§13), NO Stripe Connect | [[Sistema masterclass]], `DirectKeyChargeStrategy` |
| 2 | Erogazione via **presigned URL a scadenza** su R2, nessun DRM | [[Storage R2]] |
| 3 | Reportistica **self-service relatore** + **vista admin** | [[Comandi relatori]], [[Comandi admin]] |
| 4 | Accesso **una-tantum**: link solo al pagamento, link perso = intervento admin | [[Sistema masterclass]] |
| 5 | `relatori` e `masterclass` popolate **a mano via SQL**, nessun comando di gestione | [[Relatore]], [[Masterclass]] |
| 6 | **Doppio acquisto bloccato** (check `COMPLETED` su `user_id + masterclass_id`) | [[Pagamento masterclass]] |
| 7 | Durata del link **globale** da `server_config`, default 3h | [[Tabella server_config]] |
| 8 | Valuta: **solo EUR**; un solo **bucket privato** per tutti i relatori | [[Storage R2]] |
| 9 | Rimborsi e dispute: **gestione solo manuale** in v1 | [[Sistema masterclass]] |

## Perché si è abbandonato Stripe Connect (§13.1)

Per **non costituire una piattaforma Connect** e la relativa KYC/onboarding. Ogni relatore usa il
proprio account Stripe: il bot crea il checkout con la **chiave del relatore**, l'incasso è tutto
suo e **nessuna commissione viene realmente trattenuta**. Conseguenza contabile importante: i campi
`commissioni_server` e `importo_netto_relatore` restano calcolati ma sono **valori teorici** — il
relatore incassa davvero `lordo − stripe_fee`. Vedi [[Pagamento masterclass]].

Il codice Connect **resta in piedi e funzionante** (`ConnectChargeStrategy`), selezionabile con la
property `masterclass.payment.mode=connect`.

## Sezioni ancora descrittive del modello Connect (§6)

I capitoli §4.1 (`stripe_account_id` NOT NULL), §6 (destination charge, `application_fee`), §6.2
(onboarding Express, capability `card_payments`/`transfers`) descrivono il modello **congelato**.
Nel modello attivo `relatori.stripe_account_id` è **NULL** e non esiste application fee.

## Rischio residuo accettato (§9.3)

Nella finestra di validità del link (default 3h) il presigned URL **è condivisibile** e il file
scaricabile. Mitigazioni adottate: durata breve, object key non indovinabile (UUID), DM privato.
Evoluzioni valutate e non fatte: watermark per-utente, streaming proxy con token monouso,
Cloudflare Stream.

## Voci correlate
- [[Fonti]]
- [[Sistema masterclass]]
- [[Piano sviluppo doppio Stripe]]
