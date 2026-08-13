---
tipo: entita
titolo: Configurazione di server
alias: [server_config, ServerConfig, parametro runtime]
tag: [dominio/configurazione]
fonti: [Codice Discord-access-app]
creato: 2026-07-25
aggiornato: 2026-07-25
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

Unico punto di accesso, `LoadConfigurationService.getConfigurationValue`, con tre argomenti: nome,
funzione di conversione, valore di default.

```java
int ore = loadConfigurationService.getConfigurationValue(
        "MASTERCLASS_DURATA_LINK_ORE", Integer::parseInt, 3);
```

Il valore di default nel codice è **l'ultima rete di sicurezza**: se la riga manca nel DB
l'applicazione continua a funzionare. Ne segue una proprietà importante: **una riga assente non
disabilita nulla**, applica il default. Per i flag booleani il default è `true`, quindi cancellare
la riga **riapre** i pagamenti anziché chiuderli ([[Blocco dei pagamenti]]).

## Nessuna cache

Ogni lettura è una query. I cambi di valore hanno effetto **immediato** sull'operazione successiva,
senza riavvio: è il pregio principale del meccanismo. Il costo è una query per ogni lettura, che a
questi volumi è irrilevante.

## ⚠️ Chiave non unica

Senza vincolo `UNIQUE` su `nome_configurazione`, un doppio inserimento della stessa chiave non dà
errore: `findByNomeConfigurazione` restituisce un `Optional` e Spring Data solleva un'eccezione se
i risultati sono più di uno. Prima di un `INSERT` in produzione conviene sempre verificare che la
chiave non esista già.

## Voci correlate
- [[Tabella cfg_server]]
- [[Blocco dei pagamenti]]
- [[Schema del database]]
