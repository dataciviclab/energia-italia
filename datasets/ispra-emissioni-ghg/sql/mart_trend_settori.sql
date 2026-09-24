-- mart_trend_settori.sql — Trend emissioni GHG per settore (1990 -> ultimo anno)
--
-- 1 riga = 1 settore (4 settori + totale) con metriche di trend:
-- delta assoluto e % dalla baseline 1990, CAGR annuale, picco e minimo
-- della serie con relativi anni, classificazione trend.
--
-- PK: (settore)

WITH settori AS (
    SELECT
        anno,
        'industrie_energetiche' AS settore,
        industrie_energetiche AS emissioni_mt
    FROM clean_input
    UNION ALL
    SELECT anno, 'industrie_manifatturiere', industrie_manifatturiere FROM clean_input
    UNION ALL
    SELECT anno, 'residenziale_e_servizi', residenziale_e_servizi FROM clean_input
    UNION ALL
    SELECT anno, 'trasporti', trasporti FROM clean_input
    UNION ALL
    SELECT anno, 'totale', totale FROM clean_input
),
con_finestre AS (
    SELECT
        anno,
        settore,
        emissioni_mt,
        MIN(anno) OVER (PARTITION BY settore) AS anno_primo,
        MAX(anno) OVER (PARTITION BY settore) AS anno_ultimo,
        ROUND(AVG(emissioni_mt) OVER (
            PARTITION BY settore ORDER BY anno ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 1) AS ma3
    FROM settori
    WHERE emissioni_mt IS NOT NULL
),
ultimi_3 AS (
    SELECT settore, AVG(emissioni_mt) AS media_ultimi_3
    FROM settori
    WHERE emissioni_mt IS NOT NULL
      AND anno >= (SELECT MAX(anno) - 2 FROM settori)
    GROUP BY settore
),
primi_3 AS (
    SELECT settore, AVG(emissioni_mt) AS media_primi_3
    FROM settori
    WHERE emissioni_mt IS NOT NULL
      AND anno <= (SELECT MIN(anno) + 2 FROM settori)
    GROUP BY settore
)
SELECT
    c.settore,
    MIN(c.anno_primo) AS anno_primo,
    MAX(c.anno_ultimo) AS anno_ultimo,
    ROUND(SUM(CASE WHEN anno = anno_primo THEN emissioni_mt END), 1) AS emissioni_1990,
    ROUND(SUM(CASE WHEN anno = anno_ultimo THEN emissioni_mt END), 1) AS emissioni_ultimo,
    ROUND(
        SUM(CASE WHEN anno = anno_ultimo THEN emissioni_mt END)
        - SUM(CASE WHEN anno = anno_primo THEN emissioni_mt END),
        1
    ) AS delta_assoluto_mt,
    ROUND(
        100.0 * (
            SUM(CASE WHEN anno = anno_ultimo THEN emissioni_mt END)
            - SUM(CASE WHEN anno = anno_primo THEN emissioni_mt END)
        ) / NULLIF(SUM(CASE WHEN anno = anno_primo THEN emissioni_mt END), 0),
        1
    ) AS delta_pct,
    ROUND(
        POWER(
            SUM(CASE WHEN anno = anno_ultimo THEN emissioni_mt END)
            / NULLIF(SUM(CASE WHEN anno = anno_primo THEN emissioni_mt END), 0),
            1.0 / NULLIF(MAX(anno_ultimo) - MIN(anno_primo), 0)
        ) - 1,
        4
    ) AS cagr_annuale,
    ROUND(MAX(emissioni_mt), 1) AS emissioni_picco,
    arg_max(anno, emissioni_mt) AS anno_picco,
    ROUND(MIN(emissioni_mt), 1) AS emissioni_minimo,
    arg_min(anno, emissioni_mt) AS anno_minimo,
    CASE
        WHEN u.media_ultimi_3 < p.media_primi_3 * 0.7 THEN 'strong_decline'
        WHEN u.media_ultimi_3 < p.media_primi_3 * 0.95 THEN 'improving'
        WHEN u.media_ultimi_3 > p.media_primi_3 * 1.05 THEN 'worsening'
        ELSE 'stable'
    END AS classificazione_trend
FROM con_finestre c
JOIN ultimi_3 u ON c.settore = u.settore
JOIN primi_3 p ON c.settore = p.settore
GROUP BY c.settore, u.media_ultimi_3, p.media_primi_3
ORDER BY c.settore
