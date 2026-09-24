-- mart_confronto_eu.sql
-- Confronto emissioni Italia vs EU27 per gas (GHG totale)

WITH italia AS (
    SELECT
        year,
        airpol,
        SUM(value) AS emissioni_t
    FROM clean_input
    WHERE geo = 'IT'
      AND unit = 'T'
      AND nace_r2 = 'TOTAL'
    GROUP BY year, airpol
),
eu27 AS (
    SELECT
        year,
        airpol,
        SUM(value) AS emissioni_t
    FROM clean_input
    WHERE geo = 'EU27_2020'
      AND unit = 'T'
      AND nace_r2 = 'TOTAL'
    GROUP BY year, airpol
)
SELECT
    i.year,
    i.airpol AS gas,
    i.emissioni_t AS emissioni_it,
    e.emissioni_t AS emissioni_eu27,
    ROUND(i.emissioni_t / NULLIF(e.emissioni_t, 0) * 100, 2) AS quota_it_pct
FROM italia i
JOIN eu27 e ON i.year = e.year AND i.airpol = e.airpol
WHERE i.airpol = 'GHG'
ORDER BY i.year