-- clean.sql - irena_lcoe
-- Fonte: IRENA, "Renewable Power Generation Costs in 2024" (datafile, lug 2025)
-- Foglio "Fig 1.2 " — LCOE globale pesato per tecnologia, 2010-2024 (2024 USD/kWh).
-- Struttura del foglio: riga header a r5, dati da r6; col1 = tecnologia,
-- col2..col16 = anni 2010..2024. Letti con skip=5/header=false → col0..col23.

WITH base AS (
    SELECT
        trim(CAST("col1" AS VARCHAR)) AS tecnologia,
        "col2"  AS y2010,
        "col3"  AS y2011,
        "col4"  AS y2012,
        "col5"  AS y2013,
        "col6"  AS y2014,
        "col7"  AS y2015,
        "col8"  AS y2016,
        "col9"  AS y2017,
        "col10" AS y2018,
        "col11" AS y2019,
        "col12" AS y2020,
        "col13" AS y2021,
        "col14" AS y2022,
        "col15" AS y2023,
        "col16" AS y2024
    FROM raw_input
    WHERE "col1" IS NOT NULL
      AND trim(CAST("col1" AS VARCHAR)) <> ''
),
unp AS (
    SELECT * FROM (
        UNPIVOT base
        ON y2010, y2011, y2012, y2013, y2014, y2015, y2016, y2017,
           y2018, y2019, y2020, y2021, y2022, y2023, y2024
        INTO NAME anno_col VALUE lcoe_usd_kwh
    )
)
SELECT
    tecnologia,
    CAST(replace(anno_col, 'y', '') AS INTEGER) AS anno,
    cast_double(lcoe_usd_kwh) AS lcoe_usd_kwh
FROM unp
WHERE cast_double(lcoe_usd_kwh) IS NOT NULL
ORDER BY tecnologia, anno
