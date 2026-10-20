-- mart_lcoe_tecnologia.sql
-- LCOE per tecnologia e anno, con variazione rispetto al 2010 e ranking di costo.

WITH base AS (
    SELECT tecnologia, anno, lcoe_usd_kwh
    FROM clean_input
),
riferimento AS (
    SELECT tecnologia, lcoe_usd_kwh AS lcoe_2010
    FROM base
    WHERE anno = 2010
)
SELECT
    b.tecnologia,
    b.anno,
    b.lcoe_usd_kwh,
    ROUND(
        100.0 * (b.lcoe_usd_kwh - r.lcoe_2010) / NULLIF(r.lcoe_2010, 0), 1
    ) AS variazione_vs_2010_pct,
    RANK() OVER (PARTITION BY b.anno ORDER BY b.lcoe_usd_kwh) AS rank_costo
FROM base b
LEFT JOIN riferimento r USING (tecnologia)
ORDER BY b.anno, b.lcoe_usd_kwh
