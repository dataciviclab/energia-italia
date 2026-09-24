-- mart_confronto_ue.sql - Confronto Italia vs principali paesi EU

WITH paesi_ue AS (
    SELECT *
    FROM clean_input
    WHERE nazione IN (
        'Italy', 'Germany', 'France', 'Spain', 'Poland',
        'Netherlands', 'Belgium', 'Austria', 'Sweden', 'Finland',
        'Portugal', 'Greece', 'Czech Republic', 'Romania', 'Hungary'
    )
)
SELECT
    anno,
    nazione,
    ROUND(produzione_neta_twh, 2) AS produzione_neta_twh,
    ROUND(importazione_neta_twh, 2) AS importazione_neta_twh,
    ROUND(richiesta_twh, 2) AS richiesta_twh,
    ROUND(emissioni_co2_mt, 2) AS emissioni_co2_mt,
    CASE
        WHEN produzione_totale_gwh > 0
        THEN ROUND(emissioni_co2_mt * 1e6 / produzione_totale_gwh, 2)
        ELSE NULL
    END AS intensita_carbone,
    RANK() OVER (PARTITION BY anno ORDER BY richiesta_twh DESC) AS rank_domanda
FROM paesi_ue
ORDER BY anno, rank_domanda
