-- mart_investimenti_per_cea.sql
-- Investimenti mitigazione per classe CEPA

SELECT
    year,
    cep_class,
    SUM(obs_value) AS investimenti_mln_eur
FROM clean_input
GROUP BY year, cep_class
ORDER BY year, cep_class