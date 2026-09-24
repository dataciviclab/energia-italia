-- mart_energia_integrata.sql
-- Visione integrata del sistema energetico italiano:
-- mix fonti + capacity rinnovabile + quota rinnovabili EU
--
-- Fonti: terna_elettricita_per_fonte + terna_capacita_rinnovabile + eurostat_rinnovabili
-- Granularita: anno (nazionale)
-- Metriche: mix fonti, capacity MW, quota rinnovabili %, gap target, classificazione

WITH fonti_rinnovabili AS (
    SELECT 'Fotovoltaico' AS fonte UNION ALL
    SELECT 'Eolico' UNION ALL
    SELECT 'Idrico' UNION ALL
    SELECT 'Geotermoelettrico' UNION ALL
    SELECT 'Bioenergie'
),
produzione_nazionale AS (
    SELECT
        anno,
        fonte,
        SUM(produzione_gwh) AS produzione_gwh
    FROM read_parquet('../../out/data/clean/terna_elettricita_per_fonte/*/*.parquet')
    WHERE tipo_produzione = 'Netta'
    GROUP BY anno, fonte
),
totale_produzione AS (
    SELECT anno, SUM(produzione_gwh) AS totale_gwh
    FROM produzione_nazionale
    GROUP BY anno
),
mix_con_quote AS (
    SELECT
        p.anno,
        p.fonte,
        p.produzione_gwh,
        t.totale_gwh,
        ROUND(p.produzione_gwh / NULLIF(t.totale_gwh, 0) * 100, 2) AS quota_pct,
        CASE WHEN f.fonte IS NOT NULL THEN 'rinnovabile' ELSE 'altro' END AS tipo_fonte
    FROM produzione_nazionale p
    JOIN totale_produzione t ON p.anno = t.anno
    LEFT JOIN fonti_rinnovabili f ON p.fonte = f.fonte
),
rinnovabili_nazionali AS (
    SELECT
        anno,
        ROUND(SUM(CASE WHEN tipo_fonte = 'rinnovabile' THEN quota_pct ELSE 0 END), 2) AS quota_rinnovabili_pct,
        ROUND(SUM(CASE WHEN tipo_fonte = 'altro' THEN quota_pct ELSE 0 END), 2) AS quota_altro_pct
    FROM mix_con_quote
    GROUP BY anno
),
capacity_nazionale AS (
    SELECT
        anno,
        SUM(potenza_totale_mw) AS capacity_totale_mw,
        SUM(CASE WHEN fonti IN ('Fotovoltaico', 'Eolico', 'Idrico', 'Geotermoelettrico', 'Bioenergie')
              THEN potenza_totale_mw ELSE 0 END) AS capacity_rinnovabile_mw
    FROM read_parquet('../../out/data/clean/terna_capacita_rinnovabile/*/*.parquet')
    WHERE tipo_capacita = 'Netta'
    GROUP BY anno
),
eu_rinnovabili AS (
    SELECT year, value AS rinnovabili_eu_pct
    FROM read_parquet('../../out/data/clean/eurostat_rinnovabili/*/*.parquet')
    WHERE geo = 'IT'
)
SELECT
    r.anno,
    r.quota_rinnovabili_pct,
    r.quota_altro_pct,
    c.capacity_totale_mw,
    c.capacity_rinnovabile_mw,
    ROUND(c.capacity_rinnovabile_mw / NULLIF(c.capacity_totale_mw, 0) * 100, 2) AS capacity_rinnovabile_pct,
    e.rinnovabili_eu_pct,
    ROUND(r.quota_rinnovabili_pct - e.rinnovabili_eu_pct, 2) AS delta_vs_eu_pp,
    ROUND(42.0 - r.quota_rinnovabili_pct, 2) AS gap_target_2030_pp,
    CASE
        WHEN r.quota_rinnovabili_pct > 42 THEN 'achieved'
        WHEN r.quota_rinnovabili_pct > 30 THEN 'on-track'
        WHEN r.quota_rinnovabili_pct > 20 THEN 'off-track'
        ELSE 'worsening'
    END AS classificazione
FROM rinnovabili_nazionali r
JOIN capacity_nazionale c ON r.anno = c.anno
LEFT JOIN eu_rinnovabili e ON r.anno = e.year
ORDER BY r.anno
