-- clean.sql for istat_subsidi_ambientali
-- ISTAT 72_1028: sussidi ambientali per dominio CEPA e settore NACE

SELECT
    FREQ AS freq,
    REF_AREA AS ref_area,
    DATA_TYPE_AGGR AS data_type,
    BRKDW_INDUSTRY_NACE_REV2 AS nace_r2,
    CEP_CLASS AS cep_class,
    CAST(TIME_PERIOD AS INTEGER) AS year,
    CAST(OBS_VALUE AS DOUBLE) AS obs_value,
    UNIT_MEAS AS unit
FROM raw_input
WHERE FREQ = 'A'
  AND REF_AREA = 'IT'
  AND OBS_VALUE IS NOT NULL