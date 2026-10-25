-- mart_profilo_carico.sql
-- Profilo medio della domanda per ora del giorno (zona 'Italy').
-- Ogni giorno pesa allo stesso modo: media per (anno, giorno, ora) prima di
-- mediare sui giorni.

with per_giorno as (
    select
        anno,
        cast(data_ora as date) as giorno,
        hour(data_ora) as ora,
        tipo_carico,
        avg(carico_mw) as mw_ora
    from clean_input
    where zona = 'Italy'
    group by anno, cast(data_ora as date), hour(data_ora), tipo_carico
)
select
    ora,
    tipo_carico,
    round(avg(mw_ora) / 1000, 2) as media_gw
from per_giorno
group by ora, tipo_carico
order by ora, tipo_carico
