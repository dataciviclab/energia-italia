# Italian Energy Intelligence

Analisi del sistema elettrico italiano: produzione, mix energetico, prezzi, emissioni e confronti EU.

## Storia che raccontiamo

Come sta cambiando il sistema elettrico italiano — dal termoelettrico alle rinnovabili, dai prezzi alle emissioni.

**Trend chiave (2015-2024):**
- FV installato: 19 GW → 37 GW (+96%)
- Quota rinnovabili: 33.5% → 39.9%
- Termoelettrico: 51.4% → 44.6% della copertura
- Intensità carbone: 305 → 257 g CO2/kWh

## Dataset

### Produzione e Mix

| Dataset | Fonte | Periodo | Granularità |
|---------|-------|---------|-------------|
| `terna-capacita-rinnovabile` | Terna Download Center | 2015-2024 | Regione, fonte, anno |
| `terna-elettricita-per-fonte` | Terna Download Center | 2015-2024 | Regione, provincia, fonte |
| `terna-copertura-domanda` | Terna Download Center | 2015-2024 | Fonte, regione |
| `terna-consumo-per-fonte` | Terna Download Center | 2015-2024 | Fonte, regione |

### Consumi

| Dataset | Fonte | Periodo | Granolarità |
|---------|-------|---------|-------------|
| `terna-elettricita-per-settore` | Terna Download Center | 2015-2024 | Settore, provincia |

### Prezzi

| Dataset | Fonte | Periodo | Granolarità |
|---------|-------|---------|-------------|
| `gme-pun-storico` | Portale Offerte | 2020-2026 | Mensile (PUN, PSV, PE) |

### Emissioni

| Dataset | Fonte | Periodo | Granolarità |
|---------|-------|---------|-------------|
| `terna-emissioni-co2` | Terna Download Center | 2015-2024 | Combustibile, regione |
| `ispra-emissioni-ghg` | ISPRA | 1990-2023 | Settore, nazionale |
| `eurostat-emissioni-ghg` | Eurostat SDMX | 2008-2023 | NACE, paese EU |

### Confronti EU

| Dataset | Fonte | Periodo | Granolarità |
|---------|-------|---------|-------------|
| `terna-bilancio-elettrico` | Terna Download Center | 2022-2023 | Paese EU |
| `eurostat-rinnovabili` | Eurostat SDMX | 2004-2025 | Paese EU, % target |

### Policy (laterale)

| Dataset | Fonte | Periodo |
|---------|-------|---------|
| `istat-subsidi-ambientali` | ISTAT | 1995-2023 |
| `istat-investimenti-mitigazione` | ISTAT | 2016-2023 |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Uso

```bash
# Esegui tutti i dataset
make run-all

# Esegui un singolo dataset
toolkit run --config datasets/terna-copertura-domanda/dataset.yml

# Aggiorna registry
make registry-write

# Esegui reconcile (cross-check fonti)
python3 scripts/reconcile.py
```

## Struttura

```
energia-italia/
├── datasets/           # Config e SQL per ogni dataset
│   ├── terna-*/        # Dati Terna (Download Center)
│   ├── gme-*/          # Dati GME (Portale Offerte)
│   ├── eurostat-*/     # Dati Eurostat (SDMX)
│   ├── ispra-*/        # Dati ISPRA
│   └── istat-*/        # Dati ISTAT
├── data/               # Reconcile output
├── dashboard/          # Streamlit dashboard
├── scripts/            # reconcile.py, signals.py
├── tests/              # Test
├── registry/           # Registry dataset
└── out/                # Output pipeline (raw, clean, mart)
```

## Reconcile

Cross-check automatico tra fonti indipendenti:
- ISPRA vs Eurostat (emissioni GHG)
- Terna capacity vs produzione (capacity factor)
- Terna emissioni CO2 vs ISPRA (termoelettrico vs processi energetici)
- GME PUN (profilo annuale)

## Licenza

CC BY 4.0
