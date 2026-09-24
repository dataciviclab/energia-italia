#!/usr/bin/env python3
"""
signals.py — Generatore segnali con soglie

Calcola 12 indicatori su 5 dimensioni:
- Emissioni (3): totale, YoY%, quota trasporti
- Rinnovabili (3): quota, gap target, ranking EU
- Mix energetico (2): quota termoelettrico, capacity factor solare
- Finanza verde (2): sussidi/emissione, trend investimenti
- Regionali (2): divario Nord-Sud, regioni sotto target

Output: data/signals/signals.csv + data/reporting/panorama.md
"""

import json
from pathlib import Path

from lab_connectors.duckdb.core import safe_connect

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "data"
CLEAN_DIR = OUT_DIR / "clean"
SIGNALS_DIR = Path(__file__).resolve().parent.parent / "data" / "signals"
REPORTING_DIR = Path(__file__).resolve().parent.parent / "data" / "reporting"
SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
REPORTING_DIR.mkdir(parents=True, exist_ok=True)

# ── Definizione segnali ─────────────────────────────────────────────────────

SIGNALS = [
    # (id, dimensione, label, unita, soglia_warning, soglia_bad, direzione)
    # direzione: "lower_is_better" = valori bassi buoni, "higher_is_better" = valori alti buoni
    ("emissioni_ghg_mt", "emissioni", "Emissioni GHG totali (Mt)", "Mt", None, None, None),
    ("emissioni_yoy_pct", "emissioni", "Variazione emissioni YoY", "%", 0, 5, "lower_is_better"),
    ("quota_emissioni_trasporti", "emissioni", "Quota emissioni trasporti", "%", 25, 30, "lower_is_better"),
    ("rinnovabili_pct", "rinnovabili", "Quota rinnovabili consumo finale", "%", 30, 20, "higher_is_better"),
    ("gap_target_2030_pp", "rinnovabili", "Gap target 2030", "pp", None, 21.5, "lower_is_better"),
    ("ranking_eu", "rinnovabili", "Ranking Italia EU rinnovabili", None, None, 15, "higher_is_better"),
    ("quota_termoelettrico_pct", "mix", "Quota termoelettrico nazionale", "%", 50, 60, "lower_is_better"),
    ("capacity_factor_solare_pct", "mix", "Capacity factor solare nazionale", "%", 12, 8, "higher_is_better"),
    ("sussidi_per_emissione_mt", "finanza", "Sussidi per unita' emissione", "mln/Mt", None, None, None),
    ("investimenti_yoy_pct", "finanza", "Variazione investimenti YoY", "%", 0, -10, "higher_is_better"),
    ("divario_nord_sud_pp", "regionali", "Divario Nord-Sud mix rinnovabili", "pp", 30, 40, "lower_is_better"),
    ("regioni_sotto_target_30pct", "regionali", "Regioni sotto 30% rinnovabili", "n", 10, 15, "lower_is_better"),
]


def _connect():
    """Return a DuckDB connection (caller manages lifecycle via context manager)."""
    return safe_connect()


def _load(con: duckdb.DuckDBPyConnection, alias: str, pattern: str) -> None:
    con.execute(f"CREATE VIEW {alias} AS SELECT * FROM read_parquet('{pattern}')")


def _get_signal(con: duckdb.DuckDBPyConnection, signal_id: str) -> dict:
    """Calcola un singolo segnale dal dataset."""

    if signal_id == "emissioni_ghg_mt":
        row = con.execute("""
            SELECT ROUND(SUM(totale), 1) AS val
            FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet')
            WHERE anno = (SELECT MAX(anno) FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet'))
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "ISPRA ultimo anno disponibile"}

    elif signal_id == "emissioni_yoy_pct":
        row = con.execute("""
            WITH annuale AS (
                SELECT anno, SUM(totale) AS emissioni
                FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet')
                GROUP BY anno ORDER BY anno DESC LIMIT 2
            )
            SELECT ROUND((MAX(emissioni) - MIN(emissioni)) / NULLIF(MIN(emissioni), 0) * 100, 2)
            FROM annuale
        """.format(CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "ISPRA YoY ultimo biennio"}

    elif signal_id == "quota_emissioni_trasporti":
        row = con.execute("""
            SELECT ROUND(100.0 * trasporti / NULLIF(totale, 0), 1)
            FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet')
            WHERE anno = (SELECT MAX(anno) FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet'))
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "ISPRA ultimo anno"}

    elif signal_id == "rinnovabili_pct":
        row = con.execute("""
            SELECT ROUND(value, 1)
            FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet')
            WHERE geo = 'IT' AND year = (SELECT MAX(year) FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet') WHERE geo = 'IT')
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Eurostat ultimo anno"}

    elif signal_id == "gap_target_2030_pp":
        row = con.execute("""
            SELECT ROUND(42.0 - value, 1)
            FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet')
            WHERE geo = 'IT' AND year = (SELECT MAX(year) FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet') WHERE geo = 'IT')
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Target 42% - attuale"}

    elif signal_id == "ranking_eu":
        row = con.execute("""
            WITH classifica AS (
                SELECT year, geo, value,
                    RANK() OVER (PARTITION BY year ORDER BY value DESC) AS rank
                FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet')
                WHERE year = (SELECT MAX(year) FROM read_parquet('{}/eurostat_rinnovabili/*/*.parquet'))
            )
            SELECT rank FROM classifica WHERE geo = 'IT'
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Ranking EU ultimo anno"}

    elif signal_id == "quota_termoelettrico_pct":
        row = con.execute("""
            WITH naz AS (
                SELECT fonte, SUM(copertura_gwh) AS gwh
                FROM read_parquet('{}/terna_consumo_per_fonte/*/*.parquet')
                GROUP BY fonte
            ),
            tot AS (SELECT SUM(gwh) AS totale FROM naz)
            SELECT ROUND(100.0 * n.gwh / t.totale, 1)
            FROM naz n CROSS JOIN tot t
            WHERE n.fonte = 'Termoelettrico tradizionale'
        """.format(CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Terna consumo nazionale"}

    elif signal_id == "capacity_factor_solare_pct":
        row = con.execute("""
            WITH cap AS (
                SELECT SUM(potenza_mw) AS mw
                FROM read_parquet('{}/terna_capacita_rinnovabile/*/*.parquet')
                WHERE tipo_capacita = 'Netta' AND fonti = 'Fotovoltaico'
                AND anno = (SELECT MAX(anno) FROM read_parquet('{}/terna_capacita_rinnovabile/*/*.parquet'))
            ),
            prod AS (
                SELECT SUM(produzione_gwh) AS gwh
                FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet')
                WHERE tipo_produzione = 'Netta' AND fonte = 'Fotovoltaico'
                AND anno = (SELECT MAX(anno) FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet'))
            )
            SELECT ROUND(p.gwh * 1000 / NULLIF(c.mw * 8760, 0) * 100, 1)
            FROM cap c, prod p
        """.format(CLEAN_DIR, CLEAN_DIR, CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Terna ultimo anno"}

    elif signal_id == "sussidi_per_emissione_mt":
        row = con.execute("""
            WITH s AS (
                SELECT SUM(obs_value) AS sussidi
                FROM read_parquet('{}/istat_subsidi_ambientali/*/*.parquet')
                WHERE year = (SELECT MAX(year) FROM read_parquet('{}/istat_subsidi_ambientali/*/*.parquet'))
            ),
            e AS (
                SELECT totale AS emissioni
                FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet')
                WHERE anno = (SELECT MAX(anno) FROM read_parquet('{}/ispra_emissioni_ghg/*/*.parquet'))
            )
            SELECT ROUND(s.sussidi / NULLIF(e.emissioni, 0), 2)
            FROM s, e
        """.format(CLEAN_DIR, CLEAN_DIR, CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "ISTAT sussidi / ISPRA emissioni"}

    elif signal_id == "investimenti_yoy_pct":
        row = con.execute("""
            WITH annuale AS (
                SELECT year, SUM(obs_value) AS val
                FROM read_parquet('{}/istat_investimenti_mitigazione/*/*.parquet')
                GROUP BY year ORDER BY year DESC LIMIT 2
            )
            SELECT ROUND((MAX(val) - MIN(val)) / NULLIF(MIN(val), 0) * 100, 2)
            FROM annuale
        """.format(CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "ISTAT investimenti YoY"}

    elif signal_id == "divario_nord_sud_pp":
        row = con.execute("""
            WITH regioni AS (
                SELECT anno, regione,
                    SUM(CASE WHEN fonte IN ('Fotovoltaico','Eolico','Idrico','Geotermoelettrico','Bioenergie')
                          THEN produzione_gwh ELSE 0 END) AS rin_gwh,
                    SUM(produzione_gwh) AS tot_gwh
                FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet')
                WHERE tipo_produzione = 'Netta'
                AND anno = (SELECT MAX(anno) FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet'))
                GROUP BY anno, regione
            )
            SELECT ROUND(MAX(rin_gwh/tot_gwh*100) - MIN(rin_gwh/tot_gwh*100), 1)
            FROM regioni
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Terna ultimo anno"}

    elif signal_id == "regioni_sotto_target_30pct":
        row = con.execute("""
            WITH regioni AS (
                SELECT regione,
                    SUM(CASE WHEN fonte IN ('Fotovoltaico','Eolico','Idrico','Geotermoelettrico','Bioenergie')
                          THEN produzione_gwh ELSE 0 END) / NULLIF(SUM(produzione_gwh), 0) * 100 AS quota_pct
                FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet')
                WHERE tipo_produzione = 'Netta'
                AND anno = (SELECT MAX(anno) FROM read_parquet('{}/terna_elettricita_per_fonte/*/*.parquet'))
                GROUP BY regione
            )
            SELECT COUNT(*) FROM regioni WHERE quota_pct < 30
        """.format(CLEAN_DIR, CLEAN_DIR)).fetchone()
        return {"value": row[0], "year": None, "note": "Terna ultimo anno"}

    return {"value": None, "year": None, "note": "not implemented"}


def _classify(signal_id: str, value: float | None) -> str:
    """Classifica il segnale: ok / warning / bad / unknown."""
    if value is None:
        return "unknown"
    for sid, dim, label, unit, thr_warn, thr_bad, direction in SIGNALS:
        if sid != signal_id:
            continue
        if thr_warn is None or thr_bad is None:
            return "ok"
        if direction == "lower_is_better":
            if value <= thr_warn:
                return "ok"
            elif value <= thr_bad:
                return "warning"
            else:
                return "bad"
        elif direction == "higher_is_better":
            if value >= thr_warn:
                return "ok"
            elif value >= thr_bad:
                return "warning"
            else:
                return "bad"
    return "ok"


def main() -> None:
    with safe_connect() as con:
        results = []

        print("  Calcolo segnali...")
        for signal_id, dimensione, label, unit, thr_warn, thr_bad, direction in SIGNALS:
            try:
                data = _get_signal(con, signal_id)
                status = _classify(signal_id, data["value"])
                results.append({
                    "id": signal_id,
                    "dimensione": dimensione,
                    "label": label,
                    "value": data["value"],
                    "unit": unit,
                    "status": status,
                    "threshold_warning": thr_warn,
                    "threshold_bad": thr_bad,
                    "note": data["note"],
                })
                icon = {"ok": "✓", "warning": "⚠", "bad": "✗", "unknown": "?"}[status]
                print(f"    {icon} {label}: {data['value']} {unit}")
            except Exception as e:
                results.append({
                    "id": signal_id, "dimensione": dimensione, "label": label,
                    "value": None, "unit": unit, "status": "error",
                    "threshold_warning": thr_warn, "threshold_bad": thr_bad,
                    "note": f"ERROR: {e}",
            })
            print(f"    ✗ {label}: ERROR {e}")

        # Scrivi CSV
        csv_path = SIGNALS_DIR / "signals.csv"
        with open(csv_path, "w") as f:
            f.write("id,dimensione,label,value,unit,status,threshold_warning,threshold_bad,note\n")
            for r in results:
                f.write(",".join(str(r[k]) for k in ["id", "dimensione", "label", "value", "unit",
                                                      "status", "threshold_warning", "threshold_bad", "note"]) + "\n")
        print(f"\n  Signals CSV: {csv_path}")

        # Scrivi panorama markdown
        ok_count = sum(1 for r in results if r["status"] == "ok")
        warn_count = sum(1 for r in results if r["status"] == "warning")
        bad_count = sum(1 for r in results if r["status"] == "bad")

        panorama = f"# Panorama Climatico Italia\n\n"
        panorama += f"**Segnali**: {ok_count} ok / {warn_count} warning / {bad_count} bad\n\n"
        for dim in ["emissioni", "rinnovabili", "mix", "finanza", "regionali"]:
            dim_signals = [r for r in results if r["dimensione"] == dim]
            if dim_signals:
                panorama += f"## {dim.title()}\n\n"
                for s in dim_signals:
                    icon = {"ok": "[OK]", "warning": "[WARN]", "bad": "[BAD]", "unknown": "[?]", "error": "[ERR]"}[s["status"]]
                    panorama += f"- {icon} **{s['label']}**: {s['value']} {s['unit']}\n"
                panorama += "\n"

        panorama_path = REPORTING_DIR / "panorama.md"
        with open(panorama_path, "w") as f:
            f.write(panorama)
        print(f"  Panorama MD:  {panorama_path}")

        # Scrivi JSON
        json_path = REPORTING_DIR / "panorama.json"
        with open(json_path, "w") as f:
            json.dump({"signals": results, "summary": {"ok": ok_count, "warning": warn_count, "bad": bad_count}}, f, indent=2)
        print(f"  Panorama JSON: {json_path}")


if __name__ == "__main__":
    main()
