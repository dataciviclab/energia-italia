-- mart_carico_zona.sql
-- Domanda per zona di mercato (esclusa 'Italy', che e' il totale nazionale).

select
    anno,
    zona,
    tipo_carico,
    round(sum(carico_mw * passo_ore) / 1e6, 2) as energia_twh,
    round(avg(carico_mw) / 1000, 2) as media_gw,
    round(max(carico_mw) / 1000, 2) as max_gw
from clean_input
where zona <> 'Italy'
group by anno, zona, tipo_carico
order by anno, zona, tipo_carico
