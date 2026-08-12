---
tipo: modulo
titolo: Onboarding e disclaimer
alias: [ingresso nel server, censimento]
tag: [dominio/utenti]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Onboarding e disclaimer

Il percorso che porta un nuovo arrivato da "membro anonimo della guild" a [[Utente]] censito e
pagante.

## Sequenza completa

1. **L'utente entra** con un invito. Scattano **due** listener sullo stesso evento
   `onGuildMemberJoin`:
   - `InviteListener` confronta i contatori d'uso degli inviti per capire **quale invito** è stato
     usato;
   - `DisclaimerListener` **censisce l'utente** in `users` ([[Utente]]), assegna il ruolo **GUEST** e
     invia in DM il messaggio di benvenuto con i pulsanti dei comandi ([[Comandi utente]]).
2. **L'utente legge il disclaimer** nel canale dedicato e reagisce con ✅.
3. `DisclaimerListener.onMessageReactionAdd`:
   - crea o aggiorna la riga in [[Accettazione disclaimer]] con `accettato = true`;
   - **collega** l'accettazione all'utente (`users.disclaimer_id`), abilitandolo alle azioni;
   - se il referral non era ancora stato risolto, fa un ultimo tentativo di assegnarlo;
   - se l'utente non esistesse (membro entrato prima dell'introduzione del censimento all'ingresso),
     lo censisce comunque.
4. Da qui l'utente può usare tutti i comandi e pagare.

Il censimento **non dipende** dalla risoluzione dell'invito, che è asincrona: l'utente viene creato
subito e il referral arriva quando è disponibile. Ruolo GUEST e messaggio di benvenuto non sono più
subordinati all'esistenza del canale disclaimer (un canale mal configurato non impedisce l'accesso
base: viene solo loggato un errore).

## Il messaggio di benvenuto

Contiene cinque pulsanti: *Stato Disclaimer*, *Info Donazione*, *Verifica Transazione*, *Bacheca*,
*Verifica Scadenza*. Sono gli stessi che si riottengono con `!Comandi`.

## Se la reazione viene tolta

`onMessageReactionRemove` porta `accettato` a `false`. Tutti i flussi di pagamento tornano bloccati,
ma **l'utente non viene degradato**: ruoli e abbonamento restano quelli che erano.

## Punti fragili da conoscere

- Il contatore dell'invito può essere propagato da Discord **con un istante di ritardo** rispetto
  all'evento di ingresso: per questo, quando il primo confronto non trova differenze, si riprova
  automaticamente a **2, 5 e 15 secondi**.
- Se due utenti entrano nello stesso istante con inviti diversi, l'attribuzione resta **indecidibile**:
  finiscono in [[Referral pendente]] come `AMBIGUO`.
- Chi non viene attribuito è recuperabile con `!SyncReferral` ([[Comandi admin]]), perché i contatori
  non vengono riallineati sui fallimenti ([[Sistema referral e commissioni]]).
- Un utente che entra e **non accetta mai** il disclaimer ora **esiste** in `users`, con
  `abilitato = false`: può ricevere DM e usare `!Comandi`, ma ogni flusso di pagamento resta bloccato
  dal gate del disclaimer. La tabella cresce quindi con tutti i passanti — scelta deliberata, senza
  filtri.

## Voci correlate
- [[Utente]]
- [[Accettazione disclaimer]]
- [[Sistema referral e commissioni]]
- [[Bot Discord]]
