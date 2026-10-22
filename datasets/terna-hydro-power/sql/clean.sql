-- clean.sql - terna_hydro_power
-- Fonte: Terna Download Center (HydroPower)
-- Produzione idroelettrica per provincia e tipo di impianto.
-- "Impianto idrico" arriva come 'Bacino' / 'Fluente' / 'Serbatoio (compresi
-- eventuali pompaggi)': normalizzato a Bacino/Fluente/Serbatoio.

select
    cast("Anno" as integer) as anno,
    trim(cast("Tipo produzione" as varchar)) as tipo_produzione,
    trim(cast("Regione" as varchar)) as regione,
    trim(cast("Provincia" as varchar)) as provincia,
    case
        when trim(cast("Impianto idrico" as varchar)) like 'Serbatoio%' then 'Serbatoio'
        else trim(cast("Impianto idrico" as varchar))
    end as tipo_impianto,
    cast("Produzione (GWh)" as double) as produzione_gwh
from raw_input
where try_cast("Anno" as integer) is not null
  and trim(cast("Regione" as varchar)) <> ''
  and trim(cast("Provincia" as varchar)) <> ''
