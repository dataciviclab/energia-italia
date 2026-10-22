-- mart_storage_configurazione.sql
-- Totale nazionale di accumuli per anno e tipo di configurazione.

select
    anno,
    tipo_configurazione,
    round(sum(potenza_mw), 3) as potenza_mw,
    round(sum(capacita_mwh), 3) as capacita_mwh,
    sum(n_installazioni) as n_installazioni
from clean_input
group by anno, tipo_configurazione
order by anno desc, tipo_configurazione
