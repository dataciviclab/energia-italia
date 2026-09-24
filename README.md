# Energia Italia

Come sta cambiando il sistema elettrico italiano — produzione, prezzi, emissioni, confronti EU. Dati aperti da Terna e GME.

## Perché questi dati

L'Italia sta attraversando una transizione energetica veloce: il fotovoltaico è raddoppiato in 2 anni, il termoelettrico perde terreno, i prezzi seguono il mix. Questi dati permettono dimonitorare la transizione con evidenze, non con opinioni.

**Numeri chiave (2015-2024):**
- FV installato: 19 GW → 37 GW (+96%)
- Quota rinnovabili: 33.5% → 39.9%
- Termoelettrico: 51.4% → 44.6%
- Intensità carbone: 305 → 257 g CO2/kWh

## Cosa contengono

| Dataset | Periodo | Righe | Copertura |
|---------|---------|-------|-----------|
| `terna-capacita-rinnovabile` | 2015-2024 | ~1.100/anno | MW per regione, fonte |
| `terna-elettricita-per-fonte` | 2015-2024 | ~850/anno | GWh per regione, provincia, fonte |
| `terna-copertura-domanda` | 2015-2024 | ~180/anno | Copertura domanda per fonte |
| `terna-elettricita-per-settore` | 2015-2024 | ~100/anno | Consumi per settore, provincia |
| `terna-emissioni-co2` | 2015-2024 | ~100/anno | CO2 per combustibile, regione |
| `terna-bilancio-elettrico` | 2022-2023 | 9 paesi | Confronti EU |
| `gme-pun-storico` | 2020-2026 | 78 | PUN/PSV mensili |

## Esempi di domande

1. Quanto contribuisce il fotovoltaico alla copertura della domanda italiana?
2. Come si muovono i prezzi PUN in relazione alla quota rinnovabili?
3. Quali regioni hanno la più alta intensità di carbonio?
4. Come performa l'Italia rispetto a Germania e Francia in termini di emissioni?
5. Qual è l'andamento delle emissioni CO2 per combustibile?

## Come accedere

### Dashboard interattiva

```bash
cd dashboard && streamlit run app.py
```

### Dati locali (parquet)

I dati puliti sono in `out/data/clean/` e `out/data/mart/`:

```python
import duckdb
con = duckdb.connect()
df = con.sql("SELECT * FROM read_parquet('out/data/clean/terna_copertura_domanda/2024/*.parquet')").df()
```

### Query SQL

```bash
make run-all          # esegui tutti i dataset
make reconcile        # cross-check tra fonti
```

## Dashboard

6 pagine Streamlit:
- **Panoramica** — KPI principali + trend rinnovabili
- **Mix Energetico** — stacked bar + dettaglio regionale
- **Prezzi** — PUN/PSV mensili e annuale
- **Emissioni** — CO2 per combustibile e regione
- **Confronti EU** — intensità carbone Italia vs Europa
- **Query SQL** — interrogazione libera

## Struttura

```
energia-italia/
├── datasets/           # Config e SQL per ogni dataset
├── dashboard/          # Streamlit dashboard
├── tests/              # Test
├── registry/           # Registry dataset
└── out/                # Output pipeline (raw, clean, mart)
```

## Partecipa

- [Discussions](https://github.com/orgs/dataciviclab/discussions) — domande, idee, feedback
- [Issues](https://github.com/dataciviclab/energia-italia/issues) — bug, dataset mancanti, miglioramenti
- Contribuire: vedi `CONTRIBUTING.md`

## Licenza

[![MIT License](https://img.shields.io/badge/Licenza-MIT-green.svg)](LICENSE)
