-- clean.sql - terna_storage_accumuli
-- Fonte: Terna Download Center (Storage)
-- Impianti di accumulo per regione, provincia, fonte, configurazione e tensione.
-- Le regioni Terna arrivano senza trattino ("Emilia Romagna", "Valle d'aosta"):
-- normalizzate ai nomi canonici usati negli altri dataset del repo.

select
    cast("Anno" as integer) as anno,
    cast("Mese" as integer) as mese,
    trim(cast("Zona mercato" as varchar)) as zona_mercato,
    case trim(cast("Regione" as varchar))
        when 'Emilia Romagna' then 'Emilia-Romagna'
        when 'Friuli Venezia Giulia' then 'Friuli-Venezia Giulia'
        when 'Trentino Alto Adige' then 'Trentino-Alto Adige'
        when 'Valle d''aosta' then 'Valle d''Aosta'
        else trim(cast("Regione" as varchar))
    end as regione,
    trim(cast("Provincia" as varchar)) as provincia,
    trim(cast("Classe di potenza dell'impianto" as varchar)) as classe_potenza,
    trim(cast("Tipo configurazione" as varchar)) as tipo_configurazione,
    trim(cast("Fonte" as varchar)) as fonte,
    trim(cast("Livello tensione" as varchar)) as livello_tensione,
    cast("Potenza attiva nominale (MW)" as double) as potenza_mw,
    cast("Capacità (MWh)" as double) as capacita_mwh,
    cast("Numero installazioni" as integer) as n_installazioni
from raw_input
where try_cast("Anno" as integer) is not null
  and trim(cast("Regione" as varchar)) <> ''
