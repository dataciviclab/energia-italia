-- mart.sql - terna_capacita_rinnovabile - Capacity installata per regione/fonte (per anno)
-- Il toolkit esegue questo SQL per ogni anno separatamente.

WITH base AS (
    SELECT
        anno,
        regione,
        fonti,
        SUM(potenza_mw) AS potenza_totale_mw,
        COUNT(*) AS record_count
    FROM clean_input
    WHERE tipo_capacita = 'Netta'
    GROUP BY anno, regione, fonti
),
totali AS (
    SELECT anno, regione, SUM(potenza_totale_mw) AS totale_regionale_mw
    FROM base GROUP BY anno, regione
)
SELECT
    b.anno,
    b.regione,
    b.fonti,
    b.potenza_totale_mw,
    b.record_count,
    ROUND(b.potenza_totale_mw / NULLIF(t.totale_regionale_mw, 0) * 100, 2) AS quota_fonte_pct,
    RANK() OVER (ORDER BY t.totale_regionale_mw DESC) AS ranking_capacity
FROM base b
JOIN totali t ON b.anno = t.anno AND b.regione = t.regione
ORDER BY ranking_capacity, b.fonti
