-- clean.sql - terna_elettricita_per_settore
-- Input: XLSX da Terna Download Center (ElectricalEnergy)
-- Colonne: Anno, Regione, Provincia, Settore, Consumo (GWh)

SELECT
    CAST("Anno" AS INTEGER) AS anno,
    TRIM(CAST("Regione" AS VARCHAR)) AS regione,
    TRIM(CAST("Provincia" AS VARCHAR)) AS provincia,
    TRIM(CAST("Settore" AS VARCHAR)) AS settore,
    ROUND(SUM(CAST("Consumo (GWh)" AS DOUBLE)), 3) AS consumo_gwh
FROM raw_input
WHERE TRY_CAST("Anno" AS INTEGER) IS NOT NULL
  AND TRIM(CAST("Settore" AS VARCHAR)) <> ''
  AND CAST("Consumo (GWh)" AS DOUBLE) >= 0
GROUP BY 1, 2, 3, 4
ORDER BY 1 DESC, 2, 3, 4
