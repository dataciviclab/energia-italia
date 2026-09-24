-- mart_sussidi_per_dominio.sql
-- Sussidi ambientali per dominio ambientale

SELECT
    year,
    env_domain AS dominio,
    SUM(value) AS sussidi_mln_eur
FROM clean_input
GROUP BY year, env_domain
ORDER BY year, env_domain
