-- mart_mix_annuale.sql
-- Energia annua per fonte (GW * passo orario) e quota sul totale.
-- Cross-check possibile con `terna_elettricita_per_fonte` (annuale).

select
    anno,
    fonte,
    round(sum(generazione_gw * passo_ore), 1) as gwh,
    round(100.0 * sum(generazione_gw * passo_ore)
          / sum(sum(generazione_gw * passo_ore)) over (partition by anno), 1) as quota_pct
from clean_input
group by anno, fonte
order by anno, fonte
