-- mart_ranking_eu.sql
-- Ranking Italia tra paesi EU per % rinnovabili

WITH classifica AS (
    SELECT
        year,
        geo,
        value AS rinnovabili_pct,
        RANK() OVER (PARTITION BY year ORDER BY value DESC) AS rank
    FROM clean_input
    WHERE geo IN ('IT', 'DE', 'FR', 'ES', 'PL', 'NL', 'BE', 'AT', 'SE', 'DK', 'FI', 'IE', 'PT', 'GR', 'CZ', 'RO', 'HU', 'BG', 'SK', 'SI', 'HR', 'LT', 'LV', 'EE', 'CY', 'LU', 'MT')
)
SELECT * FROM classifica WHERE geo = 'IT' ORDER BY year