#!/usr/bin/env python3
"""
Energia Italia · Dashboard Streamlit
Intelligence sul sistema elettrico italiano
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Energia Italia · Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding()

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Mix_Energetico.py", title="Mix Energetico", icon="⚡"),
        st.Page("pages/03_Prezzi.py", title="Prezzi", icon="💰"),
        st.Page("pages/04_Emissioni.py", title="Emissioni", icon="🏭"),
        st.Page("pages/05_Confronti_EU.py", title="Confronti EU", icon="🇪🇺"),
    ],
    "Strumenti": [
        st.Page("pages/06_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.markdown("---")
st.sidebar.caption("Dati: Terna, GME, Eurostat, ISPRA, ISTAT")
st.sidebar.caption(
    "Codice: [dataciviclab/energia-italia](https://github.com/dataciviclab/energia-italia)"
)
st.sidebar.caption("[DataCivicLab](https://dataciviclab.org/) · CC BY 4.0")

pg.run()
