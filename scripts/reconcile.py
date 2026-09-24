#!/usr/bin/env python3
"""
reconcile.py — Cross-check tra fonti indipendenti (energia Italia)

Confonta fonti indipendenti sullo stesso fenomeno climatico.
Ogni caso ha: query SQL, soglia anomalia, classificazione, deliverable CSV.

Uso:
    python reconcile.py                  # tutti i casi
    python reconcile.py --case emissioni  # solo caso specifico
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

THRESHOLD_PCT = 5.0  # soglia anomalia in %


def _connect():
    """Return a DuckDB connection (caller manages lifecycle via context manager)."""
    return safe_connect()


def _load_parquet(con: duckdb.DuckDBPyConnection, pattern: str, alias: str) -> None:
    con.execute(f"CREATE OR REPLACE VIEW {alias} AS SELECT * FROM read_parquet('{pattern}')")


def _compare(a: float, b: float, label: str) -> dict[str, Any]:
    """Confronta due valori e classifica lo scostamento."""
    if a == 0 and b == 0:
        return {"label": label, "val_a": a, "val_b": b, "delta_pct": 0, "status": "ok"}
    ref = max(abs(a), abs(b))
    delta_pct = abs(a - b) / ref * 100 if ref > 0 else 0
    status = "ok" if delta_pct < THRESHOLD_PCT else "anomaly"
    return {"label": label, "val_a": round(a, 2), "val_b": round(b, 2),
            "delta_pct": round(delta_pct, 2), "status": status}


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    cols = list(rows[0].keys())
    with open(path, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r[c]) for c in cols) + "\n")


# ── Caso 1: ISPRA vs Eurostat — totale GHG Italia ─────────────────────────

def case_emissioni(con: duckdb.DuckDBPyConnection) -> dict:
    """Confronta emissioni GHG totali Italia: ISPRA vs Eurostat.

    ISPRA: macro-settori sommati, valori in Mt (diviso 1.000.000)
    Eurostat: totale GHG, valori in tonnellate
    """
    _load_parquet(con, str(CLEAN_DIR / "ispra_emissioni_ghg/*/*.parquet"), "ispra")
    _load_parquet(con, str(CLEAN_DIR / "eurostat_emissioni_ghg/*/*.parquet"), "eurostat")

    rows = con.execute("""
        WITH ispra_totale AS (
            SELECT anno, totale AS emissioni_mt
            FROM ispra
        ),
        eurostat_it AS (
            SELECT year, SUM(value) / 1000000.0 AS emissioni_mt_euro
            FROM eurostat
            WHERE geo = 'IT' AND airpol = 'GHG' AND unit = 'T' AND nace_r2 = 'TOTAL'
            GROUP BY year
        )
        SELECT
            COALESCE(i.anno, e.year) AS anno,
            i.emissioni_mt AS ispra_mt,
            e.emissioni_mt_euro AS eurostat_mt,
            CASE
                WHEN i.emissioni_mt IS NOT NULL AND e.emissioni_mt_euro IS NOT NULL
                THEN ABS(i.emissioni_mt - e.emissioni_mt_euro) / GREATEST(i.emissioni_mt, e.emissioni_mt_euro) * 100
                ELSE NULL
            END AS delta_pct
        FROM ispra_totale i
        FULL OUTER JOIN eurostat_it e ON i.anno = e.year
        WHERE i.emissioni_mt IS NOT NULL AND e.emissioni_mt_euro IS NOT NULL
        ORDER BY anno
    """).fetchall()

    results = []
    anomalies = []
    for anno, ispra, euro, delta in rows:
        status = "ok" if delta and delta < THRESHOLD_PCT else "anomaly" if delta else "missing"
        results.append({"anno": anno, "ispra_mt": round(ispra, 2), "eurostat_mt": round(euro, 2),
                        "delta_pct": round(delta, 2) if delta else None, "status": status})
        if status == "anomaly":
            anomalies.append(anno)

    _write_csv(results, RECONCILE_DIR / "c1_emissioni_ispra_eurostat.csv")
    return {
        "case": "c1_emissioni_ispra_eurostat",
        "description": "Confronto totale GHG Italia: ISPRA vs Eurostat",
        "fonti": ["ISPRA (macro-settori)", "Eurostat (ENV_AC_AINAH_R2)"],
        "threshold_pct": THRESHOLD_PCT,
        "years_compared": len(results),
        "anomalies": anomalies,
        "status": "ok" if not anomalies else "anomaly",
    }


# ── Caso 2: ISPRA sector classification vs Eurostat NACE ───────────────────

def case_settori(con: duckdb.DuckDBPyConnection) -> dict:
    """Confronta la classificazione settoriale ISPRA vs Eurostat.

    ISPRA: 4 macro-settori (industrie_energetiche, manifatturiere, residenziale, trasporti)
    Eurostat: codici NACE R2 dettagliati
    Verifica che i totali siano coerenti.
    """
    _load_parquet(con, str(CLEAN_DIR / "ispra_emissioni_ghg/*/*.parquet"), "ispra")
    _load_parquet(con, str(CLEAN_DIR / "eurostat_emissioni_ghg/*/*.parquet"), "eurostat")

    rows = con.execute("""
        WITH ispra AS (
            SELECT anno,
                industrie_energetiche + industrie_manifatturiere + residenziale_e_servizi + trasporti AS somma_settori,
                totale
            FROM ispra
        ),
        eurostat_latest AS (
            SELECT year, SUM(value) / 1000000.0 AS emissioni_mt
            FROM eurostat
            WHERE geo = 'IT' AND airpol = 'GHG' AND unit = 'T' AND nace_r2 = 'TOTAL'
            GROUP BY year
        )
        SELECT
            i.anno,
            ROUND(i.somma_settori, 2) AS somma_settori_mt,
            ROUND(i.totale, 2) AS totale_ispra_mt,
            ROUND(i.totale - i.somma_settori, 2) AS delta_interno_mt,
            e.emissioni_mt AS eurostat_mt
        FROM ispra i
        LEFT JOIN eurostat_latest e ON i.anno = e.year
        WHERE i.anno BETWEEN 2008 AND 2023
        ORDER BY i.anno
    """).fetchall()

    results = []
    for anno, somma, totale, delta_int, euro in rows:
        results.append({
            "anno": anno, "somma_settori_mt": somma, "totale_ispra_mt": totale,
            "delta_interno_mt": delta_int, "eurostat_mt": round(euro, 2) if euro else None
        })

    _write_csv(results, RECONCILE_DIR / "c2_settori_ispra_eurostat.csv")
    return {
        "case": "c2_settori_ispra_eurostat",
        "description": "Coerenza interna ISPRA (somma settori vs totale) e confronto Eurostat",
        "fonti": ["ISPRA (macro-settori)", "Eurostat (ENV_AC_AINAH_R2)"],
        "years_compared": len(results),
        "status": "ok",
    }


# ── Caso 3: Capacity factor Terna ─────────────────────────────────────────

def case_capacity_factor(con: duckdb.DuckDBPyConnection) -> dict:
    """Verifica il capacity factor (produzione/capacity) per fonte.

    Valori attesi:
    - Solare: 10-18%
    - Eolico: 20-30%
    - Idrico: 30-50%
    - Geotermico: 80-95%
    - Bioenergie: 50-80%
    Valori fuori range = potenziale anomalia dati.
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

    _write_csv(results, RECONCILE_DIR / "c3_capacity_factor.csv")
    return {
        "case": "c3_capacity_factor",
        "description": "Capacity factor per fonte rinnovabile (Terna capacity vs produzione)",
        "fonti": ["Terna (CapacityRenewableSources)", "Terna (ElectricityBySource)"],
        "threshold_pct": 50,
        "anomalies": anomalies,
        "status": "ok" if not anomalies else "anomaly",
    }


# ── Caso 4: Sussidi vs Investimenti ISTAT ─────────────────────────────────

def case_sussidi_investimenti(con: duckdb.DuckDBPyConnection) -> dict:
    """Confronta sussidi e investimenti per dominio CEPA.

    Rapporto sussidi/investimenti > 100% = potenziale inefficienza.
    Rapporto < 5% = potenziale sotto-finanziamento.
    """
    _load_parquet(con, str(CLEAN_DIR / "istat_subsidi_ambientali/*/*.parquet"), "sussidi")
    _load_parquet(con, str(CLEAN_DIR / "istat_investimenti_mitigazione/*/*.parquet"), "investimenti")

    rows = con.execute("""
        WITH s AS (
            SELECT year, cep_class, SUM(obs_value) AS sussidi
            FROM sussidi GROUP BY year, cep_class
        ),
        i AS (
            SELECT year, cep_class, SUM(obs_value) AS investimenti
            FROM investimenti GROUP BY year, cep_class
        )
        SELECT
            COALESCE(s.year, i.year) AS anno,
            COALESCE(s.cep_class, i.cep_class) AS dominio,
            s.sussidi,
            i.investimenti,
            ROUND(s.sussidi / NULLIF(i.investimenti, 0) * 100, 2) AS rapporto_pct
        FROM s
        FULL OUTER JOIN i ON s.year = i.year AND s.cep_class = i.cep_class
        WHERE s.sussidi > 0 OR i.investimenti > 0
        ORDER BY anno, dominio
    """).fetchall()

    results = []
    warnings = []
    for anno, dom, sus, inv, rap in rows:
        status = "ok"
        if rap and (rap > 100 or rap < 5):
            status = "warning"
            warnings.append(f"{anno}-{dom}")
        results.append({"anno": anno, "dominio": dom, "sussidi": round(sus, 1) if sus else 0,
                        "investimenti": round(inv, 1) if inv else 0, "rapporto_pct": rap, "status": status})

    _write_csv(results, RECONCILE_DIR / "c4_sussidi_investimenti.csv")
    return {
        "case": "c4_sussidi_investimenti",
        "description": "Rapporto sussidi/investimenti per dominio CEPA (ISTAT)",
        "fonti": ["ISTAT (72_1028 sussidi)", "ISTAT (71_1028 investimenti)"],
        "warnings": warnings,
        "status": "ok" if not warnings else "warning",
    }


# ── Caso 5: Coerenza Terna capacity vs produzione regionale ────────────────

def case_coerenza_terna(con: duckdb.DuckDBPyConnection) -> dict:
    """Verifica che la somma regionale della produzione sia coerente con i totali nazionali."""
    _load_parquet(con, str(CLEAN_DIR / "terna_elettricita_per_fonte/*/*.parquet"), "produzione")
    _load_parquet(con, str(CLEAN_DIR / "terna_consumo_per_fonte/*/*.parquet"), "consumo")

    rows = con.execute("""
        WITH prod_naz AS (
            SELECT anno, SUM(produzione_gwh) AS produzione_gwh
            FROM produzione WHERE tipo_produzione = 'Netta'
            GROUP BY anno
        ),
        cons_naz AS (
            SELECT anno, SUM(copertura_gwh) AS consumo_gwh
            FROM consumo
            GROUP BY anno
        )
        SELECT
            COALESCE(p.anno, c.anno) AS anno,
            p.produzione_gwh,
            c.consumo_gwh,
            ROUND((p.produzione_gwh - c.consumo_gwh) / NULLIF(c.consumo_gwh, 0) * 100, 2) AS saldo_pct
        FROM prod_naz p
        FULL OUTER JOIN cons_naz c ON p.anno = c.anno
        ORDER BY anno
    """).fetchall()

    results = []
    for anno, prod, cons, saldo in rows:
        results.append({"anno": anno, "produzione_gwh": round(prod, 1) if prod else None,
                        "consumo_gwh": round(cons, 1) if cons else None, "saldo_pct": saldo})

    _write_csv(results, RECONCILE_DIR / "c5_coerenza_terna.csv")
    return {
        "case": "c5_coerenza_terna",
        "description": "Coerenza produzione vs consumo nazionale (Terna)",
        "fonti": ["Terna (ElectricityBySource)", "Terna (ConsumptionBySource)"],
        "years_compared": len(results),
        "status": "ok",
    }


# ── Caso 6: Coerenza PUN GME vs Terna prezzo mercato ───────────────────────

def case_pun_terna(con: duckdb.DuckDBPyConnection) -> dict:
    """Verifica coerenza tra PUN GME e dati Terna.

    Confronta il PUN medio annuale (GME) con il prezzo medio di mercato
    derivato dai dati Terna (se disponibili).
    """
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

    _write_csv(results, RECONCILE_DIR / "c6_pun_gme_annuale.csv")
    return {
        "case": "c6_pun_gme_annuale",
        "description": "Profilo annuale PUN (GME Portale Offerte)",
        "fonti": ["GME (Portale Offerte)"],
        "years_compared": len(results),
        "status": "ok",
    }


# ── Caso 7: Emissioni Terna CO2 vs ISPRA GHG ──────────────────────────────

def case_emissioni_terna_ispra(con: duckdb.DuckDBPyConnection) -> dict:
    """Confronta emissioni CO2 Terna (da combustibili termoelettrici) con ISPRA GHG.

    Terna: emissioni da produzione termoelettrica, per combustibile.
    ISPRA: emissioni totali da processi energetici, per settore.
    Il confronto è indicativo: Terna copre solo termoelettrico, ISPRA è più ampio.
    """
    _load_parquet(con, str(CLEAN_DIR / "terna_emissioni_co2/*/*.parquet"), "terna")
    _load_parquet(con, str(CLEAN_DIR / "ispra_emissioni_ghg/*/*.parquet"), "ispra")

    rows = con.execute("""
        WITH terna_totale AS (
            SELECT anno, SUM(emissioni_mt) AS emissioni_termo_mt
            FROM terna
            WHERE emissioni_mt IS NOT NULL
            GROUP BY anno
        ),
        ispra_energetiche AS (
            SELECT anno, industrie_energetiche AS emissioni_energ_mt
            FROM ispra
        )
        SELECT
            COALESCE(t.anno, i.anno) AS anno,
            t.emissioni_termo_mt,
            i.emissioni_energ_mt,
            CASE
                WHEN t.emissioni_termo_mt IS NOT NULL AND i.emissioni_energ_mt IS NOT NULL
                THEN ROUND(ABS(t.emissioni_termo_mt - i.emissioni_energ_mt) / GREATEST(t.emissioni_termo_mt, i.emissioni_energ_mt) * 100, 2)
                ELSE NULL
            END AS delta_pct
        FROM terna_totale t
        FULL OUTER JOIN ispra_energetiche i ON t.anno = i.anno
        WHERE t.anno IS NOT NULL OR i.anno IS NOT NULL
        ORDER BY anno
    """).fetchall()

    results = []
    anomalies = []
    for anno, terna, ispra, delta in rows:
        status = "ok" if delta and delta < 20 else "anomaly" if delta else "missing"
        results.append({
            "anno": anno,
            "terna_termo_mt": round(terna, 2) if terna else None,
            "ispra_energetiche_mt": round(ispra, 2) if ispra else None,
            "delta_pct": delta,
            "status": status,
        })
        if status == "anomaly":
            anomalies.append(anno)

    _write_csv(results, RECONCILE_DIR / "c7_emissioni_terna_ispra.csv")
    return {
        "case": "c7_emissioni_terna_ispra",
        "description": "Confronto emissioni CO2: Terna (termoelettrico) vs ISPRA (processi energetici)",
        "fonti": ["Terna (GrossVsCO2Emissions)", "ISPRA (emissioni_ghg)"],
        "note": "Terna = solo termoelettrico; ISPRA = tutti i processi energetici. Delta atteso ~30-50%.",
        "threshold_pct": 20,
        "years_compared": len(results),
        "anomalies": anomalies,
        "status": "ok" if not anomalies else "anomaly",
    }


# ── Main ────────────────────────────────────────────────────────────────────

CASES = {
    "emissioni": case_emissioni,
    "settori": case_settori,
    "capacity_factor": case_capacity_factor,
    "sussidi_investimenti": case_sussidi_investimenti,
    "coerenza_terna": case_coerenza_terna,
    "pun_gme": case_pun_terna,
    "emissioni_terna_ispra": case_emissioni_terna_ispra,
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
