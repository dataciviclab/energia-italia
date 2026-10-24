-- mart_profilo_orario.sql
-- Profilo medio per ora del giorno e fonte (GW medi), su tutto il periodo.
-- Indipendente dalla granularita' (media dei valori istantanei).

select
    hour(data_ora) as ora,
    fonte,
    round(avg(generazione_gw), 2) as media_gw
from clean_input
group by hour(data_ora), fonte
order by ora, fonte
