# irena-costi-tecnologia — Note

## Fonte

IRENA, *Renewable Power Generation Costs in 2024* (datafile, luglio 2025) — stesso
file di `irena-lcoe`, foglio **`Table S.1`** (indice 2).

- Capex (2024 USD/kW), capacity factor (%) e LCOE (2024 USD/kWh) per tecnologia
- Confronto **2010 vs 2024** (il CF riporta 2010 vs **2023**, come da fonte)
- 7 tecnologie: Bioenergy, Geothermal, Hydropower, Solar PV, CSP, Onshore wind,
  Offshore wind

## Quirks del foglio

- Header a r6, dati da r7 → `skip: 6` + `header: false`
- I numeri grandi usano lo **spazio come separatore delle migliaia** (`3 082`) →
  `replace(' ', '')` prima del cast
- Le variazioni percentuali sono **frazioni** (`0.05` = 5%) → `* 100` in clean
- Le colonne col0 e col11-13 sono vuote

## Mart

`mart_costi_tecnologia` (7 righe, PK tecnologia):
capex 2010/2024 + variazione, CF 2010/2023 + variazione, LCOE 2010/2024 +
variazione, `capex_per_mw_2024_usd`, `mwh_per_mw_anno` (CF × 8760).

## Caveat

- Valori **globali pesati**, non Italia-specifici
- Un file per release (aggiornamento annuale)
- `lcoe_var_pct` può differire di 1-2 punti dal report per arrotondamento

## Uso

Incrociato con `mart_lcoe_tecnologia` (serie annuale) e con
`mart_capacity_factor` del compose `energia-incroci` (CF reali italiani) per
leggere il divario tra benchmark globale e parco italiano.
