# terna-elettricita-per-fonte

Dataset per il progetto energia-italia.

## Stato
- [ ] Run pipeline completa
- [ ] Dashboard Streamlit
- [ ] Analisi pubblica

## Qualità dati — anomalie note nella fonte

Verificate sui raw Terna (2026-10-17). I valori sono fedeli alla fonte: non
vengono corretti in clean (no imputazione). Chi aggrega questa serie deve
considerare questi punti:

- **2017 produzione Netta parziale**: Eolico 4.861 GWh con sole 43 province
  (~96 nel 2016, reale ~17.800 GWh); Fotovoltaico 193 GWh (reale ~19.000).
  Il file Terna 2017 è compromesso su queste due fonti.
- **2000-2007 valori FV/Eolico molto bassi**: copertura provinciale parziale
  nell'era di bassa penetrazione (impatto trascurabile sui totali nazionali
  moderni).

Il compose `energia-incroci` marca questi punti con `cf_sospetto` nel mart
`mart_capacity_factor` (range fisici plausibili per fonte).
