-- mart_bilancio_nazionale.sql - terna_bilancio_elettrico - Riepilogo annuale bilancio

WITH base AS (
    SELECT
        anno,
        MAX(produzione_neta_twh) AS produzione_neta_twh,
        MAX(importazione_neta_twh) AS importazione_neta_twh,
        MAX(richiesta_twh) AS richiesta_twh,
        MAX(consumi_twh) AS consumi_twh,
        MAX(emissioni_co2_mt) AS emissioni_co2_mt,
        MAX(produzione_termo_gwh) AS produzione_termo_gwh,
        MAX(produzione_totale_gwh) AS produzione_totale_gwh,
        MAX(emissioni_co2_termo_gr_kwh) AS emissioni_co2_termo_gr_kwh,
        MAX(emissioni_co2_totali_gr_kwh) AS emissioni_co2_totali_gr_kwh
    FROM clean_input
    GROUP BY anno
)
SELECT
    anno,
    ROUND(produzione_neta_twh, 2) AS produzione_neta_twh,
    ROUND(importazione_neta_twh, 2) AS importazione_neta_twh,
    ROUND(richiesta_twh, 2) AS richiesta_twh,
    ROUND(consumi_twh, 2) AS consumi_twh,
    ROUND(emissioni_co2_mt, 2) AS emissioni_co2_mt,
    ROUND(produzione_termo_gwh, 2) AS produzione_termo_gwh,
    ROUND(produzione_totale_gwh, 2) AS produzione_totale_gwh,
    ROUND(emissioni_co2_termo_gr_kwh, 2) AS emissioni_co2_termo_gr_kwh,
    ROUND(emissioni_co2_totali_gr_kwh, 2) AS emissioni_co2_totali_gr_kwh,
    CASE
        WHEN importazione_neta_twh > 0
        THEN ROUND(importazione_neta_twh / NULLIF(richiesta_twh, 0) * 100, 2)
        ELSE 0
    END AS copertura_import_pct,
    CASE
        WHEN produzione_totale_gwh > 0
        THEN ROUND(emissioni_co2_mt * 1e6 / NULLIF(produzione_totale_gwh, 0), 2)
        ELSE NULL
    END AS intensita_carbone_g_kwh
FROM base
ORDER BY anno
