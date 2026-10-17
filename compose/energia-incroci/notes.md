# energia-incroci — Note

Compose mart-only (ADR-005): incroci cross-dataset sui clean Terna di questo repo.

## Tabelle

- `mart_capacity_factor`: produzione netta (per-fonte) ÷ potenza netta (capacita-rinnovabile),
  per regione × fonte × anno (2000-2024, 4 FER). Approssimazione standard
  (produzione annuale su snapshot di fine anno).
- `mart_intensita_regionale`: emissioni di produzione (emissioni-co2) ÷ copertura locale
  della domanda escluso saldo import/export (copertura-domanda) + quota rinnovabile,
  per regione × anno (2005-2024). Coerenza: media ponderata 2023 = 250 g/kWh
  vs 257 del bilancio internazionale (confini leggermente diversi).

## Flag `cf_sospetto`

Range fisici plausibili per fonte (FV 3-25%, Eolico 8-45%, Idrico 3-60%,
Geotermico 40-100%). Marca anomalie della **fonte Terna** (valori fedeli in
clean, non corretti):

- 2009 FV capacità 88 MW (reale ~1.160)
- 2017 FV produzione 193 GWh (reale ~19.000)
- 2017 Eolico produzione 4.861 GWh, 43 province su ~96 (reale ~17.800)

Dettagli nei notes/README dei dataset support (`terna-elettricita-per-fonte`,
`terna-capacita-rinnovabile`).

## Convenzioni

- Anno sintetico `2026` nel config: output a livello dataset
  (`out/data/mart/energia_incroci/2026/`), i dati reali sono nelle tabelle.
- Run: `toolkit run mart --config compose/energia-incroci/dataset.yml`
  (richiede i clean+mart dei support già eseguiti).
- Normalizzazione `Valle D'Aosta` → `Valle d'Aosta` (case inconsistency tra anni
  in capacita-rinnovabile).
