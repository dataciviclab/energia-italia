-- mart_pun_mensile.sql - gme_pun_storico - PUN mensile con confronto YoY e media mobile

WITH base AS (
    SELECT
        anno,
        mese,
        pun_eur_kwh,
        psv_eur_smc,
        pe_eur_kwh,
        LAG(pun_eur_kwh, 12) OVER (ORDER BY anno, mese) AS pun_12m_fa,
        AVG(pun_eur_kwh) OVER (
            ORDER BY anno, mese
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ma3_pun
    FROM clean_input
)
SELECT
    anno,
    mese,
    ROUND(pun_eur_kwh, 6) AS pun_eur_kwh,
    ROUND(psv_eur_smc, 6) AS psv_eur_smc,
    ROUND(pe_eur_kwh, 6) AS pe_eur_kwh,
    CASE
        WHEN pun_12m_fa IS NOT NULL AND pun_12m_fa > 0
        THEN ROUND((pun_eur_kwh - pun_12m_fa) / pun_12m_fa * 100, 2)
        ELSE NULL
    END AS yoy_pct,
    ROUND(ma3_pun, 6) AS ma3
FROM base
ORDER BY anno, mese
