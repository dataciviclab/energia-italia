-- mart_costi_tecnologia.sql
-- Confronto 2010 vs 2024 per tecnologia: capex, capacity factor, LCOE.
-- Aggiunge due indicatori derivati:
--   capex_per_mw_2024 = capex in USD per MW installato
--   mwh_per_mw_anno   = energia annua per MW (CF * 8760)

SELECT
    tecnologia,
    capex_2010_usd_kw,
    capex_2024_usd_kw,
    ROUND(capex_2024_usd_kw * 1000, 0) AS capex_per_mw_2024_usd,
    capex_var_pct,
    cf_2010_pct,
    cf_2023_pct,
    cf_var_pct,
    ROUND(cf_2023_pct / 100.0 * 8760, 0) AS mwh_per_mw_anno,
    lcoe_2010_usd_kwh,
    lcoe_2024_usd_kwh,
    lcoe_var_pct
FROM clean_input
ORDER BY lcoe_2024_usd_kwh
