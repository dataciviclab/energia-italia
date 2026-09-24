-- mart_pun_annuale.sql - gme_pun_storico - Riepilogo annuale PUN/PSV

SELECT
    anno,
    ROUND(AVG(pun_eur_kwh), 6) AS pun_medio_kwh,
    ROUND(AVG(psv_eur_smc), 6) AS psv_medio_smc,
    ROUND(AVG(pe_eur_kwh), 6) AS pe_medio_kwh,
    ROUND(MIN(pun_eur_kwh), 6) AS pun_min_kwh,
    ROUND(MAX(pun_eur_kwh), 6) AS pun_max_kwh,
    ROUND(MIN(psv_eur_smc), 6) AS psv_min_smc,
    ROUND(MAX(psv_eur_smc), 6) AS psv_max_smc,
    COUNT(*) AS mesi
FROM clean_input
GROUP BY anno
ORDER BY anno
