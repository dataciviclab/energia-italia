# irena-lcoe — Note

## Fonte

IRENA, *Renewable Power Generation Costs in 2024* (datafile, luglio 2025).

- URL: `https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2025/Jul/IRENA-Datafile-RenPwrGenCosts-in-2024.xlsx`
- XLSX ~12,7 MB, ~130 fogli (tabelle e figure del report)
- Licenza IRENA con attribuzione

## Cosa estraiamo

Solo il foglio **`Fig 1.2 `** (attenzione: spazio finale nel nome):
LCOE globale pesato per tecnologia, 2010-2024, in **2024 USD/kWh**.

- 7 tecnologie: Bioenergy, Geothermal, Hydro, Offshore wind, Onshore wind,
  Solar photovoltaic, Solar thermal
- 104 righe clean (7 × 15 anni, meno Geothermal 2011 assente nella fonte)

## Quirks del file (per chi tocca il clean)

- Il foglio ha **spazio finale** nel nome: il reader lo strippa → selezione per
  **indice posizionale** (`sheet_name: 13`) invece che per nome
- Layout: titolo r1-r3, header r5, dati da r6; col1 = tecnologia, col2..col16 =
  anni 2010..2024 → lettura `skip: 5` + `header: false` e unpivot
- L'unpivot cambia colonne e righe per costruzione: `transition.warn_removed_columns: false`

## Caveat

- **LCOE globale/regionale**, non specifico per impianto italiano: il confronto
  con l'Italia è indicativo
- Un file per release (aggiornamento annuale), non una serie continua
- `years: [2024]` è l'anno della release; la copertura dati è 2010-2024
  (`time_coverage`)

## Mart

`mart_lcoe_tecnologia`: LCOE per tecnologia e anno + variazione % vs 2010 +
rank di costo per anno.

## Follow-up possibile

Il foglio **`Table S.1`** dello stesso file contiene anche capex (USD/kW) e
capacity factor per tecnologia (2010 vs 2024): potrebbe diventare un secondo
dataset (`irena-costi-tecnologia`) per completare il quadro ROI.
