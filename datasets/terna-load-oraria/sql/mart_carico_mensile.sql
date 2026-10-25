-- mart_carico_mensile.sql
-- Domanda mensile nazionale (zona 'Italy'): stagionalita'.

select
    anno,
    month(data_ora) as mese,
    tipo_carico,
    round(sum(carico_mw * passo_ore) / 1e6, 2) as energia_twh,
    round(avg(carico_mw) / 1000, 2) as media_gw
from clean_input
where zona = 'Italy'
group by anno, month(data_ora), tipo_carico
order by anno, mese, tipo_carico
