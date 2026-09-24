-- mart_emissioni_italia.sql
-- Emissioni GHG Italia per settore NACE (CO2 equivalente, kilotonnellate)

SELECT
    year,
    nace_r2 AS settore,
    SUM(value) AS emissioni_kt,
    unit
FROM clean_input
WHERE geo = 'IT'
  AND airpol = 'GHG'  -- tutti i gas serra
GROUP BY year, nace_r2, unit
ORDER BY year, nace_r2
