"""
test_smoke.py — Smoke test per energia-italia

Verifica:
- Esistenza e integrita' dei mart parquet
- Contratti colonne (required_columns)
- Min rows per mart
- Summary reconcile e signals
"""

import json
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
MART_DIR = ROOT / "out" / "data" / "mart"
CLEAN_DIR = ROOT / "out" / "data" / "clean"
RECONCILE_DIR = ROOT / "data" / "reconcile"
SIGNALS_DIR = ROOT / "data" / "signals"


# ── Contratti mart (per dataset) ────────────────────────────────────────────

MART_CONTRACTS = {
    "eurostat_emissioni_ghg": {
        "mart_emissioni_italia_gas": {
            "min_rows": 100,
            "required_columns": ["year", "gas", "emissioni_t"],
        },
        "mart_emissioni_italia_settori": {
            "min_rows": 1000,
            "required_columns": ["year", "settore", "gas", "emissioni_t"],
        },
        "mart_confronto_eu": {
            "min_rows": 15,
            "required_columns": ["year", "gas", "emissioni_it", "emissioni_eu27", "quota_it_pct"],
        },
    },
    "eurostat_rinnovabili": {
        "mart_rinnovabili_italia": {
            "min_rows": 15,
            "required_columns": ["year", "rinnovabili_pct", "target_2030", "gap_target_pct"],
        },
        "mart_ranking_eu": {
            "min_rows": 20,
            "required_columns": ["year", "geo", "rinnovabili_pct", "rank"],
        },
    },
    "ispra_emissioni_ghg": {
        "mart_settori_anno": {
            "min_rows": 100,
            "required_columns": ["anno", "settore", "emissioni_mt", "quota_pct"],
        },
        "mart_trend_settori": {
            "min_rows": 5,
            "required_columns": ["settore", "emissioni_1990", "emissioni_ultimo", "delta_pct", "cagr_annuale"],
        },
    },
    "istat_subsidi_ambientali": {
        "mart_sussidi_per_cea": {
            "min_rows": 100,
            "required_columns": ["year", "dominio", "sussidi_mln_eur"],
        },
        "mart_trend_sussidi": {
            "min_rows": 5,
            "required_columns": ["dominio", "sussidi_primo", "anno_primo", "sussidi_ultimo", "anno_ultimo", "delta_pct"],
        },
    },
    "istat_investimenti_mitigazione": {
        "mart_investimenti_per_cea": {
            "min_rows": 100,
            "required_columns": ["year", "cep_class", "investimenti_mln_eur"],
        },
        "mart_trend_investimenti": {
            "min_rows": 5,
            "required_columns": ["cep_class", "investimenti_primo", "anno_primo", "investimenti_ultimo", "anno_ultimo", "delta_pct"],
        },
    },
}


def _find_mart_files(dataset: str, mart_name: str) -> list[Path]:
    """Trova i parquet di un mart specifico."""
    pattern = MART_DIR / f"{dataset}*" / f"{mart_name}*"
    return list(pattern.parent.glob(f"{mart_name}*.parquet")) if pattern.parent.exists() else []


@pytest.mark.smoke
class TestMartContracts:
    """Verifica contratti dei mart per ogni dataset."""

    @pytest.mark.parametrize("dataset,mart_name,contract", [
        (ds, mart, contract)
        for ds, marts in MART_CONTRACTS.items()
        for mart, contract in marts.items()
    ], ids=[f"{ds}-{mart}" for ds, marts in MART_CONTRACTS.items() for mart in marts])
    def test_mart_exists_and_valid(self, dataset: str, mart_name: str, contract: dict):
        files = _find_mart_files(dataset, mart_name)
        if not files:
            pytest.skip(f"No mart files found for {dataset}/{mart_name}")

        con = duckdb.connect()
        all_rows = 0
        for f in files:
            df = con.execute(f"SELECT * FROM read_parquet('{f}')").fetchdf()
            all_rows += len(df)
            # Check required columns
            for col in contract["required_columns"]:
                assert col in df.columns, f"Missing column {col} in {f.name}"

        assert all_rows >= contract["min_rows"], \
            f"{dataset}/{mart_name}: {all_rows} rows < {contract['min_rows']}"


@pytest.mark.smoke
class TestReconcile:
    """Verifica output reconcile."""

    def test_summary_exists(self):
        summary_path = RECONCILE_DIR / "summary.json"
        if not summary_path.exists():
            pytest.skip("Reconcile not run yet")
        with open(summary_path) as f:
            data = json.load(f)
        assert data["total"] >= 3
        assert "ok" in data
        assert "anomalies" in data

    @pytest.mark.parametrize("case_file", [
        "c1_emissioni_ispra_eurostat.csv",
        "c2_settori_ispra_eurostat.csv",
        "c3_capacity_factor.csv",
        "c4_sussidi_investimenti.csv",
        "c5_coerenza_terna.csv",
    ])
    def test_case_csv_exists(self, case_file: str):
        path = RECONCILE_DIR / case_file
        if not path.exists():
            pytest.skip(f"Reconcile case {case_file} not run yet")
        assert path.stat().st_size > 0


@pytest.mark.smoke
class TestSignals:
    """Verifica output signals."""

    def test_signals_csv_exists(self):
        csv_path = SIGNALS_DIR / "signals.csv"
        if not csv_path.exists():
            pytest.skip("Signals not run yet")
        with open(csv_path) as f:
            lines = f.readlines()
        assert len(lines) >= 13  # header + 12 signals

    def test_panorama_exists(self):
        md_path = ROOT / "data" / "reporting" / "panorama.md"
        if not md_path.exists():
            pytest.skip("Panorama not generated yet")
        assert md_path.stat().st_size > 100
