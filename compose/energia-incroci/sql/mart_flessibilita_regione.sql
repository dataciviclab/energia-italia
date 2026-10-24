-- mart_flessibilita_regione.sql
-- Flessibilita' del sistema per regione, anno 2024 (unico con dati di accumulo).
-- Unisce: accumuli (storage), VRE installata (capacita) e produzione VRE
-- (per-fonte), idro per tipo impianto (hydro).
-- NOTA: la VRE e' ricalcolata dai support, non letta da mart_capacity_factor
-- (evita la dipendenza dall'ordine delle tabelle dello stesso run).

WITH storage AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(potenza_mw) AS accumulo_mw,
        SUM(capacita_mwh) AS accumulo_mwh,
        SUM(n_installazioni) AS n_installazioni
    FROM read_parquet('{support.storage.clean}')
    GROUP BY 1, 2
),
vre_cap AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(potenza_mw) AS vre_mw
    FROM read_parquet('{support.capacita.clean}')
    WHERE tipo_capacita = 'Netta' AND fonti IN ('Eolico', 'Fotovoltaico')
    GROUP BY 1, 2
),
vre_prod AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(produzione_gwh) AS vre_gwh
    FROM read_parquet('{support.fonte.clean}')
    WHERE tipo_produzione = 'Netta' AND fonte IN ('Eolico', 'Fotovoltaico')
    GROUP BY 1, 2
),
idro AS (
    SELECT
        anno,
        CASE WHEN regione = 'Valle D''Aosta' THEN 'Valle d''Aosta' ELSE regione END AS regione,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Serbatoio') AS idro_serbatoio_gwh,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Bacino') AS idro_bacino_gwh,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Fluente') AS idro_fluente_gwh
    FROM read_parquet('{support.hydro.clean}')
    WHERE tipo_produzione = 'Netta'
    GROUP BY 1, 2
)
SELECT
    s.anno,
    s.regione,
    ROUND(s.accumulo_mw, 1) AS accumulo_mw,
    ROUND(s.accumulo_mwh, 1) AS accumulo_mwh,
    s.n_installazioni,
    ROUND(vc.vre_mw, 1) AS vre_mw,
    ROUND(vp.vre_gwh / 1000, 2) AS vre_twh,
    ROUND(i.idro_serbatoio_gwh / 1000, 2) AS idro_serbatoio_twh,
    ROUND(i.idro_bacino_gwh / 1000, 2) AS idro_bacino_twh,
    ROUND(i.idro_fluente_gwh / 1000, 2) AS idro_fluente_twh,
    ROUND(s.accumulo_mwh / NULLIF(vc.vre_mw, 0), 2) AS mwh_accumulo_per_mw_vre,
    ROUND(s.accumulo_mwh / NULLIF(s.accumulo_mw, 0), 1) AS ore_accumulo,
    ROUND(
        100.0 * i.idro_serbatoio_gwh
        / NULLIF(i.idro_serbatoio_gwh + i.idro_bacino_gwh + i.idro_fluente_gwh, 0), 1
    ) AS quota_idro_serbatoio_pct
FROM storage s
LEFT JOIN vre_cap vc USING (anno, regione)
LEFT JOIN vre_prod vp USING (anno, regione)
LEFT JOIN idro i USING (anno, regione)
ORDER BY s.anno, s.regione
