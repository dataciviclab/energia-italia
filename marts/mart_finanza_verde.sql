-- mart_finanza_verde.sql
-- Finanza verde: sussidi + investimenti ambientali per dominio CEPA
--
-- Fonti: istat_subsidi_ambientali + istat_investimenti_mitigazione
-- Granularita: anno x dominio CEPA
-- Metriche: sussidi, investimenti, rapporto sussidi/investimenti, trend, classificazione

WITH sussidi AS (
    SELECT
        year AS anno,
        cep_class AS dominio,
        SUM(obs_value) AS sussidi_mln_eur
    FROM read_parquet('../../out/data/clean/istat_subsidi_ambientali/*/*.parquet')
    GROUP BY year, cep_class
),
investimenti AS (
    SELECT
        year AS anno,
        cep_class AS dominio,
        SUM(obs_value) AS investimenti_mln_eur
    FROM read_parquet('../../out/data/clean/istat_investimenti_mitigazione/*/*.parquet')
    GROUP BY year, cep_class
),
con_finestre_sussidi AS (
    SELECT
        anno,
        dominio,
        sussidi_mln_eur,
        LAG(sussidi_mln_eur) OVER (PARTITION BY dominio ORDER BY anno) AS prev_sussidi,
        ROUND(AVG(sussidi_mln_eur) OVER (
            PARTITION BY dominio ORDER BY anno ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 1) AS ma3_sussidi
    FROM sussidi
),
con_finestre_investimenti AS (
    SELECT
        anno,
        dominio,
        investimenti_mln_eur,
        LAG(investimenti_mln_eur) OVER (PARTITION BY dominio ORDER BY anno) AS prev_investimenti,
        ROUND(AVG(investimenti_mln_eur) OVER (
            PARTITION BY dominio ORDER BY anno ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 1) AS ma3_investimenti
    FROM investimenti
)
SELECT
    COALESCE(s.anno, i.anno) AS anno,
    COALESCE(s.dominio, i.dominio) AS dominio,
    ROUND(COALESCE(s.sussidi_mln_eur, 0), 1) AS sussidi_mln_eur,
    ROUND(COALESCE(i.investimenti_mln_eur, 0), 1) AS investimenti_mln_eur,
    ROUND(COALESCE(s.sussidi_mln_eur, 0) / NULLIF(COALESCE(i.investimenti_mln_eur, 0), 0) * 100, 2) AS rapporto_sussidi_investimenti_pct,
    ROUND(COALESCE(s.sussidi_mln_eur, 0) - COALESCE(s.prev_sussidi, 0), 1) AS yoy_sussidi_mln,
    ROUND(COALESCE(i.investimenti_mln_eur, 0) - COALESCE(i.prev_investimenti, 0), 1) AS yoy_investimenti_mln,
    s.ma3_sussidi,
    i.ma3_investimenti,
    CASE
        WHEN s.ma3_sussidi > s.prev_sussidi AND i.ma3_investimenti > i.prev_investimenti THEN 'growing_both'
        WHEN s.ma3_sussidi < s.prev_sussidi AND i.ma3_investimenti < i.prev_investimenti THEN 'declining_both'
        WHEN s.ma3_sussidi > s.prev_sussidi THEN 'sussidi_growing'
        WHEN i.ma3_investimenti > i.prev_investimenti THEN 'investimenti_growing'
        ELSE 'stable'
    END AS classificazione
FROM con_finestre_sussidi s
FULL OUTER JOIN con_finestre_investimenti i ON s.anno = i.anno AND s.dominio = i.dominio
ORDER BY anno, dominio
