"""
test_smoke.py — Smoke test per energia-italia

Verifica:
- Esistenza e integrita' dei mart parquet
- Contratti colonne (required_columns)
- Min rows per mart
"""

from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parent.parent
MART_DIR = ROOT / "out" / "data" / "mart"


# ── Contratti mart (per dataset) ────────────────────────────────────────────

MART_CONTRACTS = {
    "terna_copertura_domanda": {
        "mart_copertura_fonte_nazionale": {
            "min_rows": 5,
            "required_columns": ["anno", "fonte", "copertura_gwh", "quota_pct"],
        },
        "mart_copertura_fonte_regione": {
            "min_rows": 50,
            "required_columns": ["anno", "regione", "fonte", "copertura_gwh"],
        },
    },
    "terna_elettricita_per_fonte": {
        "mart_mix_regioni": {
            "min_rows": 10,
            "required_columns": ["anno", "regione", "quota_rinnovabili_pct"],
        },
    },
    "terna_emissioni_co2": {
        "mart_emissioni_combustibile": {
            "min_rows": 3,
            "required_columns": ["anno", "combustibile", "emissioni_mt"],
        },
        "mart_emissioni_regione": {
            "min_rows": 10,
            "required_columns": ["anno", "regione", "emissioni_mt"],
        },
    },
    "terna_bilancio_elettrico": {
        "mart_bilancio_italia": {
            "min_rows": 1,
            "required_columns": ["anno", "produzione_neta_twh", "richiesta_twh"],
        },
        "mart_confronto_ue": {
            "min_rows": 5,
            "required_columns": ["anno", "nazione", "produzione_neta_twh"],
        },
    },
    "gme_pun_storico": {
        "mart_pun_mensile": {
            "min_rows": 50,
            "required_columns": ["anno", "mese", "pun_eur_kwh"],
        },
        "mart_pun_annuale": {
            "min_rows": 5,
            "required_columns": ["anno", "pun_medio_kwh"],
        },
    },
    "terna_capacita_rinnovabile": {
        "mart_regioni_fonti_nette": {
            "min_rows": 100,
            "required_columns": ["anno", "regione", "fonti", "potenza_totale_mw"],
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
            for col in contract["required_columns"]:
                assert col in df.columns, f"Missing column {col} in {f.name}"

        assert all_rows >= contract["min_rows"], \
            f"{dataset}/{mart_name}: {all_rows} rows < {contract['min_rows']}"
