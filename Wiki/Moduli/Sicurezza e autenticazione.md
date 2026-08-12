---
tipo: modulo
titolo: Sicurezza e autenticazione
alias: [Spring Security, JWT, filtri]
tag: [dominio/sicurezza]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
stato: stabile
---

# Sicurezza e autenticazione

Come è protetta la superficie HTTP dell'applicazione — e quale parte della sicurezza è invece
delegata a Discord.

## La configurazione Spring Security

Sessioni **STATELESS**, nessun form di login. Le regole:

| Pattern | Regola |
|---|---|
| `/api/auth/**` | `permitAll` |
| ~~`/api/verifica-accesso/**`~~ | regola **rimossa** il 2026-08-12 insieme a `ApiKeyAuthFilter` ([[Integrazione VuTracker]]) |
| `/payment/**` | `permitAll` (pagine di ritorno Stripe) |
| `/api/webhooks/**` | `permitAll` (webhook Stripe) |
| `/css/**`, `/js/**` | `permitAll` |
| `/admin/**` | `hasRole("ADMIN")` |
| tutto il resto | `authenticated()` |

CSRF disabilitato su `/api/webhooks/**` e `/payment/**` — necessario, sono chiamate server-to-server.

## Chi protegge davvero i webhook

Non Spring Security, ma la **verifica della firma Stripe**: `Webhook.constructEvent(payload,
sigHeader, secret)`. Senza il webhook secret corretto nessun payload viene accettato, quindi non è
possibile falsificare un pagamento chiamando l'endpoint. Ogni account e ogni relatore ha il proprio
secret ([[Chiavi Stripe]]).

## L'autorizzazione applicativa vive su Discord

Le funzioni sensibili (report finanziari, prelievi) non sono su HTTP: sono comandi del bot. La loro
autorizzazione è `isAdmin(discordId)`, che verifica il **ruolo Discord** in tempo reale
([[Ruoli Discord]]). `/admin/**` con `hasRole("ADMIN")` esiste nella configurazione ma **nessun
controller** è mappato lì.

## ⚠️ Il flusso JWT non è attivo

Nel codice esistono `JwtService`, `JwtAuthFilter`, `CustomUserDetailsService`, un
`DaoAuthenticationProvider` con BCrypt e le variabili `JWT_SECRET` / `JWT_EXPIRATION`. Anche la
configurazione **OAuth2 Discord** è presente in `application.yml` (client id/secret, scope
`identify,email,guilds.join`, redirect URI).

Ma **il flusso non è usato**: nessun controller emette token, non esiste un endpoint di login né di
logout, non c'è blacklist di token né job di pulizia. Il filtro JWT è registrato nella catena e
lascia semplicemente passare le richieste senza token.

Se un giorno si attiva, il progetto ha già registrato cosa serve: blacklist, endpoint di logout, job
di pulizia dei token scaduti, e rigenerazione del JWT secret con un valore crittograficamente
casuale.

## Difese sui pagamenti

Sono la parte di sicurezza più curata:

- **importo bloccante** sul Supporter Member Stripe: pagato < atteso → accesso negato + notifica admin;
- **validazione dei mesi** (1-24): con `0` l'importo atteso si azzererebbe e qualunque pagamento
  passerebbe;
- **anti-replay crypto**: `tx_hash` `UNIQUE` più controllo applicativo;
- **rate limiting** sui tentativi di verifica ([[Tentativo di verifica transazione]]);
- **idempotenza** sui webhook ([[Idempotenza dei webhook]]);
- **400 invece di 500** sugli errori di configurazione, per non innescare i retry di Stripe.

Queste logiche sono coperte da test JUnit (`PagamentiValidatorTest`, `StripeAccountSelectorTest`,
`StripeAccountKeyProviderTest`, `PagamentiAbilitazioneServiceTest`, i test dei notification service).

## Altri accorgimenti

- La password del database passa a `mysqldump` via variabile d'ambiente, non da riga di comando
  ([[Backup del database]]).
- I presigned URL R2 non vengono mai loggati per intero ([[Storage R2]]).
- Swagger UI è **disabilitato** nel profilo `prod`.
- In `prod` il server ascolta su `127.0.0.1`: è raggiungibile solo tramite il proxy nginx.

## Voci correlate
- [[Integrazione VuTracker]]
- [[Endpoint REST]]
- [[Idempotenza dei webhook]]
- [[Variabili d'ambiente]]
