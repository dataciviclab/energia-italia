# terna-capacita-rinnovabile — Note

## Espansione serie storica 2026-06-06

Da 2 anni (2023-2024) a 10 anni (2015-2024).

L'API Terna supporta tutti gli anni con `filterYear={year}`. `pageSize` aumentato da 1160 a 5000 per sicurezza.

Run verificati: 2015, 2024 raw+clean+mart OK.

## Espansione 2000-2024 (2026-10-16)

La fonte ha dati dal **2000** (verificato: 1999 vuoto). Estesi gli anni da 2015 a 2000.
I primi anni hanno un parco più piccolo (~830 righe vs ~1100 recenti): `min_rows`
abbassato da 1000 a 800 come floor anti-troncatura.
