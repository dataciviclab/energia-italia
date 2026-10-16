"""Consumi per Settore -- Domestico, Industria, Servizi, Agricoltura."""

import plotly.graph_objects as go
import streamlit as st
from sources import ENERGIA_YEARS, load_settore, load_settore_storico

st.title("Consumi per Settore")

SETTORI_COLORS = {
    "Industria": "#6366f1",
    "Servizi": "#059669",
    "Domestico": "#f59e0b",
    "Agricoltura": "#8b5cf6",
}

# ── Evoluzione nazionale ─────────────────────────────────────────────
st.subheader(f"Evoluzione nazionale ({ENERGIA_YEARS[0]}-{ENERGIA_YEARS[-1]})")

try:
    df_storico = load_settore_storico()
    if not df_storico.empty:
        nat = (
            df_storico.groupby(["anno", "settore"], as_index=False)["consumo_gwh"]
            .sum()
        )
        tot = nat.groupby("anno")["consumo_gwh"].transform("sum")
        nat["pct"] = nat["consumo_gwh"] / tot * 100

        settori = sorted(nat["settore"].unique())
        fig = go.Figure()
        for settore in reversed(settori):
            pts = nat[nat["settore"] == settore].sort_values("anno")
            fig.add_trace(go.Bar(
                x=pts["anno"],
                y=pts["pct"],
                name=settore,
                marker_color=SETTORI_COLORS.get(settore, "#ccc"),
            ))
        fig.update_layout(
            barmode="stack",
            height=420,
            margin={"t": 40, "b": 40},
            title="Quota percentuale per settore",
            yaxis_title="% dei consumi",
            xaxis={"dtick": 2},
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig, width="stretch")

        totale = (
            nat.groupby("anno", as_index=False)["consumo_gwh"].sum()
            .sort_values("anno")
        )
        fig2 = go.Figure(go.Scatter(
            x=totale["anno"],
            y=totale["consumo_gwh"] / 1000,
            mode="lines+markers",
            name="Totale",
            line={"color": "#6b7280", "width": 3},
        ))
        fig2.update_layout(
            height=280,
            margin={"t": 40, "b": 40},
            title="Consumo elettrico totale nazionale",
            yaxis_title="TWh",
            xaxis={"dtick": 2},
        )
        st.plotly_chart(fig2, width="stretch")
    else:
        st.info("Nessun dato disponibile.")
except Exception as e:
    st.warning(f"Errore caricamento serie storica: {e}")

# ── Dettaglio per regione ────────────────────────────────────────────
st.subheader("Dettaglio regionale")

col_anno, col_settore = st.columns(2)
with col_anno:
    anno_sel = st.selectbox(
        "Anno", ENERGIA_YEARS, index=len(ENERGIA_YEARS) - 1, key="settore_anno"
    )
with col_settore:
    settore_sel = st.selectbox(
        "Settore", ["Industria", "Servizi", "Domestico", "Agricoltura"],
        key="settore_sel",
    )

try:
    df = load_settore(anno_sel)
    if not df.empty:
        df_s = df[df["settore"] == settore_sel].nlargest(20, "consumo_gwh")
        fig3 = go.Figure(go.Bar(
            x=df_s["consumo_gwh"],
            y=df_s["regione"],
            orientation="h",
            marker_color=SETTORI_COLORS.get(settore_sel, "#6366f1"),
        ))
        fig3.update_layout(
            height=400,
            margin={"t": 10, "b": 10, "l": 160},
            xaxis_title="GWh",
            yaxis={"autorange": "reversed"},
        )
        st.plotly_chart(fig3, width="stretch")
    else:
        st.info("Nessun dato disponibile per questo anno.")
except Exception as e:
    st.warning(f"Errore caricamento: {e}")

st.caption("Fonte: Terna Download Center (ElectricalEnergy) · CC BY 4.0")
