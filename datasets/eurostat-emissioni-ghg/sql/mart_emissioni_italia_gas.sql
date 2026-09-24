-- mart_emissioni_italia_gas.sql
-- Emissioni totali Italia per gas serra con trend e classificazione
--
-- Metriche aggiunte:
-- - baseline 1990 (primo anno disponibile per il gas)
-- - media mobile 3 e 5 anni
-- - YoY % (variazione anno su anno)
-- - target UE -55% 2030 vs 1990 (per gas GHG totale)
-- - classificazione: improving / worsening / stable

WITH raw AS (
    SELECT
        year,
        airpol AS gas,
        SUM(value) AS emissioni_t
    FROM clean_input
    WHERE geo = 'IT'
      AND unit = 'T'
      AND nace_r2 = 'TOTAL'
    GROUP BY year, airpol
),
baseline AS (
    SELECT gas, MIN(year) AS baseline_year, SUM(emissioni_t) AS baseline_t
    FROM raw
    GROUP BY gas
),
con_finestre AS (
    SELECT
        r.year,
        r.gas,
        r.emissioni_t,
        b.baseline_year,
        b.baseline_t,
        LAG(r.emissioni_t) OVER (PARTITION BY r.gas ORDER BY r.year) AS prev_t,
        ROUND(AVG(r.emissioni_t) OVER (
            PARTITION BY r.gas ORDER BY r.year ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 0) AS ma3,
        ROUND(AVG(r.emissioni_t) OVER (
            PARTITION BY r.gas ORDER BY r.year ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 0) AS ma5
    FROM raw r
    JOIN baseline b ON r.gas = b.gas
)
SELECT
    year,
    gas,
    emissioni_t,
    baseline_year,
    baseline_t,
    ROUND(emissioni_t - baseline_t, 0) AS delta_vs_baseline_t,
    ROUND((emissioni_t - baseline_t) / NULLIF(baseline_t, 0) * 100, 1) AS delta_vs_baseline_pct,
    ROUND(emissioni_t - prev_t, 0) AS yoy_t,
    ROUND((emissioni_t - prev_t) / NULLIF(prev_t, 0) * 100, 2) AS yoy_pct,
    ma3,
    ma5,
    CASE
        WHEN gas = 'GHG' AND baseline_t > 0
            THEN ROUND(emissioni_t / NULLIF(baseline_t, 0) * 100, 1)
        ELSE NULL
    END AS pct_vs_1990,
    CASE
        WHEN gas = 'GHG' AND baseline_t > 0 AND ma3 < baseline_t * 0.85
        THEN 'improving'
        WHEN gas = 'GHG' AND baseline_t > 0 AND ma3 > baseline_t * 1.05
        THEN 'worsening'
        WHEN gas = 'GHG' THEN 'stable'
        ELSE NULL
    END AS classificazione
FROM con_finestre
ORDER BY year, gas