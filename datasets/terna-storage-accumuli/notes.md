# terna-storage-accumuli — Note

## Fonte

Terna Download Center, dataset `Storage` (XLSX, foglio `Export`).

- Impianti di accumulo: potenza (MW), capacità (MWh), numero installazioni
- Snapshot annuale (mese 12) — **pubblicato solo dal 2024**
- `years: [2024]`

## ⚠️ Il file 2025 escluso (semantica diversa)

Il file `2025-12` **non è uno stock cumulato**: 82,97 MW / 155,73 MWh /
11.263 installazioni contro i 10.008 MW / 66.153 MWh / 740.084 del 2024.
Sembra un **incremento/parziale** (copre 22 combinazioni regione×fonte vs 49),
non lo stato a fine anno. Mescolarlo al 2024 darebbe una serie sbagliata:
escluso dagli `years`, da rivalutare quando Terna consolida.

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

Il 2025 è **escluso** dagli `years` (vedi sopra): il file non è cumulato.

## Mart

- `mart_storage_regione_fonte`: anno × regione × fonte (MW, MWh, installazioni)
- `mart_storage_configurazione`: anno × tipo configurazione (nazionale)
