---
tipo: entita
titolo: Catalogo servizi
alias: [catalogo_servizi, CatalogoServizi, piani]
tag: [dominio/prezzi]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Catalogo servizi

Il listino: definisce **prezzo, durata e ruolo** di ogni piano di abbonamento, e ospita anche le
[[Promozioni temporali]]. Tabella `catalogo_servizi`, entità `CatalogoServizi`.

## Le tre righe che esistono

Dai dati iniziali del repo (`sql/insert.sql`):

| `nome_servizio` | Prezzo EUR | Prezzo USD | Mesi | Durata giorni | Uso |
|---|---|---|---|---|---|
| `BASIC` | 40,00 | 45,00 | — | 30 | piano standard di ogni nuovo iscritto |
| `PIONIERE` | 30,00 | 35,00 | — | 30 | piano agevolato dei [[Membri pionieri]] |
| `PROMO` | 130,00 | 149,00 | 4 | 0 | promozione a tempo, prezzo **totale** per 4 mesi |

`prezzo_eur` è usato dal canale Stripe, `prezzo_usd` dal canale crypto: sono **due listini
distinti**, non una conversione.

## Campi

| Campo | Note |
|---|---|
| `nomeServizio` | discrimina il tipo di riga: `BASIC`, `PIONIERE`, `PROMO` |
| `prezzoEur` / `prezzoUsd` | per i piani è il prezzo **mensile**; per le promo è il **totale** del periodo |
| `numeroMesi` | valorizzato solo sulle promo: mesi forzati dell'offerta |
| `durataGiorniAbbonamento` | giorni aggiunti alla scadenza per ogni mese pagato (30). Sulle promo è `0` |
| `dataInizio` / `dataFine` | finestra di validità, solo per le promo |
| `ruoloDiscord` | ruolo assegnato: `SUPPORTER_MEMBER` |
| `attivo` | selettore usato dalle query; il batch disattiva le promo scadute |
| `referral` | se valorizzato, la promo vale **solo** per chi è entrato con quel [[Referral agent]] |
| `rinnovo` | se `false`, la promo non si applica a chi sta rinnovando |

## Come viene scelto il prezzo

- L'utente ha sempre un `pianoApplicato` (BASIC o PIONIERE) salvato sull'[[Utente]].
- Nel canale **Stripe** il prezzo arriva da `utente.pianoApplicato.prezzoEur`, moltiplicato per i
  mesi scelti.
- Nel canale **crypto** il prezzo è riletto dal catalogo in base a `membroPioniere`:
  `PIONIERE` se vero, `BASIC` altrimenti — **non** dal `pianoApplicato`.
- Se esiste una promo valida, essa **sovrascrive** prezzo e numero di mesi ([[Promozioni temporali]]).

## Trappola: due sorgenti per lo stesso prezzo

Stripe legge `pianoApplicato`, crypto rilegge il catalogo da `membroPioniere`. Se i due campi
divergono su un utente (per esempio pioniere con piano BASIC), lo **stesso utente paga prezzi
diversi** a seconda del canale. Va tenuto presente in ogni modifica ai prezzi.

## Voci correlate
- [[Promozioni temporali]]
- [[Membri pionieri]]
- [[Abbonamento Supporter Member]]
