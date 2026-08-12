---
tipo: modulo
titolo: Sistema masterclass
alias: [masterclass, vendita video]
tag: [dominio/masterclass]
fonti: [Codice Discord-access-app, Piano sviluppo masterclass]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Sistema masterclass

La vendita di contenuti video dei [[Relatore|relatori]] direttamente su Discord: pagamento con
Stripe, contenuto su [[Storage R2]], erogazione con link firmato a scadenza inviato in DM.

## Il modello attivo: "chiave per relatore"

Ogni relatore usa **il proprio account Stripe**. Il bot crea il checkout con la **secret key del
relatore**, senza `stripeAccount` e senza `applicationFee`: l'incasso è **tutto suo** e il server
non trattiene nulla realmente ([[Pagamento masterclass]]).

La scelta è stata fatta per **non costituire una piattaforma Stripe Connect** e la relativa
KYC/onboarding (fonte: [[Piano sviluppo masterclass]] §13).

Il modello **Connect** resta implementato e funzionante, selezionabile con la property
`masterclass.payment.mode=connect`; il default è `direct`. La selezione avviene tramite
`MasterclassChargeStrategyResolver`, che in ricezione webhook è invece implicita nell'endpoint
chiamato.

## Il flusso di acquisto

```
!masterclass
  └─ menu relatori (solo attivi con almeno una masterclass attiva)
       └─ menu masterclass attive del relatore (titolo + prezzo)
            └─ embed di dettaglio + pulsante [🛒 Acquista]
                 └─ CONTROLLI PRE-CHECKOUT
                      1. masterclass riletta dal DB e ancora attiva
                      2. acquirente censito in users
                      3. non già acquistata (stato COMPLETED)
                      4. file presente su R2 (HEAD)  ← nessuno paga a vuoto
                 └─ Checkout Session (2 ore) → link in risposta effimera
```

Se la creazione della sessione fallisce (chiavi mancanti, account non abilitato) l'utente riceve
«momentaneamente non disponibile» e gli admin una notifica col dettaglio.

## Il flusso post-pagamento

Webhook `POST /api/webhooks/stripe/masterclass/relatore/{relatoreId}` — un endpoint **per
relatore**, perché ogni relatore ha un webhook secret diverso ([[Relatore]]).

1. verifica della firma col secret di quel relatore;
2. idempotenza su `stripe_session_id`;
3. calcolo degli importi (quota server teorica, fee, netto) → [[Riconciliazione della fee Stripe]];
4. salvataggio del [[Pagamento masterclass]] — se scatta il vincolo di doppio acquisto, **niente
   erogazione** e notifica agli admin che invita a valutare il rimborso;
5. **erogazione**: presigned URL R2 di durata `MASTERCLASS_DURATA_LINK_ORE` (default 3h) e DM
   all'acquirente. Questo passo **non dipende dalla fee**;
6. DM al relatore e notifica agli admin. Un errore qui viene loggato ma non blocca l'erogazione.

## Il modello Connect, per confronto

| Aspetto | direct (attivo) | connect (congelato) |
|---|---|---|
| Chiave usata | del relatore | della piattaforma + `Stripe-Account` |
| `relatori.stripe_account_id` | `NULL` | `acct_xxx` obbligatorio |
| Application fee | assente | pari alla quota server, accreditata alla piattaforma |
| Webhook | uno per relatore | uno solo, di tipo Connect |
| Quota server | teorica | **realmente incassata** |

## Limiti noti e accettati

- **Rimborsi e dispute**: nessuna gestione automatica. Gli eventi `charge.refunded` e
  `charge.dispute.created` non sono nemmeno ascoltati: il video resta erogato, la policy è manuale.
- **Link perso**: nessuna rigenerazione self-service, serve un admin.
- **Ri-condivisione**: nella finestra di validità il link è tecnicamente condivisibile. Rischio
  accettato, mitigato da durata breve + object key non indovinabile + DM privato.
- **Nessun comando di gestione**: relatori e masterclass si inseriscono via SQL.

## Voci correlate
- [[Masterclass]]
- [[Relatore]]
- [[Storage R2]]
- [[Comandi relatori]]
