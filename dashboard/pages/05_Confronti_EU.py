"""Confronti EU -- Italia vs paesi europei."""

import streamlit as st
import plotly.graph_objects as go
from sources import load_confronto_ue

st.title("Confronti EU")

anno = st.selectbox("Anno", [2022, 2023], index=1)

# ── Intensita carbone ────────────────────────────────────────────────
st.subheader("Intensita carbone (g CO2/kWh)")

try:
    df = load_confronto_ue(anno)
    if not df.empty and "nazione" in df.columns:
        df_sorted = df.sort_values("emissioni_co2_totali_gr_kwh")
        colors = ["#059669" if n == "Italy" else "#6366f1" for n in df_sorted["nazione"]]
        fig = go.Figure(go.Bar(
            x=df_sorted["emissioni_co2_totali_gr_kwh"],
            y=df_sorted["nazione"],
            orientation="h",
            marker_color=colors,
            text=df_sorted["emissioni_co2_totali_gr_kwh"].apply(lambda x: f"{x:.0f}"),
            textposition="outside",
        ))
        fig.update_layout(
            height=350,
            margin={"t": 10, "b": 10, "l": 120},
            xaxis_title="g CO2/kWh",
        )
        st.plotly_chart(fig, width="stretch")
    elif not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nessun dato disponibile per questo anno.")
except Exception as e:
    st.warning(f"Errore: {e}")

# ── Tabella confronto ────────────────────────────────────────────────
st.subheader("Confronto dettagliato")

try:
    df2 = load_confronto_ue(anno)
    if not df2.empty:
        cols_show = [c for c in ["nazione", "produzione_neta_twh", "richiesta_twh",
                                  "emissioni_co2_mt", "copertura_import_pct"]
                     if c in df2.columns]
        if cols_show:
            st.dataframe(df2[cols_show], use_container_width=True, hide_index=True)
except Exception as e:
    st.warning(f"Errore: {e}")

st.caption("Fonti: Terna Download Center (ElectricityBalance) · CC BY 4.0")
