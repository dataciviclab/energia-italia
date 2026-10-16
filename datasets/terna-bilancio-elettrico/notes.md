# terna-bilancio-elettrico — Note

## Truncation pageSize (fix 2026-10-16)

L'API Download Center Terna pagina gli export xlsx con `pageSize` (default 100).
Con `pageSize=100` il dataset arrivava a **100 paesi** (alfabetico A→Kuwait, tagliato
a metà): mancavano tutti i paesi da L a Z e `mart_confronto_ue` usciva a 9/15 paesi UE.

- `pageSize=500` restituisce i **209 paesi** completi (verificato: fino a Zimbabwe).
- I dataset sorella con pageSize 500–5000 non avevano il problema — pattern già noto
  nel repo (vedi terna-capacita-rinnovabile: "pageSize aumentato da 1160 a 5000").
- **2024/2025 non ancora pubblicati** dalla fonte (file vuoti con filterMonth=12,
  verificato 2026-10-16): anni fermi a [2022, 2023].

## Shape

- **Fonte**: TERNA Download Center, dataset `ElectricityBalance`
- **Formato**: XLSX, foglio `Export`, footer "Applied filters" da skippare in clean
- **Granularità**: annuale, per nazione (~209 paesi)
- **Nota**: è un dataset di confronto internazionale, non il bilancio italiano
