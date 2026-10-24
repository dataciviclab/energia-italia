-- mart_mix_mensile.sql
-- Energia mensile per fonte (stagionalita' del mix).

select
    anno,
    month(data_ora) as mese,
    fonte,
    round(sum(generazione_gw * passo_ore), 1) as gwh
from clean_input
group by anno, month(data_ora), fonte
order by anno, mese, fonte
