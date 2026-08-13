---
tipo: modulo
titolo: Comandi agenti
alias: [mieiref, report agente]
tag: [dominio/bot, dominio/comandi, dominio/referral]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Comandi agenti

Un solo comando, `!mieiref`, riservato a chi è censito nella tabella `referral_agenti` ([[Agente]]).

## Chi può usarlo

Il riconoscimento è `agentiService.findByDiscordId(user.getId())`: se l'utente non è in tabella
riceve un embed «Accesso Negato — Non risulti registrato come agente». Non c'entra il ruolo Discord:
essere admin **non** dà accesso a `!mieiref` come agente.

## Cosa mostra

Il messaggio iniziale contiene tre cose:

1. la **percentuale di commissione** dell'agente;
2. l'elenco dei suoi **link referral attivi**, in forma `https://discord.gg/<codice>`;
3. un menu per scegliere il periodo: **mese corrente** o **mese precedente**.

## Quali link vengono mostrati

Doppio filtro:

- **quali codici considerare** — se `codici_ref_validi` è valorizzato si usano solo quelli;
  altrimenti tutti i [[Referral agent]] creati da quel Discord ID;
- **quali sono ancora vivi** — l'elenco viene incrociato con gli inviti **realmente attivi sulla
  guild**, recuperati da Discord in quel momento.

Un invito scaduto o revocato sparisce automaticamente. Se non ne resta nessuno:
«_nessun invito attivo_».

## Il report

Scelto il periodo, arrivano **due embed separati** in DM:

| Embed | Metodo | Valuta | Colore |
|---|---|---|---|
| 💳 Report Commissioni STRIPE | `STRIPE` | EUR | blu |
| 🪙 Report Commissioni CRYPTO | `CRYPTO` | USD | arancione |

Ogni riga: username dell'utente pagante, importo del pagamento, percentuale applicata e commissione
calcolata. In fondo: numero di pagamenti e totale commissioni.

Le due valute **non vengono sommate**: non esiste un totale unico, perché non c'è conversione.

## Cosa il report non dice

- **Non indica se la commissione è stata pagata**: il sistema traccia il maturato, non il liquidato.
  Il pagamento agli agenti avviene fuori dall'applicazione (eventualmente registrato come
  [[Prelievo]]).
- **Gli importi possono cambiare** fra due letture dello stesso mese: la commissione si ricalcola
  sull'importo del pagamento, che può essere stato riconciliato da lordo a netto nel frattempo
  ([[Riconciliazione della fee Stripe]]).

## La vista admin

Un admin ottiene lo stesso identico report dal menu `!Admin` → *Report Agente*, con un'intestazione
in più. Gli embed sono prodotti dalla stessa funzione: le due viste non possono divergere.

## Voci correlate
- [[Agente]]
- [[Commissione pagamento]]
- [[Sistema referral e commissioni]]
- [[Comandi admin]]
