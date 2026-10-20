-- clean.sql - irena_costi_tecnologia
-- Fonte: IRENA, "Renewable Power Generation Costs in 2024" (datafile, lug 2025)
-- Foglio "Table S.1" — capex (2024 USD/kW), capacity factor (%) e LCOE
-- (2024 USD/kWh) per tecnologia, confronto 2010 vs 2024.
-- Layout: header a r6, dati da r7; col1 = tecnologia, col2-4 capex,
-- col5-7 capacity factor, col8-10 LCOE. Letti con skip=6/header=false → col0..col13.
-- I numeri grandi usano lo spazio come separatore delle migliaia ("3 082").
-- Le variazioni percentuali sono frazioni (0.05 = 5%) → * 100.

SELECT
    trim(CAST("col1" AS VARCHAR)) AS tecnologia,
    cast_double(replace(CAST("col2" AS VARCHAR), ' ', '')) AS capex_2010_usd_kw,
    cast_double(replace(CAST("col3" AS VARCHAR), ' ', '')) AS capex_2024_usd_kw,
    ROUND(100.0 * cast_double("col4"), 1) AS capex_var_pct,
    cast_double("col5") AS cf_2010_pct,
    cast_double("col6") AS cf_2023_pct,
    ROUND(100.0 * cast_double("col7"), 1) AS cf_var_pct,
    cast_double("col8") AS lcoe_2010_usd_kwh,
    cast_double("col9") AS lcoe_2024_usd_kwh,
    ROUND(100.0 * cast_double("col10"), 1) AS lcoe_var_pct
FROM raw_input
WHERE "col1" IS NOT NULL
  AND trim(CAST("col1" AS VARCHAR)) <> ''
ORDER BY tecnologia
