-- mart_transizione_regionale.sql
-- Transizione energetica regionale: capacity + produzione + mix per regione
--
-- Fonti: terna_capacita_rinnovabile + terna_elettricita_per_fonte
-- Granularita: anno x regione
-- Metriche: capacity MW, produzione GWh, quota rinnovabili, ranking, classificazione

WITH fonti_rinnovabili AS (
    SELECT 'Fotovoltaico' AS fonte UNION ALL
    SELECT 'Eolico' UNION ALL
    SELECT 'Idrico' UNION ALL
    SELECT 'Geotermoelettrico' UNION ALL
    SELECT 'Bioenergie'
),
capacity AS (
    SELECT
        anno,
        regione,
        SUM(potenza_totale_mw) AS capacity_totale_mw,
        SUM(CASE WHEN fonti IN ('Fotovoltaico', 'Eolico', 'Idrico', 'Geotermoelettrico', 'Bioenergie')
              THEN potenza_totale_mw ELSE 0 END) AS capacity_rinnovabile_mw
    FROM read_parquet('../../out/data/clean/terna_capacita_rinnovabile/*/*.parquet')
    WHERE tipo_capacita = 'Netta'
    GROUP BY anno, regione
),
produzione AS (
    SELECT
        anno,
        regione,
        SUM(produzione_gwh) AS produzione_totale_gwh,
        SUM(CASE WHEN fonti IN ('Fotovoltaico', 'Eolico', 'Idrico', 'Geotermoelettrico', 'Bioenergie')
              THEN produzione_gwh ELSE 0 END) AS produzione_rinnovabile_gwh
    FROM read_parquet('../../out/data/clean/terna_elettricita_per_fonte/*/*.parquet')
    WHERE tipo_produzione = 'Netta'
    GROUP BY anno, regione
),
integrated AS (
    SELECT
        COALESCE(c.anno, p.anno) AS anno,
        COALESCE(c.regione, p.regione) AS regione,
        c.capacity_totale_mw,
        c.capacity_rinnovabile_mw,
        ROUND(c.capacity_rinnovabile_mw / NULLIF(c.capacity_totale_mw, 0) * 100, 2) AS capacity_rinnovabile_pct,
        p.produzione_totale_gwh,
        p.produzione_rinnovabile_gwh,
        ROUND(p.produzione_rinnovabile_gwh / NULLIF(p.produzione_totale_gwh, 0) * 100, 2) AS produzione_rinnovabile_pct,
        LAG(ROUND(p.produzione_rinnovabile_gwh / NULLIF(p.produzione_totale_gwh, 0) * 100, 2))
            OVER (PARTITION BY COALESCE(c.regione, p.regione) ORDER BY COALESCE(c.anno, p.anno)) AS prev_produzione_rinnovabile_pct
    FROM capacity c
    FULL OUTER JOIN produzione p ON c.anno = p.anno AND c.regione = p.regione
)
SELECT
    anno,
    regione,
    capacity_totale_mw,
    capacity_rinnovabile_mw,
    capacity_rinnovabile_pct,
    produzione_totale_gwh,
    produzione_rinnovabile_gwh,
    produzione_rinnovabile_pct,
    ROUND(produzione_rinnovabile_pct - prev_produzione_rinnovabile_pct, 2) AS yoy_pp,
    ROUND((produzione_rinnovabile_pct - prev_produzione_rinnovabile_pct)
        / NULLIF(prev_produzione_rinnovabile_pct, 0) * 100, 2) AS yoy_pct,
    RANK() OVER (PARTITION BY anno ORDER BY produzione_rinnovabile_pct DESC) AS ranking_rinnovabili,
    CASE
        WHEN produzione_rinnovabile_pct > 60 THEN 'leader'
        WHEN produzione_rinnovabile_pct > 40 THEN 'good'
        WHEN produzione_rinnovabile_pct > 20 THEN 'developing'
        ELSE 'lagging'
    END AS classificazione
FROM integrated
WHERE anno IS NOT NULL
ORDER BY anno, ranking_rinnovabili
