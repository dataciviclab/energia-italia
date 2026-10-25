-- mart_carico_annuale.sql
-- Domanda annua nazionale (zona 'Italy'): energia, medie, picchi e accuratezza
-- della previsione Terna.

select
    anno,
    tipo_carico,
    round(sum(carico_mw * passo_ore) / 1e6, 2) as energia_twh,
    round(avg(carico_mw) / 1000, 2) as media_gw,
    round(max(carico_mw) / 1000, 2) as max_gw,
    round(min(carico_mw) / 1000, 2) as min_gw,
    round(avg(abs(carico_mw - previsione_mw)), 1) as errore_previsione_medio_mw,
    round(quantile_cont(abs(carico_mw - previsione_mw), 0.95), 1) as errore_previsione_p95_mw
from clean_input
where zona = 'Italy'
group by anno, tipo_carico
order by anno, tipo_carico
