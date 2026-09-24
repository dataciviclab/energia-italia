-- mart_investimenti_italia.sql
-- Investimenti mitigazione per settore EGSS

SELECT
    year,
    egss AS voce,
    SUM(value) AS investimenti_mln_eur
FROM clean_input
GROUP BY year, egss
ORDER BY year, egss
