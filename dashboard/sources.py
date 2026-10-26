"""Fonti dati per la dashboard Energia Italia.

Multi-dataset: Terna, GME, Eurostat, ISPRA.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from lab_connectors.duckdb.queries import (
    load_mart_table as _load_mart_table,
)
from lab_connectors.duckdb.queries import (
    query_clean as _query_clean,
)

PREFIX = "energia_italia/"
YEARS = list(range(2000, 2027))
# Copertura domanda pubblicata dalla fonte dal 2005
COPERTURA_YEARS = list(range(2005, 2025))
# Fonte/settore/emissioni/capacita: serie storica dal 2000
ENERGIA_YEARS = list(range(2000, 2025))
# Bilancio internazionale: solo 2022-2023 (consolidamento annuale Terna)
CONFRONTO_YEARS = [2022, 2023]


def _q(slug: str, sql: str, year: int = 2026):
    """Query su clean layer per un dataset specifico."""
    return _query_clean(slug, sql, [year], prefix=PREFIX)


def _concat_years_mart(slug: str, table: str, years: list[int]) -> pd.DataFrame:
    """Concatena un mart table su piu' anni, saltando gli anni non ancora pubblicati.

    Su Streamlit Cloud i layer mart/clean possono non coprire ancora tutti gli
anni configurati (i nuovi anni vengono pubblicati dalla pipeline post-merge).
Senza questo filtro un singolo anno mancante farebbe fallire tutto il grafico.
    """
    frames: list[pd.DataFrame] = []
    for y in years:
        try:
            df = _load_mart_table(slug, table, y, prefix=PREFIX)
            if not df.empty:
                frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data(ttl=3600, show_spinner=False)
def load_copertura(year: int = 2024):
    """Copertura domanda per fonte (nazionale)."""
    return _load_mart_table(
        "terna_copertura_domanda", "mart_copertura_fonte_nazionale", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_copertura_storico():
    """Serie nazionale completa per anno, saltando gli anni non pubblicati."""
    return _concat_years_mart(
        "terna_copertura_domanda", "mart_copertura_fonte_nazionale", COPERTURA_YEARS
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
def load_settore(year: int = 2024):
    """Consumi elettrici per settore e provincia."""
    return _load_mart_table(
        "terna_elettricita_per_settore", "mart_consumi_settore_provincia", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_settore_storico():
    """Serie consumi per settore (nazionale), saltando gli anni non pubblicati."""
    return _concat_years_mart(
        "terna_elettricita_per_settore", "mart_consumi_settore_provincia", ENERGIA_YEARS
    )


# Anno sintetico del compose energia-incroci (output a livello dataset)
INCI_YEAR = 2026


@st.cache_data(ttl=3600, show_spinner=False)
def load_capacity_factor():
    """Capacity factor delle FER per regione x fonte x anno (compose)."""
    return _load_mart_table(
        "energia_incroci", "mart_capacity_factor", INCI_YEAR, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def load_intensita_regionale():
    """Intensita di carbonio della copertura regionale + quota rinnovabile (compose)."""
    return _load_mart_table(
        "energia_incroci", "mart_intensita_regionale", INCI_YEAR, prefix=PREFIX
    )


# ── Domanda e generazione oraria (2019-2025) ──────────────────────────
# Due dataset con granularita' oraria: la dimensione che le altre pagine
# (annuale/mensile/regionale) non coprono.
ORA_YEARS = list(range(2019, 2026))


@st.cache_data(ttl=3600, show_spinner=False)
def load_carico_annuale():
    """Domanda annua nazionale: total (2019-2025) e market (dal 2021)."""
    return _concat_years_mart("terna_load_oraria", "mart_carico_annuale", ORA_YEARS)


@st.cache_data(ttl=3600, show_spinner=False)
def load_carico_profilo(year: int = 2025):
    """Profilo medio della domanda per ora del giorno (un anno)."""
    return _load_mart_table("terna_load_oraria", "mart_profilo_carico", year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_ore_alta_domanda():
    """Ore equivalenti sopra soglia di domanda, per anno (2019-2025)."""
    return _concat_years_mart("terna_load_oraria", "mart_ore_alta_domanda", ORA_YEARS)


@st.cache_data(ttl=3600, show_spinner=False)
def load_generazione_profilo(year: int = 2025):
    """Profilo medio della generazione per fonte e ora del giorno (un anno)."""
    return _load_mart_table(
        "terna_generation_oraria", "mart_profilo_orario", year, prefix=PREFIX
    )


@st.cache_data(ttl=3600, show_spinner=False)
def query(sql: str, years: tuple[int, ...] = tuple(YEARS)):
    """Query SQL generica sul clean layer."""
    return _query_clean("terna_copertura_domanda", sql, list(years), prefix=PREFIX)
