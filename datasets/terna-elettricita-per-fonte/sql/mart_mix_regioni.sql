-- mart_mix_regioni.sql
-- Mix energetico regionale: quota rinnovabili e classificazione (per singolo anno)
-- Il toolkit esegue questo SQL per ogni anno separatamente.

WITH fonti_rinnovabili AS (
    SELECT 'Fotovoltaico' AS fonte UNION ALL
    SELECT 'Eolico' UNION ALL
    SELECT 'Idrico' UNION ALL
    SELECT 'Geotermoelettrico' UNION ALL
    SELECT 'Bioenergie'
),
netta AS (
    SELECT
        anno,
        regione,
        fonte,
        SUM(produzione_gwh) AS produzione_gwh_netta
    FROM clean_input
    WHERE tipo_produzione = 'Netta'
    GROUP BY anno, regione, fonte
),
totali_regione AS (
    SELECT anno, regione, SUM(produzione_gwh_netta) AS totale_regione_gwh_netta
    FROM netta
    GROUP BY anno, regione
),
rinnovabili_regione AS (
    SELECT n.anno, n.regione, SUM(n.produzione_gwh_netta) AS rinnovabili_gwh
    FROM netta n
    JOIN fonti_rinnovabili f ON n.fonte = f.fonte
    GROUP BY n.anno, n.regione
)
SELECT
    t.anno,
    t.regione,
    ROUND(t.totale_regione_gwh_netta, 6) AS totale_regione_gwh_netta,
    ROUND(COALESCE(r.rinnovabili_gwh, 0), 6) AS rinnovabili_gwh,
    ROUND(COALESCE(r.rinnovabili_gwh, 0) / NULLIF(t.totale_regione_gwh_netta, 0) * 100, 2) AS quota_rinnovabili_pct,
    RANK() OVER (ORDER BY COALESCE(r.rinnovabili_gwh, 0) / NULLIF(t.totale_regione_gwh_netta, 0) DESC) AS ranking_rinnovabili,
    CASE
        WHEN COALESCE(r.rinnovabili_gwh, 0) / NULLIF(t.totale_regione_gwh_netta, 0) * 100 > 50 THEN 'leader'
        WHEN COALESCE(r.rinnovabili_gwh, 0) / NULLIF(t.totale_regione_gwh_netta, 0) * 100 > 30 THEN 'good'
        WHEN COALESCE(r.rinnovabili_gwh, 0) / NULLIF(t.totale_regione_gwh_netta, 0) * 100 > 15 THEN 'developing'
        ELSE 'lagging'
    END AS classificazione
FROM totali_regione t
LEFT JOIN rinnovabili_regione r ON t.anno = r.anno AND t.regione = r.regione
ORDER BY ranking_rinnovabili
