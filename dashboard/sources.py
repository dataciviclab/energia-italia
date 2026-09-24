"""Fonti dati per la dashboard Energia Italia.

Multi-dataset: Terna, GME, Eurostat, ISPRA.
"""

from __future__ import annotations

import streamlit as st

from lab_connectors.duckdb.queries import (
    load_mart_table as _load_mart_table,
    query_clean as _query_clean,
)
from lab_connectors.formatters import fmt_num, fmt_pct, fmt_eur

PREFIX = "energia_italia/"
YEARS = list(range(2015, 2027))


def _q(slug: str, sql: str, year: int = 2026):
    """Query su clean layer per un dataset specifico."""
    return _query_clean(slug, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_copertura(year: int = 2024):
    """Copertura domanda per fonte (nazionale)."""
    return _load_mart_table(
        "terna_copertura_domanda", "mart_copertura_fonte_nazionale", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_copertura_regione(year: int = 2024):
    """Copertura domanda per fonte e regione."""
    return _load_mart_table(
        "terna_copertura_domanda", "mart_copertura_fonte_regione", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_mix_regioni(year: int = 2024):
    """Mix rinnovabili per regione."""
    return _load_mart_table(
        "terna_elettricita_per_fonte", "mart_mix_regioni", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_pun_mensile():
    """PUN/PSV mensili (tutti gli anni)."""
    return _load_mart_table(
        "gme_pun_storico", "mart_pun_mensile", 2026, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_pun_annuale():
    """PUN/PSV annuali."""
    return _load_mart_table(
        "gme_pun_storico", "mart_pun_annuale", 2026, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_emissioni_combustibile(year: int = 2024):
    """Emissioni CO2 per combustibile."""
    return _load_mart_table(
        "terna_emissioni_co2", "mart_emissioni_combustibile", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_emissioni_regione(year: int = 2024):
    """Emissioni CO2 per regione."""
    return _load_mart_table(
        "terna_emissioni_co2", "mart_emissioni_regione", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_confronto_ue(year: int = 2023):
    """Confronto Italia vs paesi EU."""
    return _load_mart_table(
        "terna_bilancio_elettrico", "mart_confronto_ue", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_capacita(year: int = 2024):
    """Capacita rinnovabile per regione/fonte."""
    return _load_mart_table(
        "terna_capacita_rinnovabile", "mart_regioni_fonti_nette", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def query(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    """Query SQL generica sul clean layer."""
    return _query_clean("terna_copertura_domanda", sql, list(years), prefix=PREFIX)
