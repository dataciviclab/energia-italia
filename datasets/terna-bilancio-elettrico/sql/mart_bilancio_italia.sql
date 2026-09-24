-- mart_bilancio_italia.sql - Solo dati Italia

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
    END AS copertura_import_pct
FROM clean_input
WHERE nazione = 'Italy'
ORDER BY anno
