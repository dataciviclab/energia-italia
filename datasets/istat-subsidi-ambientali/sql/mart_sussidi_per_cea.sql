-- mart_sussidi_per_cea.sql
-- Sussidi ambientali per classe CEPA

SELECT
    year,
    cep_class AS dominio,
    SUM(obs_value) AS sussidi_mln_eur
FROM clean_input
GROUP BY year, cep_class
ORDER BY year, cep_class