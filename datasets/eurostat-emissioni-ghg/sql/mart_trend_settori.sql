-- mart_trend_settori.sql
-- Trend emissioni per settore: confronto primo vs ultimo anno disponibile

WITH prima AS (
    SELECT
        nace_r2 AS settore,
        value AS emissioni_primo,
        year AS anno_primo
    FROM clean_input
    WHERE geo = 'IT'
      AND airpol = 'GHG'
      AND year = (SELECT MIN(year) FROM clean_input WHERE geo = 'IT' AND airpol = 'GHG')
),
ultima AS (
    SELECT
        nace_r2 AS settore,
        value AS emissioni_ultimo,
        year AS anno_ultimo
    FROM clean_input
    WHERE geo = 'IT'
      AND airpol = 'GHG'
      AND year = (SELECT MAX(year) FROM clean_input WHERE geo = 'IT' AND airpol = 'GHG')
)
SELECT
    p.settore,
    p.anno_primo,
    p.emissioni_primo,
    u.anno_ultimo,
    u.emissioni_ultimo,
    ROUND((u.emissioni_ultimo - p.emissioni_primo) / NULLIF(p.emissioni_primo, 0) * 100, 2) AS delta_pct,
    ROUND(
        (POWER(u.emissioni_ultimo / NULLIF(p.emissioni_primo, 0), 1.0 / NULLIF(u.anno_ultimo - p.anno_primo, 0)) - 1) * 100,
        3
    ) AS cagr_annuale
FROM prima p
JOIN ultima u ON p.settore = u.settore
WHERE p.emissioni_primo > 0
ORDER BY delta_pct ASC