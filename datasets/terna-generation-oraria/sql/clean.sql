-- clean.sql - terna_generation_oraria
-- Fonte: Terna Download Center (ActualGeneration), CSV.
-- Il CSV usa la virgola sia come delimitatore sia come separatore decimale,
-- quindi ogni riga ha 5 campi: data, parte intera, parte decimale, fonte, scarto
-- (es. "2024-12-31T23:00:00,15,210000,Thermal," = 15.210000 GW Thermal).
-- Letti come VARCHAR e ricomposti qui; gli zeri iniziali della parte decimale
-- sono significativi.
-- Valori in GW. La granularita' cambia: 2019-2024 oraria, 2025 ogni 15 minuti.
-- `passo_ore` (intervallo reale per anno/fonte) permette ai mart di calcolare
-- l'energia senza assumere la granularita'.

with base as (
    select
        cast(data_ora as timestamp) as data_ora,
        year(cast(data_ora as timestamp)) as anno,
        trim(fonte) as fonte,
        cast_double(parte_intera || '.' || parte_decimale) as generazione_gw
    from raw_input
    where fonte is not null
      and trim(fonte) <> ''
      and parte_intera is not null
),
delta as (
    select
        anno,
        fonte,
        date_diff(
            'second',
            lag(data_ora) over (partition by anno, fonte order by data_ora),
            data_ora
        ) as ds
    from base
),
passo as (
    select anno, fonte, mode(ds) as passo_secondi
    from delta
    where ds is not null
    group by anno, fonte
)
select
    b.data_ora,
    b.anno,
    b.fonte,
    b.generazione_gw,
    round(p.passo_secondi / 3600.0, 4) as passo_ore
from base b
join passo p using (anno, fonte)
