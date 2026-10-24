-- mart_profilo_orario.sql
-- Profilo medio per ora del giorno e fonte (GW medi).
-- Pesa ogni GIORNO allo stesso modo: prima media per (anno, giorno, ora),
-- poi media dei giorni. Cosi' la granularita' del clean (oraria nel 2019-2024,
-- ogni 15 minuti nel 2025) non altera i pesi tra anni.

with per_giorno as (
    select
        anno,
        cast(data_ora as date) as giorno,
        hour(data_ora) as ora,
        fonte,
        avg(generazione_gw) as gw_ora
    from clean_input
    group by anno, cast(data_ora as date), hour(data_ora), fonte
)
select
    ora,
    fonte,
    round(avg(gw_ora), 2) as media_gw
from per_giorno
group by ora, fonte
order by ora, fonte
