"""Verifica che tutte le pagine della dashboard si compilino senza errori.

Il nome file e' distinto da ``tests/test_smoke.py``: due moduli con lo stesso
basename in directory diverse fanno fallire la collection quando si lanciano
insieme (``pytest tests/ dashboard/tests``).
"""

from __future__ import annotations

import py_compile
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

PAGES_DIR = Path(__file__).resolve().parent.parent / "pages"


@pytest.mark.parametrize(
    "page",
    sorted(PAGES_DIR.glob("*.py")),
    ids=lambda p: p.stem,
)
def test_page_compiles(page: Path) -> None:
    """Ogni pagina deve compilarsi senza errori di sintassi."""
    py_compile.compile(str(page), doraise=True)
