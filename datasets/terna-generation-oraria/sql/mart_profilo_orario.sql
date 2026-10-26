-- mart_profilo_orario.sql
-- Profilo medio per ora del giorno e fonte (GW medi).
-- Pesa ogni GIORNO allo stesso modo: prima media per (anno, giorno, ora),
-- poi media dei giorni. Cosi' la granularita' del clean (oraria nel 2019-2024,
-- ogni 15 minuti nel 2025) non altera i pesi tra anni.
-- `anno` e' costante nel file per-anno, ma serve a rendere leggibile il mart
-- quando i consumer lo leggono via il glob del registry.

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
    anno,
    ora,
    fonte,
    round(avg(gw_ora), 2) as media_gw
from per_giorno
group by anno, ora, fonte
order by anno, ora, fonte
