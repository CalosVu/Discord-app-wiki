---
tipo: modulo
titolo: Architettura dei moduli Maven
alias: [moduli Maven, struttura del progetto]
tag: [dominio/architettura]
fonti: [Codice Discord-access-app, DOC_PROGETTO]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Architettura dei moduli Maven

Il progetto è un multi-modulo Maven con cinque moduli e una gerarchia di dipendenze a strati.

## I cinque moduli

| Modulo | Contenuto | File `.java` |
|---|---|---|
| `discord-access-api` | entry point `MainApplication`, controller REST, classi `@Configuration`, risorse (`application*.yml`, static) | 10 |
| `discord-access-service` | logica di business: bot, listener, pagamenti, batch, storage, report | 49 |
| `discord-access-persistence` | entità JPA e repository Spring Data | 33 |
| `discord-access-security` | Spring Security, JWT, filtri | 6 |
| `discord-access-common` | DTO, costanti, enum, utility, eccezioni | 28 |

Dipendenze: `api` → `service` → `persistence` → `common`; `security` → `service` + `persistence`.

## Il JAR eseguibile

È quello di `discord-access-api`. Il deploy lo rinomina in `app.jar` sul server
([[Deploy e CI-CD]]).

## Dove stanno davvero le cose

La collocazione non sempre segue il nome del modulo — utile saperlo quando si cerca un file:

- `SecurityConfig` sta in **security**, non in `api` come le altre `@Configuration`;
- `StripeConfig`, `MasterclassStripeConfig`, `R2Config`, `Web3jConfig`, `BackupConfiguration` stanno
  in **service**, mentre `DiscordConfig`, `WebMvcConfig`, `OpenApiConfig`, `RestTemplateConfig` stanno
  in **api**;
- il package è **sempre** `discord.access.app.*`, identico in tutti i moduli: due file con lo stesso
  package possono stare in moduli diversi.

## Duplicazione da conoscere

Esiste **due volte** un file `service/IUserService.java`, in due moduli distinti. Va verificato quale
sia effettivamente sul classpath prima di modificarlo.

Il metodo `getPromoAttiva` è **replicato in tre classi** ([[Promozioni temporali]]).

## Code generation e librerie

Lombok (`@Data`, `@Builder`, `@RequiredArgsConstructor`, `@Slf4j`) e MapStruct 1.6.3 sono usati in
tutto il progetto. Le classi non hanno quindi getter/setter espliciti: sono generati in compilazione.

Librerie esterne principali: JDA 5.5.1 (Discord), Stripe SDK 29.4.0, Web3j 5.0.0 (Arbitrum), AWS SDK
v2 S3 (R2), Apache Commons Lang3 (`Pair`), SpringDoc OpenAPI.

## Convenzione linguistica

Nomi di classi, metodi e commenti sono **in italiano** (`CryptoPaymentService.avviaVerifica…`,
`PrelieviService.salvaPrelievo`), mescolati a termini tecnici inglesi. Anche i messaggi di log e
quelli verso gli utenti sono in italiano.

## Voci correlate
- [[Codice Discord-access-app]]
- [[Deploy e CI-CD]]
- [[Ambienti e profili Spring]]
