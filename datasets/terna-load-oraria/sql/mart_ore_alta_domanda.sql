-- mart_ore_alta_domanda.sql
-- Ore equivalenti sopra soglie di domanda (zona 'Italy'): quante ore il sistema
-- sta sopra 40/45/50/55 GW. Le ore sono la somma dei passi (15') sopra soglia.

with soglie as (
    select unnest([40, 45, 50, 55]) as soglia_gw
)
select
    c.anno,
    c.tipo_carico,
    s.soglia_gw,
    round(sum(case when c.carico_mw >= s.soglia_gw * 1000 then c.passo_ore else 0 end), 1) as ore
from clean_input c
cross join soglie s
where c.zona = 'Italy'
group by c.anno, c.tipo_carico, s.soglia_gw
order by c.anno, c.tipo_carico, s.soglia_gw
