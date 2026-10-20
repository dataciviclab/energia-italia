-- mart_capacity_factor.sql
-- Capacity factor delle FER per regione, fonte e anno.
-- produzione netta (per-fonte) / (potenza netta installata * 8.760h).
-- Nota: la potenza e' uno snapshot di fine anno, la produzione e' annuale —
-- l'indicatore e' un'approssimazione standard, non un bilancio orario.

WITH prod AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        fonte,
        SUM(produzione_gwh) AS produzione_gwh
    FROM read_parquet('{support.fonte.clean}')
    WHERE tipo_produzione = 'Netta'
      AND fonte IN ('Eolico', 'Fotovoltaico', 'Geotermoelettrico', 'Idrico')
    GROUP BY 1, 2, 3
),
cap AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        fonti AS fonte,
        SUM(potenza_mw) AS potenza_mw
    FROM read_parquet('{support.capacita.clean}')
    WHERE tipo_capacita = 'Netta'
      AND fonti IN ('Eolico', 'Fotovoltaico', 'Geotermoelettrico', 'Idrico')
    GROUP BY 1, 2, 3
)
SELECT
    p.anno,
    p.regione,
    p.fonte,
    ROUND(p.produzione_gwh, 1) AS produzione_gwh,
    ROUND(c.potenza_mw, 1) AS potenza_mw,
    ROUND(100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0), 1) AS capacity_factor_pct,
    -- Flag su valori fuori dai range fisici plausibili per fonte:
    -- la fonte Terna ha anomalie note (es. FV 2009 capacita 88 MW,
    -- FV/Eolico 2017 produzione parziale). Il valore resta il dato grezzo.
    CASE
        WHEN p.fonte = 'Fotovoltaico'
             AND (100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) < 3
               OR 100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) > 25) THEN true
        WHEN p.fonte = 'Eolico'
             AND (100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) < 8
               OR 100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) > 45) THEN true
        WHEN p.fonte = 'Idrico'
             AND (100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) < 3
               OR 100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) > 60) THEN true
        WHEN p.fonte = 'Geotermoelettrico'
             AND (100.0 * p.produzione_gwh / NULLIF(c.potenza_mw * 8.76, 0) < 40) THEN true
        ELSE false
    END AS cf_sospetto
FROM prod p
JOIN cap c USING (anno, regione, fonte)
WHERE c.potenza_mw > 0
ORDER BY anno, regione, fonte
