#!/usr/bin/env python3
"""
reconcile.py — Cross-check tra fonti indipendenti (energia Italia)

Confonta fonti indipendenti sullo stesso fenomeno.
Ogni caso ha: query SQL, soglia anomalia, classificazione, deliverable CSV.

Uso:
    python reconcile.py                  # tutti i casi
    python reconcile.py --case capacity_factor  # solo caso specifico
"""

import json
import sys
from pathlib import Path
from typing import Any

import duckdb
from lab_connectors.duckdb.core import safe_connect

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "data"
MART_DIR = OUT_DIR / "mart"
CLEAN_DIR = OUT_DIR / "clean"
RECONCILE_DIR = Path(__file__).resolve().parent.parent / "data" / "reconcile"
RECONCILE_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD_PCT = 5.0


def _load_parquet(con: duckdb.DuckDBPyConnection, pattern: str, alias: str) -> None:
    con.execute(f"CREATE OR REPLACE VIEW {alias} AS SELECT * FROM read_parquet('{pattern}')")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    with open(path, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r[c]) for c in cols) + "\n")


# ── Caso 1: Capacity factor Terna ─────────────────────────────────────────

def case_capacity_factor(con: duckdb.DuckDBPyConnection) -> dict:
    """Verifica il capacity factor (produzione/capacity) per fonte.

    Valori attesi:
    - Solare: 10-18%
    - Eolico: 20-30%
    - Idrico: 30-50%
    - Geotermico: 80-95%
    - Bioenergie: 50-80%
    """
    _load_parquet(con, str(CLEAN_DIR / "terna_capacita_rinnovabile/*/*.parquet"), "capacity")
    _load_parquet(con, str(CLEAN_DIR / "terna_elettricita_per_fonte/*/*.parquet"), "produzione")

    CF_EXPECTED = {
        "Fotovoltaico": (10, 18), "Eolico": (20, 30), "Idrico": (30, 50),
        "Geotermoelettrico": (80, 95), "Bioenergie": (50, 80),
    }

    rows = con.execute("""
        WITH cap AS (
            SELECT anno, fonti, SUM(potenza_mw) AS capacity_mw
            FROM capacity WHERE tipo_capacita = 'Netta'
            GROUP BY anno, fonti
        ),
        prod AS (
            SELECT anno, fonte, SUM(produzione_gwh) AS produzione_gwh
            FROM produzione WHERE tipo_produzione = 'Netta'
            GROUP BY anno, fonte
        )
        SELECT
            COALESCE(c.anno, p.anno) AS anno,
            COALESCE(c.fonti, p.fonte) AS fonte,
            c.capacity_mw,
            p.produzione_gwh,
            ROUND(p.produzione_gwh * 1000 / NULLIF(c.capacity_mw * 8760, 0) * 100, 2) AS capacity_factor_pct
        FROM cap c
        FULL OUTER JOIN prod p ON c.anno = p.anno AND c.fonti = p.fonte
        WHERE c.capacity_mw > 0 AND p.produzione_gwh > 0
        ORDER BY anno, fonte
    """).fetchall()

    results = []
    anomalies = []
    for anno, fonte, cap_mw, prod_gwh, cf in rows:
        expected = CF_EXPECTED.get(fonte)
        status = "ok"
        if expected and cf:
            if cf < expected[0] * 0.5 or cf > expected[1] * 1.3:
                status = "anomaly"
                anomalies.append(f"{anno}-{fonte}")
        results.append({"anno": anno, "fonte": fonte, "capacity_mw": round(cap_mw, 1),
                        "produzione_gwh": round(prod_gwh, 1), "capacity_factor_pct": cf, "status": status})

    _write_csv(results, RECONCILE_DIR / "c1_capacity_factor.csv")
    return {
        "case": "c1_capacity_factor",
        "description": "Capacity factor per fonte rinnovabile (Terna capacity vs produzione)",
        "fonti": ["Terna (CapacityRenewableSources)", "Terna (ElectricityBySource)"],
        "threshold_pct": 50,
        "anomalies": anomalies,
        "status": "ok" if not anomalies else "anomaly",
    }


# ── Caso 2: PUN GME profilo annuale ─────────────────────────────────────

def case_pun_gme(con: duckdb.DuckDBPyConnection) -> dict:
    """Profilo annuale PUN (GME Portale Offerte)."""
    _load_parquet(con, str(CLEAN_DIR / "gme_pun_storico/*/*.parquet"), "gme")

    rows = con.execute("""
        SELECT
            anno,
            ROUND(AVG(pun_eur_kwh), 6) AS pun_medio,
            ROUND(MIN(pun_eur_kwh), 6) AS pun_min,
            ROUND(MAX(pun_eur_kwh), 6) AS pun_max,
            COUNT(*) AS mesi
        FROM gme
        GROUP BY anno
        ORDER BY anno
    """).fetchall()

    results = []
    for anno, pun_medio, pun_min, pun_max, mesi in rows:
        results.append({
            "anno": anno, "pun_medio": pun_medio,
            "pun_min": pun_min, "pun_max": pun_max,
            "mesi": mesi, "status": "ok" if mesi >= 12 else "partial"
        })

    _write_csv(results, RECONCILE_DIR / "c2_pun_gme_annuale.csv")
    return {
        "case": "c2_pun_gme_annuale",
        "description": "Profilo annuale PUN (GME Portale Offerte)",
        "fonti": ["GME (Portale Offerte)"],
        "years_compared": len(results),
        "status": "ok",
    }


# ── Main ────────────────────────────────────────────────────────────────────

CASES = {
    "capacity_factor": case_capacity_factor,
    "pun_gme": case_pun_gme,
}


def main() -> None:
    filter_case = sys.argv[1] if len(sys.argv) > 1 else None
    cases_to_run = {filter_case: CASES[filter_case]} if filter_case else CASES

    with safe_connect() as con:
        summary = []

        for name, fn in cases_to_run.items():
            print(f"  Running {name}...")
            result = fn(con)
            summary.append(result)
            status_icon = "✓" if result["status"] == "ok" else "⚠" if result["status"] == "warning" else "✗"
            print(f"    {status_icon} {result['description']}")

    summary_path = RECONCILE_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump({"cases": summary, "total": len(summary),
                    "ok": sum(1 for s in summary if s["status"] == "ok"),
                    "warnings": sum(1 for s in summary if s["status"] == "warning"),
                    "anomalies": sum(1 for s in summary if s["status"] == "anomaly")}, f, indent=2)

    print(f"\n  Summary: {summary_path}")
    print(f"  Total: {len(summary)} | OK: {sum(1 for s in summary if s['status'] == 'ok')} | "
          f"Warnings: {sum(1 for s in summary if s['status'] == 'warning')} | "
          f"Anomalies: {sum(1 for s in summary if s['status'] == 'anomaly')}")


if __name__ == "__main__":
    main()
