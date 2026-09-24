-- mart_emissioni_italia_settori.sql
-- Emissioni Italia per settore NACE e gas (top 15 per totale storico)

WITH top_settori AS (
    SELECT
        nace_r2,
        SUM(value) AS totale_storico
    FROM clean_input
    WHERE geo = 'IT'
      AND airpol = 'GHG'
      AND unit = 'T'
      AND nace_r2 NOT IN ('TOTAL', 'TOTAL_NRG', 'TOTALOTH', 'HH', 'TOTAL_HH')
    GROUP BY nace_r2
    ORDER BY totale_storico DESC
    LIMIT 15
)
SELECT
    c.year,
    c.nace_r2 AS settore,
    c.airpol AS gas,
    SUM(c.value) AS emissioni_t
FROM clean_input c
JOIN top_settori t ON c.nace_r2 = t.nace_r2
WHERE c.geo = 'IT'
  AND c.unit = 'T'
GROUP BY c.year, c.nace_r2, c.airpol
ORDER BY c.year, c.nace_r2