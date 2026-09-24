-- mart_rinnovabili_italia.sql
-- Serie storica % rinnovabili Italia con target 2030, trend e classificazione
--
-- Metriche aggiunte:
-- - media mobile 3 e 5 anni (smussa rumore)
-- - YoY % (variazione anno su anno)
-- - baseline 2004 (primo anno disponibile)
-- - distance-to-target 2030 (42%)
-- - classificazione: on-track / off-track / worsening
-- - proiezione anno raggiungimento target (se trend lineare)

WITH italia AS (
    SELECT year, value AS rinnovabili_pct
    FROM clean_input
    WHERE geo = 'IT'
),
target AS (
    SELECT 42.0 AS target_2030
),
con_finestre AS (
    SELECT
        i.year,
        i.rinnovabili_pct,
        t.target_2030,
        ROUND(t.target_2030 - i.rinnovabili_pct, 2) AS gap_target_pct,
        FIRST_VALUE(i.rinnovabili_pct) OVER (ORDER BY i.year) AS baseline_pct,
        LAG(i.rinnovabili_pct) OVER (ORDER BY i.year) AS prev_pct,
        ROUND(AVG(i.rinnovabili_pct) OVER (
            ORDER BY i.year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS ma3,
        ROUND(AVG(i.rinnovabili_pct) OVER (
            ORDER BY i.year ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 2) AS ma5
    FROM italia i
    CROSS JOIN target t
)
SELECT
    year,
    rinnovabili_pct,
    target_2030,
    gap_target_pct,
    baseline_pct,
    ROUND(rinnovabili_pct - baseline_pct, 2) AS delta_vs_baseline_pp,
    ROUND((rinnovabili_pct - prev_pct), 2) AS yoy_pp,
    ROUND((rinnovabili_pct - prev_pct) / NULLIF(prev_pct, 0) * 100, 2) AS yoy_pct,
    ma3,
    ma5,
    CASE
        WHEN gap_target_pct <= 0 THEN 'achieved'
        WHEN rinnovabili_pct > 35 THEN 'on-track'
        WHEN rinnovabili_pct > 25 THEN 'off-track'
        WHEN rinnovabili_pct < 15 THEN 'worsening'
        ELSE 'off-track'
    END AS classificazione,
    CASE
        WHEN ma3 IS NOT NULL AND ma3 > LAG(ma3) OVER (ORDER BY year)
             AND gap_target_pct > 0
        THEN ROUND(year + gap_target_pct / NULLIF((ma3 - LAG(ma3) OVER (ORDER BY year)), 0), 0)
        ELSE NULL
    END AS anno_proiettato_target
FROM con_finestre
ORDER BY year