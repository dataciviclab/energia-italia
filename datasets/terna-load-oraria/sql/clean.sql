-- clean.sql - terna_load_oraria
-- Fonte: Terna Download Center (TotalLoad + MarketLoad), CSV.
-- Due sorgenti distinte dal campo iniettato `tipo_carico` (total / market).
-- Il CSV usa la virgola sia come delimitatore sia come separatore decimale:
-- 7 campi per riga (data, carico int, carico dec, previsione int, previsione dec,
-- zona, scarto). Tutto VARCHAR: gli zeri iniziali della parte decimale sono
-- significativi.
-- Passo 15 minuti -> `passo_ore` calcolato come moda dell'intervallo reale.

with base as (
    select
        cast(data_ora as timestamp) as data_ora,
        year(cast(data_ora as timestamp)) as anno,
        trim(tipo_carico) as tipo_carico,
        trim(zona) as zona,
        cast_double(carico_int || '.' || carico_dec) as carico_mw,
        cast_double(previsione_int || '.' || previsione_dec) as previsione_mw
    from raw_input
    where carico_int is not null
      and zona is not null
      and trim(zona) <> ''
),
delta as (
    select
        anno,
        tipo_carico,
        zona,
        date_diff(
            'second',
            lag(data_ora) over (partition by anno, tipo_carico, zona order by data_ora),
            data_ora
        ) as ds
    from base
),
passo as (
    select anno, tipo_carico, zona, mode(ds) as passo_secondi
    from delta
    where ds is not null
    group by anno, tipo_carico, zona
)
select
    b.data_ora,
    b.anno,
    b.tipo_carico,
    b.zona,
    b.carico_mw,
    b.previsione_mw,
    round(p.passo_secondi / 3600.0, 4) as passo_ore
from base b
join passo p using (anno, tipo_carico, zona)
