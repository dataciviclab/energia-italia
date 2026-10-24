-- mart_idro_tipo_impianto.sql
-- Produzione idroelettrica per anno, regione, tipo di produzione e tipo impianto.

select
    anno,
    regione,
    tipo_produzione,
    tipo_impianto,
    round(sum(produzione_gwh), 3) as produzione_gwh
from clean_input
group by anno, regione, tipo_produzione, tipo_impianto
order by anno desc, regione, tipo_produzione, tipo_impianto
