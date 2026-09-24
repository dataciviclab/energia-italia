-- clean.sql for terna_consumo_per_fonte
-- Copertura elettrica per fonte di produzione

SELECT
    CAST("Anno" AS INTEGER) AS anno,
    TRIM(CAST("Regione" AS VARCHAR)) AS regione,
    TRIM(CAST("Fonte" AS VARCHAR)) AS fonte,
    CAST("Copertura (GWh)" AS DOUBLE) AS copertura_gwh
FROM raw_input
WHERE TRY_CAST("Anno" AS INTEGER) IS NOT NULL
  AND "Copertura (GWh)" IS NOT NULL