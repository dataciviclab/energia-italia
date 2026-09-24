-- mart_emissioni_regione.sql - terna_emissioni_co2 - Emissioni CO2 per regione

SELECT
    anno,
    regione,
    ROUND(SUM(COALESCE(emissioni_mt, 0)), 2) AS emissioni_mt,
    ROUND(SUM(produzione), 2) AS produzione,
    CASE
        WHEN SUM(produzione) > 0
        THEN ROUND(SUM(COALESCE(emissioni_mt, 0)) * 1e6 / SUM(produzione), 2)
        ELSE NULL
    END AS intensita_carbone_g_kwh
FROM clean_input
GROUP BY anno, regione
ORDER BY anno, emissioni_mt DESC
