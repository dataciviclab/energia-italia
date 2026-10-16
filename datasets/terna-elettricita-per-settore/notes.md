# note - terna-electrical-energy-by-sector

## Shape

- **Fonte**: TERNA Download Center, dataset `ElectricalEnergy`
- **Formato**: XLSX, foglio `Export`
- **Colonne**: Anno, Regione, Provincia, Settore, Consumo (GWh)
- **Settori**: Domestico, Industria, Servizi, Agricoltura
- **Copertura**: 2000-2024, tutte le province italiane
- **Granularità**: annuale, per provincia e settore

## Note

- **Standardizzato nel clean**: il clean.sql aggrega con `SUM GROUP BY provincia, settore` — tutti gli anni hanno la stessa granularità (~428 righe/anno). Gli anni early arrivano raw disaggregati (fino a ~12k righe, verificato sul 2015), ma il clean normalizza.
- **pageSize=500000** nell'API per non troncare anni con molti dati. La riga di footer "Applied filters" viene filtrata dal `clean.sql` (TRY_CAST su Anno).
- **Regressioni pageSize (fix 2026-10-16)**: la config era tornata a `http_file` con `pageSize=100` → export limitati a 100 righe (5-7 regioni, 25 province). Ripristinato `pageSize=500000`: 428 righe/anno, 20 regioni, 107 province (verificato sul 2024).
- **Espansione 2000-2024 (2026-10-16)**: la fonte ha dati dal 2000; estesi gli anni da 2015. Gli anni early hanno ~412-440 righe clean.
- Si incrocia perfettamente con ElectricityBySource (produzione) per calcolare autoconsumo province
- Incrociabile con ISPRA emissioni GHG per impronta carbonica per settore
- Incrociabile con ISTAT popolazione per consumo pro-capite per provincia
