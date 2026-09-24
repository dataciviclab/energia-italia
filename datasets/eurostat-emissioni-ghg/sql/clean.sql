-- clean.sql for eurostat_emissioni_ghg
-- Il toolkit SDMX converte già il wide in long con colonne standard

SELECT
    freq,
    airpol,
    nace_r2,
    unit,
    geo,
    CAST(year AS INTEGER) AS year,
    CAST(value AS DOUBLE) AS value
FROM raw_input
WHERE value IS NOT NULL
  AND freq = 'A'
  AND airpol IN ('GHG', 'CO2', 'CH4', 'N2O', 'HFC_CO2E', 'PFC_CO2E', 'NF3_SF6_CO2E')
