"""Incroci -- Capacity factor delle FER e intensita di carbonio regionale.

Dati dal compose `energia-incroci` (cross-dataset: per-fonte x capacita,
emissioni x copertura-domanda).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sources import load_capacity_factor, load_intensita_regionale

st.title("Incroci")

FONTI_COLORS = {
    "Fotovoltaico": "#f59e0b",
    "Eolico": "#059669",
    "Idrico": "#3b82f6",
    "Geotermoelettrico": "#ef4444",
}

df_cf = pd.DataFrame()

# ── Capacity factor nazionale ─────────────────────────────────────────
st.subheader("Capacity factor nazionale per fonte")

try:
    df_cf = load_capacity_factor()
    if not df_cf.empty:
        nat = (
            df_cf.groupby(["anno", "fonte"], as_index=False)[["produzione_gwh", "potenza_mw"]]
            .sum()
        )
        nat["cf_pct"] = 100.0 * nat["produzione_gwh"] / (nat["potenza_mw"] * 8.76)

        fig = go.Figure()
        for fonte in sorted(nat["fonte"].unique()):
            pts = nat[nat["fonte"] == fonte].sort_values("anno")
            fig.add_trace(go.Scatter(
                x=pts["anno"],
                y=pts["cf_pct"],
                mode="lines+markers",
                name=fonte,
                line={"color": FONTI_COLORS.get(fonte, "#ccc"), "width": 2},
            ))
        fig.update_layout(
            height=380,
            margin={"t": 20, "b": 40},
            yaxis_title="% (produzione netta / potenza netta)",
            xaxis={"dtick": 2},
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Approssimazione: produzione annuale su potenza installata a fine anno. "
            "L'idrico e' fortemente dipendente dall'annata idrologica."
        )
    else:
        st.info("Compose non ancora pubblicato — dati disponibili dopo il run della pipeline.")
except Exception as e:
    st.warning(f"Errore caricamento capacity factor: {e}")

# ── CF regionale ──────────────────────────────────────────────────────
st.subheader("Capacity factor regionale")

col_fonte, col_anno = st.columns(2)
with col_fonte:
    fonti = sorted(df_cf["fonte"].unique()) if not df_cf.empty else []
    fonte_sel = st.selectbox("Fonte", fonti, key="cf_fonte")
with col_anno:
    anni = sorted(int(a) for a in df_cf["anno"].unique()) if not df_cf.empty else []
    anno_sel = st.selectbox("Anno", anni, index=len(anni) - 1 if anni else 0, key="cf_anno")

try:
    if not df_cf.empty:
        df_r = df_cf[(df_cf["fonte"] == fonte_sel) & (df_cf["anno"] == anno_sel)]
        if not df_r.empty:
            reg = (
                df_r.groupby("regione", as_index=False)[["produzione_gwh", "potenza_mw"]]
                .sum()
            )
            reg["cf_pct"] = 100.0 * reg["produzione_gwh"] / (reg["potenza_mw"] * 8.76)
            reg = reg[reg["potenza_mw"] > 0].sort_values("cf_pct")
            fig2 = go.Figure(go.Bar(
                x=reg["cf_pct"],
                y=reg["regione"],
                orientation="h",
                marker_color=FONTI_COLORS.get(fonte_sel, "#6366f1"),
                text=reg["cf_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            ))
            fig2.update_layout(
                height=420,
                margin={"t": 10, "b": 10, "l": 160},
                xaxis_title="%",
            )
            st.plotly_chart(fig2, width="stretch")
except Exception as e:
    st.warning(f"Errore caricamento CF regionale: {e}")

# ── Intensita regionale ───────────────────────────────────────────────
st.subheader("Intensita di carbonio della copertura regionale")

try:
    df_int = load_intensita_regionale()
    if not df_int.empty:
        anni_int = sorted(int(a) for a in df_int["anno"].unique())
        anno_int = st.selectbox(
            "Anno", anni_int, index=len(anni_int) - 1, key="int_anno"
        )
        df_a = df_int[df_int["anno"] == anno_int].sort_values("intensita_g_kwh")
        fig3 = go.Figure(go.Bar(
            x=df_a["intensita_g_kwh"],
            y=df_a["regione"],
            orientation="h",
            marker_color="#dc2626",
            text=df_a["intensita_g_kwh"].apply(lambda x: f"{x:.0f}"),
            textposition="outside",
        ))
        fig3.update_layout(
            height=480,
            margin={"t": 10, "b": 10, "l": 160},
            xaxis_title="g CO2/kWh",
        )
        st.plotly_chart(fig3, width="stretch")

        st.dataframe(
            df_a[["regione", "emissioni_mt", "copertura_locale_gwh",
                  "intensita_g_kwh", "quota_rinnovabili_pct"]]
            .reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Emissioni di produzione / copertura locale della domanda (escluso saldo "
            "import/export). Media ponderata nazionale 2023: ~250 g/kWh — in linea "
            "con il bilancio elettrico internazionale (~257)."
        )
    else:
        st.info("Compose non ancora pubblicato — dati disponibili dopo il run della pipeline.")
except Exception as e:
    st.warning(f"Errore caricamento intensita: {e}")

st.caption("Fonte: compose energia-incroci (Terna, cross-dataset) · CC BY 4.0")
