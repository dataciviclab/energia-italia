# terna-electrical-energy-by-sector

Consumi elettrici per settore economico e provincia (GWh).

## Domanda guida

Quanta elettricità consumano le famiglie, l'industria, i servizi e l'agricoltura in Italia? Come si distribuisce il consumo per provincia?

## Fonte

TERNA S.p.A. — Download Center
<https://dati.terna.it/download-center>

## Shape

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno di riferimento |
| `regione` | VARCHAR | Regione |
| `provincia` | VARCHAR | Provincia |
| `settore` | VARCHAR | Domestico, Industria, Servizi, Agricoltura |
| `consumo_gwh` | DOUBLE | Consumo in GWh |

## MART

`mart_consumi_settore_provincia`: consumi per anno, regione e settore.

Nota: gli anni early (2000-2020) arrivano raw disaggregati (fino a ~12k righe/anno) mentre 2021-2024 sono pre-aggregati (428 righe/anno). Il SUM nel mart normalizza — i totali sono comparabili tra tutti gli anni.

## Copertura

Serie **2000-2024** (estesa nel 2026-10-16; la fonte ha dati dal 2000). Prima era 2015-2024 con `pageSize=100` che troncava gli export a 100 righe (7 regioni, 25 province) — vedere `notes.md`.

## Setup

Il fetch usa `http_file` con `pageSize=500000` (la riga footer "Applied filters" viene filtrata dal `clean.sql`). `TOOLKIT_ALLOW_SCRIPT_SOURCE=1` non e' piu' necessario. Vedere `notes.md` per dettagli tecnici.
