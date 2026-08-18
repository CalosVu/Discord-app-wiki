---
tipo: entita
titolo: Configurazione di server
alias: [server_config, ServerConfig, parametro runtime]
tag: [dominio/configurazione]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-08-17
stato: stabile
---

# Configurazione di server

Un parametro di comportamento dell'applicazione, modificabile **a runtime dal database** senza
ricompilare né riavviare. Tabella `cfg_server`, entità `ServerConfig`.

Per l'elenco completo dei parametri esistenti e dei loro valori vedi [[Tabella cfg_server]];
questa pagina descrive **il meccanismo**.

## Struttura

Tre colonne significative, chiave/valore in forma testuale:

| Colonna | Tipo | Note |
|---|---|---|
| `nome_configurazione` | `VARCHAR(150)` | la chiave. ⚠️ **nessun vincolo `UNIQUE`** |
| `valore_configurazione` | `VARCHAR(150)` | sempre stringa: la conversione avviene nel codice |
| `descrizione` | `VARCHAR(500)` | spiegazione a uso umano |

## Come si legge

Unico punto di accesso, `LoadConfigurationService.getConfigurationValue`, con due argomenti: nome e
funzione di conversione.

```java
int ore = loadConfigurationService.getConfigurationValue(
        "MASTERCLASS_DURATA_LINK_ORE", Integer::parseInt);
```

**Non esiste un valore di ripiego.** Se la chiave manca, il metodo solleva — ma in pratica non ci si
arriva: `ConfigurazioneObbligatoria` verifica tutte le chiavi all'avvio e fa **fallire il boot** se
ne manca una, e una chiave esterna ne impedisce la cancellazione ([[Tabella cfg_server]]).

> [!warning] Come funzionava prima, e perché è stato cambiato
> Fino ad agosto 2026 il metodo accettava un terzo parametro con il valore da usare in assenza della
> riga. Sembrava prudente, ma produceva il caso peggiore: l'applicazione partiva e si comportava
> **diversamente** da come era configurata, senza errore né log.
>
> Sui flag booleani il ripiego era `true`, quindi cancellare una riga **riapriva** i pagamenti
> anziché chiuderli. E su `VERIFICA_CRYPTO_FINESTRA_ORE` il ripiego `0` **spegneva** il controllo
> temporale sulle transazioni crypto — cioè una protezione, in silenzio.

## Nessuna cache

Ogni lettura è una query. I cambi di valore hanno effetto **immediato** sull'operazione successiva,
senza riavvio: è il pregio principale del meccanismo. Il costo è una query per ogni lettura, che a
questi volumi è irrilevante.

## La chiave è unica

`nome_configurazione` ha il vincolo `UNIQUE` da `V4`: un doppio inserimento viene rifiutato dal
database. Serve, perché `findByNomeConfigurazione` restituisce un `Optional` e con due righe Spring
Data solleverebbe un'eccezione sulla dimensione del risultato.

È anche il presupposto della chiave esterna di `cfg_server_obbligatorie`, che referenzia proprio
questa colonna: senza unicità non sarebbe stata possibile ([[Tabella cfg_server]]).

## Voci correlate
- [[Tabella cfg_server]]
- [[Blocco dei pagamenti]]
- [[Schema del database]]
