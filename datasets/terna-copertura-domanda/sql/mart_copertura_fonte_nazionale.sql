-- mart_copertura_fonte_nazionale.sql - Copertura domanda per fonte (totale nazionale)

WITH totale AS (
    SELECT anno, SUM(copertura_gwh) AS totale_gwh
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno,
    c.fonte,
    ROUND(SUM(c.copertura_gwh), 2) AS copertura_gwh,
    ROUND(SUM(c.copertura_gwh) / NULLIF(t.totale_gwh, 0) * 100, 2) AS quota_pct
FROM clean_input c
JOIN totale t ON c.anno = t.anno
GROUP BY c.anno, c.fonte, t.totale_gwh
ORDER BY c.anno, quota_pct DESC
