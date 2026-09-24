"""Query SQL -- Interroga direttamente i dati."""

from pathlib import Path

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry

registry = load_registry(
    Path(__file__).parent.parent.parent / "registry" / "registry.json"
)

render_sql_query(
    registry=registry,
    prefix="energia_italia/",
    default_slug="terna_copertura_domanda",
    title="Query SQL",
    description="Interroga direttamente i dati. Scrivi SQL su ``clean_input``.",
)
