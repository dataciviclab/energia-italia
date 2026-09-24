-- mart_copertura_fonte_regione.sql - Copertura domanda per fonte e regione

SELECT
    anno,
    regione,
    fonte,
    ROUND(SUM(copertura_gwh), 2) AS copertura_gwh
FROM clean_input
GROUP BY anno, regione, fonte
ORDER BY anno, regione, copertura_gwh DESC
