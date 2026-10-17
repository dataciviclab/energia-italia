-- mart_intensita_regionale.sql
-- Intensita di carbonio della copertura elettrica regionale + quota rinnovabile.
-- emissioni di produzione (emissioni-co2) / copertura locale della domanda
-- (copertura-domanda, escluso il saldo import/export che non e' produzione locale).
-- intensita g CO2/kWh = Mt * 1e12 g / (GWh * 1e6 kWh) = Mt/GWh * 1e6.

WITH emis AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(emissioni_mt) FILTER (
            WHERE emissioni_mt IS NOT NULL AND NOT isnan(emissioni_mt)
        ) AS emissioni_mt
    FROM read_parquet('{support.emissioni.clean}')
    GROUP BY 1, 2
),
cop AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(copertura_gwh) FILTER (WHERE fonte <> 'Saldo import/export') AS copertura_locale_gwh,
        SUM(copertura_gwh) FILTER (
            WHERE fonte IN ('Eolico', 'Fotovoltaico', 'Idrico rinnovabile', 'Geotermoelettrico', 'Bioenergie')
        ) AS rinnovabili_gwh
    FROM read_parquet('{support.copertura.clean}')
    GROUP BY 1, 2
)
SELECT
    c.anno,
    c.regione,
    ROUND(e.emissioni_mt, 2) AS emissioni_mt,
    ROUND(c.copertura_locale_gwh, 0) AS copertura_locale_gwh,
    ROUND(1000000.0 * e.emissioni_mt / NULLIF(c.copertura_locale_gwh, 0), 1) AS intensita_g_kwh,
    ROUND(100.0 * c.rinnovabili_gwh / NULLIF(c.copertura_locale_gwh, 0), 1) AS quota_rinnovabili_pct
FROM cop c
JOIN emis e USING (anno, regione)
WHERE c.copertura_locale_gwh > 0
ORDER BY anno, regione
