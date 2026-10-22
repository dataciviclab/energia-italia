-- mart_storage_regione_fonte.sql
-- Potenza, capacita' e installazioni di accumulo per anno, regione e fonte.

select
    anno,
    regione,
    fonte,
    round(sum(potenza_mw), 3) as potenza_mw,
    round(sum(capacita_mwh), 3) as capacita_mwh,
    sum(n_installazioni) as n_installazioni
from clean_input
group by anno, regione, fonte
order by anno desc, regione, fonte
