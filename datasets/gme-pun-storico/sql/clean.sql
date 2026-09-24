-- clean.sql - gme_pun_storico - Prezzi storici PUN/PSV da Portale Offerte
-- CSV: delimiter ";", encoding cp1252, decimal ","
-- DuckDB read_csv con decimal_separator="," gestisce già la conversione.
-- Usare cast_double direttamente, NON normalize_italian_number.

SELECT
    cast_int(substring(normalize_string("AnnoMese"), 1, 4)) AS anno,
    cast_int(substring(normalize_string("AnnoMese"), 5, 2)) AS mese,
    normalize_string("AnnoMese") AS anno_mese,
    cast_double("PUN (€/kWh)") AS pun_eur_kwh,
    cast_double("PSV (€/Smc)") AS psv_eur_smc,
    cast_double("PE (€/kWh)") AS pe_eur_kwh,
    cast_double("CMEM (€/Smc)") AS cmem_eur_smc,
    cast_double("Pfor (€/Smc)") AS pfor_eur_smc,
    cast_double("Psbil (€/Smc)") AS psbil_eur_smc
FROM raw_input
WHERE "AnnoMese" IS NOT NULL
  AND cast_int(substring(normalize_string("AnnoMese"), 1, 4)) IS NOT NULL
