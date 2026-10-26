"""Ora per ora — domanda elettrica e generazione nella giornata tipo.

Sfrutta la granularita' oraria (2019-2025): profilo medio della domanda,
profilo medio della generazione per fonte e crescita delle punte.
"""

import plotly.graph_objects as go
import streamlit as st
from sources import (
    ORA_YEARS,
    load_carico_annuale,
    load_carico_profilo,
    load_generazione_profilo,
    load_ore_alta_domanda,
)

st.title("Ora per ora")

st.caption(
    "Domanda elettrica e generazione nella giornata tipo, 2019-2025. "
    "Le altre pagine guardano l'anno; qui si guarda l'ora."
)

anno = st.selectbox("Anno", ORA_YEARS, index=len(ORA_YEARS) - 1, key="ora_anno")

# ── Dati annuali ──────────────────────────────────────────────────────
try:
    df_ann = load_carico_annuale()
except Exception as e:
    st.error(f"Errore caricamento domanda annua: {e}")
    st.stop()

if df_ann.empty:
    st.warning("Nessun dato di domanda disponibile.")
    st.stop()

ann = df_ann[df_ann["anno"] == anno]
tot = ann[ann["tipo_carico"] == "total"]
mkt = ann[ann["tipo_carico"] == "market"]

# ── KPI (anno selezionato) ────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Picco domanda", f"{tot['max_gw'].iloc[0]:.1f} GW" if not tot.empty else "—")
with k2:
    st.metric("Domanda media", f"{tot['media_gw'].iloc[0]:.1f} GW" if not tot.empty else "—")
with k3:
    st.metric("Energia", f"{tot['energia_twh'].iloc[0]:.1f} TWh" if not tot.empty else "—")
with k4:
    if not tot.empty and not mkt.empty:
        fuori = tot["energia_twh"].iloc[0] - mkt["energia_twh"].iloc[0]
        st.metric(
            "Fuori mercato",
            f"{fuori:.1f} TWh",
            help="Domanda totale meno domanda servita dal mercato (autoconsumo/auto-produzione).",
        )
    else:
        st.metric("Fuori mercato", "—", help="Serie market disponibile solo dal 2021.")

# ── Profilo orario della domanda ──────────────────────────────────────
st.subheader(f"Domanda media per ora — {anno}")

try:
    df_prof = load_carico_profilo(anno)
except Exception as e:
    df_prof = None
    st.warning(f"Errore caricamento profilo domanda: {e}")

if df_prof is not None and not df_prof.empty:
    fig = go.Figure()
    for tipo, label, color in (
        ("total", "Totale", "#2563eb"),
        ("market", "Mercato", "#f59e0b"),
    ):
        d = df_prof[df_prof["tipo_carico"] == tipo].sort_values("ora")
        if not d.empty:
            fig.add_trace(
                go.Scatter(
                    x=d["ora"],
                    y=d["media_gw"],
                    mode="lines",
                    name=label,
                    line={"color": color, "width": 3},
                )
            )
    fig.update_layout(
        height=320,
        margin={"t": 20, "b": 40},
        xaxis_title="Ora del giorno",
        yaxis_title="GW",
        xaxis={"dtick": 2},
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Profilo medio su tutti i giorni dell'anno. La domanda ha due punte "
        "(mattina e sera): la sera il fotovoltaico e' gia' calato."
    )

# ── Profilo orario della generazione per fonte ────────────────────────
st.subheader(f"Generazione media per ora e fonte — {anno}")

FONTI_RETE = [
    "Thermal",
    "Hydro",
    "Geothermal",
    "Wind",
    "Photovoltaic",
]
FONTI_COLORS = {
    "Thermal": "#6b7280",
    "Hydro": "#3b82f6",
    "Geothermal": "#ef4444",
    "Wind": "#059669",
    "Photovoltaic": "#f59e0b",
    "Self-consumption": "#8b5cf6",
}

try:
    df_gen = load_generazione_profilo(anno)
except Exception as e:
    df_gen = None
    st.warning(f"Errore caricamento profilo generazione: {e}")

if df_gen is not None and not df_gen.empty:
    fig2 = go.Figure()
    # Solo le fonti immesse in rete: lo stack e' confrontabile con la domanda
    # del grafico sopra.
    for fonte in FONTI_RETE:
        d = df_gen[df_gen["fonte"] == fonte].sort_values("ora")
        if not d.empty:
            fig2.add_trace(
                go.Scatter(
                    x=d["ora"],
                    y=d["media_gw"],
                    mode="lines",
                    stackgroup="one",
                    name=fonte,
                    line={"color": FONTI_COLORS.get(fonte), "width": 0.5},
                )
            )
    # Self-consumption: generazione NON immessa in rete. Perimetro diverso dallo
    # stack -> traccia separata, non impilata (altrimenti il totale mescola i due).
    d_sc = df_gen[df_gen["fonte"] == "Self-consumption"].sort_values("ora")
    if not d_sc.empty:
        fig2.add_trace(
            go.Scatter(
                x=d_sc["ora"],
                y=d_sc["media_gw"],
                mode="lines",
                name="Self-consumption (fuori rete)",
                line={
                    "color": FONTI_COLORS["Self-consumption"],
                    "width": 2.5,
                    "dash": "dash",
                },
            )
        )
    fig2.update_layout(
        height=380,
        margin={"t": 20, "b": 40},
        xaxis_title="Ora del giorno",
        yaxis_title="GW",
        xaxis={"dtick": 2},
        legend={"orientation": "h", "y": -0.25},
    )
    st.plotly_chart(fig2, width="stretch")
    st.caption(
        "La campana del fotovoltaico domina il mezzogiorno; la sera il carico "
        "torna su termoelettrico e idrico. Lo stack è il **mix di rete**; "
        "`Self-consumption` è generazione non immessa in rete (perimetro "
        "diverso) ed è mostrata come traccia separata, non impilata."
    )

# ── Crescita delle punte ──────────────────────────────────────────────
st.subheader("Quanto cresce la punta")

try:
    df_ore = load_ore_alta_domanda()
except Exception as e:
    df_ore = None
    st.warning(f"Errore caricamento ore sopra soglia: {e}")

if df_ore is not None and not df_ore.empty:
    ore50 = df_ore[
        (df_ore["tipo_carico"] == "total") & (df_ore["soglia_gw"] == 50)
    ].sort_values("anno")
    picco = df_ann[df_ann["tipo_carico"] == "total"].sort_values("anno")

    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=ore50["anno"],
            y=ore50["ore"],
            name="Ore ≥ 50 GW",
            marker_color="#6366f1",
            yaxis="y",
        )
    )
    if not picco.empty:
        fig3.add_trace(
            go.Scatter(
                x=picco["anno"],
                y=picco["max_gw"],
                mode="lines+markers",
                name="Picco annuo",
                line={"color": "#dc2626", "width": 3},
                yaxis="y2",
            )
        )
    fig3.update_layout(
        height=340,
        margin={"t": 20, "b": 40},
        xaxis_title="Anno",
        yaxis={"title": "Ore ≥ 50 GW"},
        yaxis2={
            "title": "Picco (GW)",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        legend={"orientation": "h", "y": -0.2},
        xaxis={"dtick": 1},
    )
    st.plotly_chart(fig3, width="stretch")
    st.caption(
        "Il 2020 (lockdown) azzera quasi le ore sopra 50 GW; dal 2021 risalgono "
        "ma restano sotto i livelli 2019. Il picco annuo e' stabile ~56-59 GW."
    )

st.caption(
    "Note: `market` disponibile solo dal 2021 (prima esisteva solo la domanda "
    "totale). Dati Terna al netto della zona `Italy` (aggregato nazionale)."
)
st.caption("Fonti: Terna Download Center · TotalLoad/MarketLoad, ActualGeneration · CC BY 4.0")
