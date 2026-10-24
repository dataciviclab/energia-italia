# terna-hydro-power — Note

## Fonte

Terna Download Center, dataset `HydroPower` (XLSX, foglio `Export`).

- Produzione idroelettrica per provincia e **tipo di impianto**
- Serie **2000-2024** (2025 non ancora pubblicato, escluso dagli `years`)
- Footer "Applied filters" filtrato in clean

## Granularità e normalizzazioni

- Righe: provincia × tipo produzione (Lorda/Netta) × tipo impianto
- `Impianto idrico` arriva come `Bacino` / `Fluente` /
  `Serbatoio (compresi eventuali pompaggi)` → normalizzato a `Serbatoio`
- Regioni già con trattino (coerenti con gli altri dataset)

## Mart

`mart_idro_tipo_impianto`: anno × regione × tipo_produzione × tipo_impianto,
produzione GWh (somma province).

## Cross-check 2024 (da tenere presente)

| Voce | GWh |
|---|---:|
| HydroPower Lorda | 54.757 |
| HydroPower Netta | 53.976 |
| per-fonte Idrico (Lorda = Netta) | 54.757 |

Il dataset `per-fonte` riporta lo **stesso valore** per Lorda e Netta
sull'idrico; `HydroPower` distingue davvero (Netta ~0,8 TWh in meno). Questo
dataset aggiunge quindi la distinzione Lorda/Netta che per-fonte non ha.

## Perché vale la pena

Il **tipo di impianto** (bacino/fluente/serbatoio) è la dimensione di
flessibilità: serbatoio e bacino sono accumuli naturali, il fluente no.
Alimenta l'analisi di flessibilità insieme al dataset storage.
