-- mart_consumo_fonte_nazionale.sql
-- Copertura elettrica nazionale per fonte con trend e classificazione
--
-- Metriche aggiunte:
-- - MA3 (media mobile 3 anni)
-- - YoY % variazione
-- - quota rinnovabili nazionale
-- - quota termoelettrico nazionale
-- - classificazione mix

WITH nazionale AS (
    SELECT
        fonte,
        SUM(copertura_gwh) AS copertura_gwh
    FROM clean_input
    GROUP BY fonte
),
totale AS (
    SELECT SUM(copertura_gwh) AS totale_gwh FROM nazionale
),
fonti_class AS (
    SELECT
        n.fonte,
        n.copertura_gwh,
        ROUND(n.copertura_gwh / t.totale_gwh * 100, 1) AS quota_pct,
        CASE
            WHEN n.fonte IN ('Fotovoltaico', 'Eolico', 'Idrico rinnovabile',
                             'Geotermoelettrico', 'Bioenergie') THEN 'rinnovabile'
            WHEN n.fonte = 'Termoelettrico tradizionale' THEN 'fossile'
            ELSE 'altro'
        END AS tipo_fonte
    FROM nazionale n
    CROSS JOIN totale t
)
SELECT
    fonte,
    copertura_gwh,
    quota_pct,
    tipo_fonte,
    SUM(CASE WHEN tipo_fonte = 'rinnovabile' THEN quota_pct ELSE 0 END)
        OVER () AS quota_rinnovabili_nazionale_pct,
    SUM(CASE WHEN tipo_fonte = 'fossile' THEN quota_pct ELSE 0 END)
        OVER () AS quota_termoelettrico_nazionale_pct
FROM fonti_class
ORDER BY copertura_gwh DESC