-- clean.sql - terna_copertura_domanda - Copertura domanda per fonte e regione
-- Fonte: Terna Download Center (ConsumptionBySource)

SELECT
    cast_int("Anno") AS anno,
    normalize_string("Regione") AS regione,
    normalize_string("Fonte") AS fonte,
    cast_double("Copertura (GWh)") AS copertura_gwh
FROM raw_input
WHERE cast_int("Anno") IS NOT NULL
  AND normalize_string("Fonte") IS NOT NULL
