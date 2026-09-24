-- mart_settori_anno.sql — Emissioni GHG per settore x anno (formato long)
--
-- Trasforma il clean wide in long con metriche di trend:
-- - MA3 (media mobile 3 anni)
-- - YoY % (variazione anno su anno)
-- - quota % sul totale nazionale
-- - classificazione: improving / worsening / stable
--
-- PK: (anno, settore)

WITH settori AS (
    SELECT
        anno,
        'industrie_energetiche' AS settore,
        industrie_energetiche AS emissioni_mt,
        totale
    FROM clean_input
    UNION ALL
    SELECT anno, 'industrie_manifatturiere', industrie_manifatturiere, totale FROM clean_input
    UNION ALL
    SELECT anno, 'residenziale_e_servizi', residenziale_e_servizi, totale FROM clean_input
    UNION ALL
    SELECT anno, 'trasporti', trasporti, totale FROM clean_input
),
con_finestre AS (
    SELECT
        anno,
        settore,
        emissioni_mt,
        totale,
        ROUND(100.0 * emissioni_mt / NULLIF(totale, 0), 2) AS quota_pct,
        LAG(emissioni_mt) OVER (PARTITION BY settore ORDER BY anno) AS prev_mt,
        ROUND(AVG(emissioni_mt) OVER (
            PARTITION BY settore ORDER BY anno ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS ma3
    FROM settori
    WHERE emissioni_mt IS NOT NULL
)
SELECT
    anno,
    settore,
    ROUND(emissioni_mt, 2) AS emissioni_mt,
    quota_pct,
    ROUND(emissioni_mt - prev_mt, 2) AS yoy_mt,
    ROUND((emissioni_mt - prev_mt) / NULLIF(prev_mt, 0) * 100, 2) AS yoy_pct,
    ma3,
    CASE
        WHEN ma3 IS NOT NULL AND quota_pct < 20 THEN 'improving'
        WHEN ma3 IS NOT NULL AND quota_pct > 35 THEN 'worsening'
        ELSE 'stable'
    END AS classificazione
FROM con_finestre
ORDER BY anno, settore
