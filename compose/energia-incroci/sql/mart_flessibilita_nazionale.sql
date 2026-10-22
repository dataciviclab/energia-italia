-- mart_flessibilita_nazionale.sql
-- Serie nazionale per anno: VRE installata e prodotta, idro per tipo impianto,
-- accumuli (disponibili solo dal 2024). Il join e' FULL OUTER: idro/VRE coprono
-- 2000-2024, gli accumuli 2024-2025.

WITH idro AS (
    SELECT
        anno,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Serbatoio') / 1000 AS idro_serbatoio_twh,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Bacino') / 1000 AS idro_bacino_twh,
        SUM(produzione_gwh) FILTER (WHERE tipo_impianto = 'Fluente') / 1000 AS idro_fluente_twh
    FROM read_parquet('{support.hydro.clean}')
    WHERE tipo_produzione = 'Netta'
    GROUP BY 1
),
vre_cap AS (
    SELECT anno, SUM(potenza_mw) / 1000 AS vre_gw
    FROM read_parquet('{support.capacita.clean}')
    WHERE tipo_capacita = 'Netta' AND fonti IN ('Eolico', 'Fotovoltaico')
    GROUP BY 1
),
vre_prod AS (
    SELECT anno, SUM(produzione_gwh) / 1000 AS vre_twh
    FROM read_parquet('{support.fonte.clean}')
    WHERE tipo_produzione = 'Netta' AND fonte IN ('Eolico', 'Fotovoltaico')
    GROUP BY 1
),
acc AS (
    SELECT
        anno,
        SUM(potenza_mw) / 1000 AS accumulo_gw,
        SUM(capacita_mwh) / 1000 AS accumulo_gwh
    FROM read_parquet('{support.storage.clean}')
    GROUP BY 1
)
SELECT
    COALESCE(i.anno, vc.anno, vp.anno, a.anno) AS anno,
    ROUND(vc.vre_gw, 2) AS vre_gw,
    ROUND(vp.vre_twh, 2) AS vre_twh,
    ROUND(i.idro_serbatoio_twh, 2) AS idro_serbatoio_twh,
    ROUND(i.idro_bacino_twh, 2) AS idro_bacino_twh,
    ROUND(i.idro_fluente_twh, 2) AS idro_fluente_twh,
    ROUND(a.accumulo_gw, 2) AS accumulo_gw,
    ROUND(a.accumulo_gwh, 2) AS accumulo_gwh,
    ROUND(
        100.0 * i.idro_serbatoio_twh
        / NULLIF(i.idro_serbatoio_twh + i.idro_bacino_twh + i.idro_fluente_twh, 0), 1
    ) AS quota_idro_serbatoio_pct
FROM idro i
FULL OUTER JOIN vre_cap vc USING (anno)
FULL OUTER JOIN vre_prod vp USING (anno)
FULL OUTER JOIN acc a USING (anno)
ORDER BY anno
