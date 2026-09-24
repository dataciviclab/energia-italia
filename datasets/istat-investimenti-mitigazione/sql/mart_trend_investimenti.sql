-- mart_trend_investimenti.sql
-- Trend investimenti per classe CEPA: primo/ultimo anno, CAGR, classificazione

WITH annuale AS (
    SELECT
        year,
        cep_class,
        SUM(obs_value) AS investimenti_mln_eur
    FROM clean_input
    GROUP BY year, cep_class
),
primo_ultimo AS (
    SELECT
        cep_class,
        FIRST_VALUE(investimenti_mln_eur) OVER w AS primo_val,
        FIRST_VALUE(year) OVER w AS anno_primo,
        LAST_VALUE(investimenti_mln_eur) OVER w AS ultimo_val,
        LAST_VALUE(year) OVER w AS anno_ultimo
    FROM annuale
    WINDOW w AS (PARTITION BY cep_class ORDER BY year
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
SELECT DISTINCT
    cep_class,
    anno_primo,
    primo_val,
    anno_ultimo,
    ultimo_val,
    ROUND((ultimo_val - primo_val) / NULLIF(primo_val, 0) * 100, 2) AS delta_pct,
    ROUND(
        POWER(
            ultimo_val / NULLIF(primo_val, 0),
            1.0 / NULLIF(anno_ultimo - anno_primo, 0)
        ) - 1, 4
    ) AS cagr_annuale,
    CASE
        WHEN ultimo_val > primo_val THEN 'growing'
        WHEN ultimo_val < primo_val * 0.95 THEN 'declining'
        ELSE 'stable'
    END AS classificazione
FROM primo_ultimo
ORDER BY delta_pct DESC
