-- clean.sql for eurostat_rinnovabili
-- Il toolkit SDMX converte già il wide in long

SELECT
    freq,
    nrg_bal,
    unit,
    geo,
    year,
    CAST(value AS DOUBLE) AS value
FROM raw_input
WHERE value IS NOT NULL
  AND freq = 'A'
  AND nrg_bal = 'REN'
  AND unit = 'PC'