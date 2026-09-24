"""Emissioni -- CO2 per combustibile e regione."""

import streamlit as st
import plotly.graph_objects as go
from sources import load_emissioni_combustibile, load_emissioni_regione

st.title("Emissioni CO2")

anno = st.selectbox("Anno", list(range(2015, 2025)), index=9)

# ── Emissioni per combustibile ───────────────────────────────────────
st.subheader(f"Emissioni per combustibile — {anno}")

try:
    df = load_emissioni_combustibile(anno)
    if not df.empty:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            fig = go.Figure(go.Bar(
                x=df["emissioni_mt"],
                y=df["combustibile"],
                orientation="h",
                marker_color="#ef4444",
                text=df["emissioni_mt"].apply(lambda x: f"{x:.1f} Mt"),
                textposition="outside",
            ))
            fig.update_layout(
                height=300,
                margin={"t": 10, "b": 10, "l": 150},
                xaxis_title="Mt CO2",
            )
            st.plotly_chart(fig, width="stretch")
        with col_right:
            st.dataframe(
                df[["combustibile", "emissioni_mt", "quota_pct"]],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Nessun dato disponibile.")
except Exception as e:
    st.warning(f"Errore: {e}")

# ── Emissioni per regione ────────────────────────────────────────────
st.subheader(f"Emissioni per regione — {anno}")

try:
    df_reg = load_emissioni_regione(anno)
    if not df_reg.empty:
        top_reg = df_reg.nlargest(10, "emissioni_mt")
        fig2 = go.Figure(go.Bar(
            x=top_reg["emissioni_mt"],
            y=top_reg["regione"],
            orientation="h",
            marker_color="#f97316",
            text=top_reg["emissioni_mt"].apply(lambda x: f"{x:.1f}"),
            textposition="outside",
        ))
        fig2.update_layout(
            height=350,
            margin={"t": 10, "b": 10, "l": 150},
            xaxis_title="Mt CO2",
        )
        st.plotly_chart(fig2, width="stretch")

        if "intensita_carbone_g_kwh" in df_reg.columns:
            st.subheader("Intensita carbone per regione")
            st.dataframe(
                df_reg[["regione", "emissioni_mt", "intensita_carbone_g_kwh"]]
                .sort_values("intensita_carbone_g_kwh", ascending=False),
                use_container_width=True,
                hide_index=True,
            )
except Exception as e:
    st.warning(f"Errore: {e}")

st.caption("Fonti: Terna Download Center (GrossVsCO2Emissions) · CC BY 4.0")
