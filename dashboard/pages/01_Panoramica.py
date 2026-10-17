"""Panoramica — Visione d'insieme del sistema elettrico italiano."""

import plotly.graph_objects as go
import streamlit as st
from lab_connectors.formatters import fmt_num, fmt_pct
from sources import (
    COPERTURA_YEARS,
    load_capacita,
    load_copertura,
    load_copertura_storico,
    load_emissioni_combustibile,
    load_pun_annuale,
)

st.title("⚡ Energia Italia")

year = st.selectbox("Anno", COPERTURA_YEARS, index=len(COPERTURA_YEARS) - 1)

# ── Caricamento dati ──────────────────────────────────────────────────
df_cop = load_copertura(year)
df_pun = load_pun_annuale()
df_em = load_emissioni_combustibile(year)
df_cap = load_capacita(year)

if df_cop.empty:
    st.warning("Nessun dato disponibile per questo anno.")
    st.stop()

# ── KPI principali ────────────────────────────────────────────────────
totale_gwh = df_cop["copertura_gwh"].sum()
rinn_fonti = ["Fotovoltaico", "Eolico", "Idrico rinnovabile", "Geotermoelettrico", "Bioenergie"]
rinn_gwh = df_cop[df_cop["fonte"].isin(rinn_fonti)]["copertura_gwh"].sum()
rinn_pct = rinn_gwh / totale_gwh * 100 if totale_gwh > 0 else 0

termo_gwh = df_cop[df_cop["fonte"] == "Termoelettrico tradizionale"]["copertura_gwh"].sum()
termo_pct = termo_gwh / totale_gwh * 100 if totale_gwh > 0 else 0

cap_rinn = df_cap["potenza_totale_mw"].sum() if not df_cap.empty else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Capacita rinnovabile", f"{fmt_num(cap_rinn)} MW")
with k2:
    st.metric("Quota rinnovabili", fmt_pct(rinn_pct / 100, signed=False))
with k3:
    st.metric("Termoelettrico", fmt_pct(termo_pct / 100, signed=False))
with k4:
    pun_row = df_pun[df_pun["anno"] == year] if not df_pun.empty else None
    if pun_row is not None and not pun_row.empty:
        st.metric("PUN medio", f"{pun_row['pun_medio_kwh'].iloc[0]:.4f} €/kWh")
    else:
        st.metric("PUN medio", "—")

# ── Trend quota rinnovabili ───────────────────────────────────────────
st.subheader("Evoluzione quota rinnovabili")

trend_data = []
try:
    df_storico = load_copertura_storico()
    if not df_storico.empty:
        for y, grp in df_storico.groupby("anno"):
            tot = grp["copertura_gwh"].sum()
            rin = grp[grp["fonte"].isin(rinn_fonti)]["copertura_gwh"].sum()
            trend_data.append({"anno": int(y), "rinnovabili_pct": rin / tot * 100 if tot > 0 else 0})
except Exception:
    pass

if trend_data:
    anno_max = max(trend_data, key=lambda d: d["rinnovabili_pct"])
    fig = go.Figure()
    # Fascia dello stallo post-pieco, per leggere il trend senza sovrapporre etichette
    fig.add_vrect(
        x0=anno_max["anno"], x1=trend_data[-1]["anno"],
        fillcolor="#9ca3af", opacity=0.12, line_width=0,
        annotation_text="stallo", annotation_position="top left",
    )
    fig.add_trace(go.Scatter(
        x=[d["anno"] for d in trend_data],
        y=[d["rinnovabili_pct"] for d in trend_data],
        mode="lines+markers",
        name="Rinnovabili",
        line={"color": "#059669", "width": 3},
    ))
    fig.add_trace(go.Scatter(
        x=[anno_max["anno"]],
        y=[anno_max["rinnovabili_pct"]],
        mode="markers",
        name=f"Picco {anno_max['anno']}",
        marker={"color": "#dc2626", "size": 10},
    ))
    fig.update_layout(
        height=300,
        margin={"t": 20, "b": 40},
        yaxis_title="%",
        xaxis={"dtick": 2 if len(trend_data) > 12 else 1},
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Picco storico nel {anno_max['anno']} ({anno_max['rinnovabili_pct']:.1f}%), "
        f"poi stagnazione fino al {trend_data[-1]['anno']} "
        f"({trend_data[-1]['rinnovabili_pct']:.1f}%)."
    )

# ── Top fonti ─────────────────────────────────────────────────────────
st.subheader(f"Fonti di copertura — {year}")

col_left, col_right = st.columns([2, 1])
with col_left:
    top = df_cop.nlargest(8, "copertura_gwh")
    fig2 = go.Figure(go.Bar(
        x=top["copertura_gwh"],
        y=top["fonte"],
        orientation="h",
        marker_color="#6366f1",
    ))
    fig2.update_layout(
        height=300,
        margin={"t": 10, "b": 10, "l": 200},
        xaxis_title="GWh",
    )
    st.plotly_chart(fig2, width="stretch")

with col_right:
    st.dataframe(
        df_cop[["fonte", "copertura_gwh", "quota_pct"]].sort_values("copertura_gwh", ascending=False),
        width="stretch",
        hide_index=True,
    )

st.caption(
    "Nota: la copertura (Terna, ~320 TWh) e la richiesta del bilancio internazionale "
    "(~305 TWh) usano confini di sistema leggermente diversi — non sono direttamente confrontabili."
)
st.caption("Fonti: Terna Download Center · Dati D-1 · CC BY 4.0")
