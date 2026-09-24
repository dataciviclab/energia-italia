-- mart_emissioni_completo.sql
-- Confronto fonti emissioni GHG: ISPRA (macro-settori, 1990-2023) vs Eurostat (NACE, 2008-2023)
--
-- Metriche:
-- - trend ISPRA per settore (MA3, YoY%, classificazione)
-- - confronto totale ISPRA vs Eurostat (dove sovrapposti)
-- - gap target -55% 2030 vs 1990

WITH ispra_long AS (
    SELECT
        anno,
        'industrie_energetiche' AS settore,
        industrie_energetiche AS emissioni_mt
    FROM read_parquet('../../out/data/clean/ispra_emissioni_ghg/*/*.parquet')
    UNION ALL
    SELECT anno, 'industrie_manifatturiere', industrie_manifatturiere
    FROM read_parquet('../../out/data/clean/ispra_emissioni_ghg/*/*.parquet')
    UNION ALL
    SELECT anno, 'residenziale_e_servizi', residenziale_e_servizi
    FROM read_parquet('../../out/data/clean/ispra_emissioni_ghg/*/*.parquet')
    UNION ALL
    SELECT anno, 'trasporti', trasporti
    FROM read_parquet('../../out/data/clean/ispra_emissioni_ghg/*/*.parquet')
    UNION ALL
    SELECT anno, 'totale', totale
    FROM read_parquet('../../out/data/clean/ispra_emissioni_ghg/*/*.parquet')
),
ispra_con_finestre AS (
    SELECT
        anno,
        settore,
        emissioni_mt,
        LAG(emissioni_mt) OVER (PARTITION BY settore ORDER BY anno) AS prev_mt,
        ROUND(AVG(emissioni_mt) OVER (
            PARTITION BY settore ORDER BY anno ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 1) AS ma3
    FROM ispra_long
    WHERE emissioni_mt IS NOT NULL
),
eurostat_totale AS (
    SELECT
        year,
        SUM(value) AS emissioni_t_eurostat
    FROM read_parquet('../../out/data/clean/eurostat_emissioni_ghg/*/*.parquet')
    WHERE geo = 'IT' AND airpol = 'GHG'
    GROUP BY year
),
baseline AS (
    SELECT settore, emissioni_mt AS emissioni_1990
    FROM ispra_long
    WHERE anno = 1990
)
SELECT
    i.anno,
    i.settore,
    ROUND(i.emissioni_mt, 2) AS emissioni_mt,
    ROUND(i.emissioni_mt - b.emissioni_1990, 2) AS delta_vs_1990_mt,
    ROUND((i.emissioni_mt - b.emissioni_1990) / NULLIF(b.emissioni_1990, 0) * 100, 1) AS delta_vs_1990_pct,
    ROUND(i.emissioni_mt - i.prev_mt, 2) AS yoy_mt,
    ROUND((i.emissioni_mt - i.prev_mt) / NULLIF(i.prev_mt, 0) * 100, 2) AS yoy_pct,
    i.ma3,
    CASE
        WHEN i.settore = 'totale' AND i.emissioni_mt <= b.emissioni_1990 * 0.45 THEN 'on-track'
        WHEN i.settore = 'totale' AND i.emissioni_mt > b.emissioni_1990 * 0.7 THEN 'worsening'
        WHEN i.settore = 'totale' THEN 'off-track'
        WHEN i.ma3 > i.prev_mt THEN 'worsening'
        WHEN i.ma3 < i.prev_mt THEN 'improving'
        ELSE 'stable'
    END AS classificazione,
    ROUND(426.2 * 0.45, 1) AS target_2030_mt,
    ROUND(i.emissioni_mt - 426.2 * 0.45, 2) AS gap_target_mt
FROM ispra_con_finestre i
JOIN baseline b ON i.settore = b.settore
ORDER BY i.anno, i.settore
