# terna-load-oraria — Note

## Fonte

Terna Download Center, dataset `TotalLoad` e `MarketLoad` (CSV).

- **TotalLoad**: domanda elettrica totale (lordo, ogni 15 minuti)
- **MarketLoad**: domanda servita dal mercato
- La differenza (`total − market`) quantifica la domanda **fuori mercato**
  (autoconsumo/auto-produzione), ~31-33 TWh/anno
- Anni: **2019-2025** (2018 e prima vuoti; 2026 escluso perché parziale)
- Zone di mercato: `North`, `Centre-North`, `Centre-South`, `South`,
  `Sicily`, `Sardinia`, `Calabria` + `Italy` (aggregato nazionale)

## Due serie, disponibilità diversa

Le due serie sono distinte dal campo iniettato `tipo_carico` (`total` / `market`):

| Serie | Da | Note |
|---|---|---|
| `total` (TotalLoad) | 2019 | serie completa 2019-2025 |
| `market` (MarketLoad) | **2021** | 2019-2020: file **header-only** (61 byte, nessun dato) |

Per questo 2019-2020 hanno la sola serie `total` (~245k righe) e 2021+ hanno
entrambe (~560k righe).

## ⚠️ Quirk del CSV

Come per `terna-generation-oraria`, la virgola è **sia delimitatore sia
separatore decimale**. Ma qui ogni riga ha **7 campi** (due coppie int+dec):

```
Date,Total Load [MW],Forecast Total Load [MW],Bidding Zone
2024-12-31T23:45:00,12765,710000,13062,227000,North,
                     └12.765,710 MW┘ └13.062,227 MW┘
```

Il clean legge tutto come **VARCHAR** e ricompone `parte_intera || '.' || parte_decimale`.
Gli **zeri iniziali sono significativi** (leggere la parte decimale come numero
la corromperebbe di 10×).

### File header-only (2019-2020)

I file `MarketLoad` 2019-2020 contengono **solo l'header**: il sniffing di
DuckDB fallisce su un CSV senza righe dati. Soluzione nel config:

```yaml
clean:
  read:
    mode: all            # due sorgenti per anno, non solo la più recente
    auto_detect: false   # niente sniffing
    delim: ","           # delimitatore esplicito
    header: false
    skip: 1              # salta la riga di header
```

## Righe e zone per anno (sanity)

| Anno | Righe clean | Zone | Serie | Note |
|---|---:|---:|---|---|
| 2019 | 245.224 | 7 | total | 7×35.032; ~2 h di gap dati |
| 2020 | 245.952 | 7 | total | 7×35.136 = 366×96 (bisestile) ✅ |
| 2021 | 560.638 | 8 | total+market | **Calabria** entra come zona |
| 2022 | 560.640 | 8 | total+market | 16×35.040 = 365×96 ✅ |
| 2023 | 560.640 | 8 | total+market | ✅ |
| 2024 | 562.176 | 8 | total+market | 16×35.136 = 366×96 (bisestile) ✅ |
| 2025 | 560.640 | 8 | total+market | ✅ |

La zona `Calabria` esiste **solo dal 2021**: nei mart per zona i confronti
2019-2020 vs 2021+ non sono omogenei (6 zone vs 7, esclusa `Italy`).

Passo di campionamento: **15 minuti** (`passo_ore = 0.25`) su tutti gli anni,
calcolato come **moda dei delta** per anno×serie×zona (non assunto).

## Cross-check unità e integrazione

L'unità è **MW** (valori in `carico_mw`). L'energia annua `total` ricostruita
(`Σ carico_mw × passo_ore`) coincide con la **richiesta** del dataset
`terna-bilancio-elettrico`:

| Anno | Total load (TWh) | Bilancio richiesta (TWh) | Diff |
|---|---:|---:|---:|
| 2022 | 315,06 | 315,01 | +0,02% ✅ |
| 2023 | 306,00 | 305,62 | +0,12% ✅ |

Conferma sia l'unità sia l'integrazione a 15 minuti.

## Mart

- `mart_carico_annuale`: energia, media/picco/min e accuratezza previsione Terna
- `mart_carico_mensile`: energia mensile (stagionalità)
- `mart_profilo_carico`: profilo medio per ora del giorno (pesi uniformi:
  media per giorno prima di mediare sulle ore)
- `mart_carico_zona`: energia per zona di mercato (esclude `Italy`)
- `mart_ore_alta_domanda`: ore equivalenti sopra 40/45/50/55 GW

I mart nazionali filtrano `zona = 'Italy'` (aggregato), così non sommano le
zone due volte.

Tutti i mart espongono la colonna `anno` (anche quelli per-anno, dove è
costante): senza di essa, un mart per-anno letto via il glob del registry
unisce gli anni senza modo di distinguerli.

## Dipendenza toolkit (bug `inject_column`)

Il dataset usa `inject_column` a livello di `raw.sources[]` per etichettare la
serie (`tipo_carico`). La validazione di promozione del toolkit riusava
`read_params_used` (incluso `inject_column`, metadato di audit) come config di
lettura → `ValueError: Unsupported clean.read options ... ['inject_column']`.

Fix: `toolkit/clean/validate.py` filtra `read_params_used` alle sole chiavi di
lettura (`ALLOWED_READ_CSV_KEYS`) — branch `fix/validate-read-params-filter`.
Sblocca qualsiasi dataset multi-source con `inject_column`.
