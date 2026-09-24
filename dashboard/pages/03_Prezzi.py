"""Prezzi -- PUN, PSV e correlazione con le rinnovabili."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sources import load_pun_mensile, load_pun_annuale

st.title("Prezzi")

# ── PUN mensile ──────────────────────────────────────────────────────
st.subheader("PUN mensile (2020-2026)")

try:
    df = load_pun_mensile()
    if not df.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=list(range(len(df))),
                y=df["pun_medio_kwh"],
                mode="lines+markers",
                name="PUN (EUR/kWh)",
                line=dict(color="#6366f1", width=2),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=list(range(len(df))),
                y=df["psv_medio_smc"],
                mode="lines+markers",
                name="PSV (EUR/Smc)",
                line=dict(color="#f59e0b", width=2),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            height=350,
            margin={"t": 20, "b": 40},
            xaxis_title="Mese",
            legend=dict(orientation="h", y=-0.2),
        )
        fig.update_yaxes(title_text="EUR/kWh", secondary_y=False)
        fig.update_yaxes(title_text="EUR/Smc", secondary_y=True)
        st.plotly_chart(fig, width="stretch")
except Exception as e:
    st.warning(f"Errore: {e}")

# ── PUN annuale ──────────────────────────────────────────────────────
st.subheader("PUN medio annuale")

try:
    df_ann = load_pun_annuale()
    if not df_ann.empty:
        fig2 = go.Figure(go.Bar(
            x=df_ann["anno"],
            y=df_ann["pun_medio_kwh"],
            marker_color="#6366f1",
            text=df_ann["pun_medio_kwh"].apply(lambda x: f"{x:.4f}"),
            textposition="outside",
        ))
        fig2.update_layout(
            height=300,
            margin={"t": 20, "b": 40},
            yaxis_title="EUR/kWh",
            xaxis=dict(dtick=1),
        )
        st.plotly_chart(fig2, width="stretch")

        st.dataframe(
            df_ann[["anno", "pun_medio_kwh", "psv_medio_smc", "pun_min_kwh", "pun_max_kwh"]],
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.warning(f"Errore: {e}")

# ── Statistiche ──────────────────────────────────────────────────────
st.subheader("Statistiche")

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PUN medio storico", f"{df['pun_eur_kwh'].mean():.4f} EUR/kWh")
    with col2:
        st.metric("PSV medio", f"{df['psv_eur_smc'].mean():.4f} EUR/Smc")

if not df_ann.empty:
    col3, col4 = st.columns(2)
    with col3:
        st.metric("PUN minimo annuale", f"{df_ann['pun_min_kwh'].min():.4f} EUR/kWh")
    with col4:
        st.metric("PUN massimo annuale", f"{df_ann['pun_max_kwh'].max():.4f} EUR/kWh")

st.caption("Fonti: GME (Portale Offerte) · CC BY 4.0")
