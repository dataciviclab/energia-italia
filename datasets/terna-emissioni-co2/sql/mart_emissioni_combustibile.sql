-- mart_emissioni_combustibile.sql - Emissioni CO2 per combustibile (totale nazionale)

WITH totale AS (
    SELECT anno, SUM(emissioni_mt) AS totale_mt
    FROM clean_input
    WHERE emissioni_mt IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.combustibile,
    ROUND(SUM(c.emissioni_mt), 2) AS emissioni_mt,
    ROUND(SUM(c.emissioni_mt) / NULLIF(t.totale_mt, 0) * 100, 2) AS quota_pct,
    ROUND(SUM(c.produzione), 2) AS produzione
FROM clean_input c
JOIN totale t ON c.anno = t.anno
WHERE c.emissioni_mt IS NOT NULL
GROUP BY c.anno, c.combustibile, t.totale_mt
ORDER BY c.anno, emissioni_mt DESC
