-- clean.sql - terna_bilancio_elettrico - Bilancio elettrico confronti internazionali
-- Fonte: Terna Download Center (ElectricityBalance)
-- NOTA: è un dataset di confronto internazionale, non il bilancio italiano.
-- Solo l'Italia è utile per il nostro scopo; il resto serve per benchmarking.

SELECT
    cast_int("Anno") AS anno,
    normalize_string("Nazione") AS nazione,
    cast_double("Produzione Netta (TWh)") AS produzione_neta_twh,
    cast_double("Importazione Netta (TWh)") AS importazione_neta_twh,
    cast_double("Richiesta (TWh)") AS richiesta_twh,
    cast_double("Consumi (TWh)") AS consumi_twh,
    cast_double("Emissioni Co2 (MT)") AS emissioni_co2_mt,
    cast_double("Produzione Termoelettrica (GWh)") AS produzione_termo_gwh,
    cast_double("Produzione Totale (GWh)") AS produzione_totale_gwh,
    cast_double("Emissioni Co2 Termoelettriche (gr/kWh)") AS emissioni_co2_termo_gr_kwh,
    cast_double("Emissioni Co2 Totali (gr/kWh)") AS emissioni_co2_totali_gr_kwh
FROM raw_input
WHERE cast_int("Anno") IS NOT NULL
  AND normalize_string("Nazione") IS NOT NULL
  AND normalize_string("Nazione") NOT LIKE 'Applied%'
  AND normalize_string("Nazione") <> ''
