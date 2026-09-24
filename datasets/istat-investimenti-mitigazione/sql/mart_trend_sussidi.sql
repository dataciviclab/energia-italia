-- mart_trend_sussidi.sql
-- Trend sussidi per dominio: confronto prima e ultima osservazione

WITH prima AS (
    SELECT env_domain, value AS sussidi_prima, year AS anno_prima
    FROM clean_input
    WHERE year = (SELECT MIN(year) FROM clean_input)
),
ultima AS (
    SELECT env_domain, value AS sussidi_ultimo, year AS anno_ultimo
    FROM clean_input
    WHERE year = (SELECT MAX(year) FROM clean_input)
)
SELECT
    p.env_domain AS dominio,
    p.sussidi_prima,
    p.anno_prima,
    u.sussidi_ultimo,
    u.anno_ultimo,
    ROUND((u.sussidi_ultimo - p.sussidi_prima) / NULLIF(p.sussidi_prima, 0) * 100, 2) AS delta_pct
FROM prima p
JOIN ultima u ON p.env_domain = u.env_domain
ORDER BY delta_pct DESC
