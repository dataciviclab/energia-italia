"""
test_dashboard.py — Syntax check per pagine Streamlit

Verifica che ogni pagina sia Python valido via ast.parse().
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "dashboard"
PAGES_DIR = DASHBOARD_DIR / "pages"


@pytest.mark.dashboard
class TestDashboardSyntax:
    """Verifica sintassi di ogni pagina dashboard."""

    @pytest.mark.parametrize("page", sorted(PAGES_DIR.glob("*.py")))
    def test_page_valid_python(self, page: Path):
        source = page.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {page.name}: {e}")

    def test_app_valid_python(self):
        app = DASHBOARD_DIR / "app.py"
        if not app.exists():
            pytest.skip("app.py not found")
        source = app.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in app.py: {e}")

    def test_sources_valid_python(self):
        sources = DASHBOARD_DIR / "sources.py"
        if not sources.exists():
            pytest.skip("sources.py not found")
        source = sources.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in sources.py: {e}")
