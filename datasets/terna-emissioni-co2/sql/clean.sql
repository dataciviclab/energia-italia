-- clean.sql - terna_emissioni_co2 - Emissioni CO2 per combustibile e regione
-- Fonte: Terna Download Center (GrossVsCO2Emissions)

SELECT
    cast_int("Anno") AS anno,
    normalize_string("Combustibile") AS combustibile,
    cast_double("Produzione") AS produzione,
    normalize_string("Regione") AS regione,
    cast_double("Emissioni (milioni di tonnellate)") AS emissioni_mt
FROM raw_input
WHERE cast_int("Anno") IS NOT NULL
  AND normalize_string("Combustibile") IS NOT NULL
