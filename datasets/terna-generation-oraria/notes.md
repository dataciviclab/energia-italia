# terna-generation-oraria — Note

## Fonte

Terna Download Center, dataset `ActualGeneration` (CSV).

- Generazione per fonte: Thermal, Hydro, Geothermal, Photovoltaic,
  Self-consumption, Wind
- **Valori in GW** (da confermare con Terna)
- Anni: **2019-2025** (2018 e prima vuoti; 2026 escluso perché parziale)

## ⚠️ Quirk del CSV (importante)

La virgola è **sia delimitatore sia separatore decimale**, quindi ogni riga ha
5 campi:

```
Date,Actual Generation,Primary Source
2024-12-31T23:00:00,15,210000,Thermal,
                      └15.210000 GW┘
```

Il clean legge tutto come **VARCHAR** e ricompone: `parte_intera || '.' || parte_decimale`.
Gli **zeri iniziali sono significativi** (es. `0.040000`, non `0.40000`):
leggere la parte decimale come numero la corromperebbe di 10×.

## Granularità variabile

- **2019-2024: oraria** (~52.500 righe/anno = 8.760 h × 6 fonti)
- **2025: ogni 15 minuti** (~210.000 righe/anno)

Il clean calcola `passo_ore` come **moda dell'intervallo** tra campioni per
anno×fonte (1.0 h oppure 0.25 h), così i mart calcolano l'energia
(`GW × passo_ore`) senza assumere la granularità.

## Mart

- `mart_mix_annuale`: energia annua per fonte + quota % (per anno)
- `mart_mix_mensile`: energia mensile per fonte (stagionalità)
- `mart_profilo_orario`: GW medi per ora del giorno e fonte

## Cross-check 2024 vs `per-fonte` (annuale)

| Fonte | Orario (TWh) | Annuale (TWh) | Note |
|---|---:|---:|---|
| Wind | 22,0 | 22,3 | ✅ coerente |
| Geothermal | 5,3 | 5,7 | ✅ coerente |
| Hydro | 51,6 | 54,8 | −6% (misura vs statistica) |
| Thermal | 123,7 | 152,1 | la differenza è l'**autoconsumo** |
| Photovoltaic | 27,6 | 36,0 | idem: il FV in autoconsumo è in `Self-consumption` (33 TWh) |

`ActualGeneration` misura il lato rete e **separa `Self-consumption`** (33 TWh
nel 2024); il dataset annuale `per-fonte` la include diversamente. Confrontare
i due richiede questa consapevolezza.
