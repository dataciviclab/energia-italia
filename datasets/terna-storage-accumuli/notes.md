# terna-storage-accumuli — Note

## Fonte

Terna Download Center, dataset `Storage` (XLSX, foglio `Export`).

- Impianti di accumulo: potenza (MW), capacità (MWh), numero installazioni
- Snapshot annuale (mese 12) — **pubblicato solo dal 2024**
- `years: [2024, 2025]`

## Numeri 2024 (nazionale)

| Voce | Valore |
|---|---:|
| Potenza | 10.008 MW |
| Capacità | 66.153 MWh |
| Installazioni | 740.084 |
| Taglia media | ~13,5 kW |

Le 740mila installazioni con 10 GW indicano una netta prevalenza di
**accumuli residenziali/piccoli**; la capacità media (6,6 h) è da leggere con
cautela perché mescola tecnologie diverse.

Configurazioni 2024 (MW / MWh): Altro 4.351/53.000, Produzione monodirezionali
3.426/6.615, Post-produzione 1.235/4.156, Produzione bidirezionale 996/2.382,
Da verificare 0/0.

## Normalizzazioni

- Regioni Terna **senza trattino** (`Emilia Romagna`, `Friuli Venezia Giulia`,
  `Trentino Alto Adige`, `Valle d'aosta`) → nomi canonici con trattino, come
  gli altri dataset del repo

## Attenzione: 2025 parziale

Il 2025 (639 righe, 22 combinazioni regione×fonte, 3 configurazioni) è un
**dato in consolidamento** — le soglie `min_rows` dei mart sono basse per
coprirlo. Da rivedere quando Terna consolida l'anno.

## Mart

- `mart_storage_regione_fonte`: anno × regione × fonte (MW, MWh, installazioni)
- `mart_storage_configurazione`: anno × tipo configurazione (nazionale)
