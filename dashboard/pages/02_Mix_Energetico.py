"""Mix Energetico -- Evoluzione della copertura domanda per fonte."""

import streamlit as st
import plotly.graph_objects as go
from sources import load_copertura, load_copertura_regione

st.title("Mix Energetico")

st.subheader("Evoluzione copertura domanda per fonte (2015-2024)")

fonti_order = [
    "Termoelettrico tradizionale", "Idrico rinnovabile", "Fotovoltaico",
    "Eolico", "Bioenergie", "Geotermoelettrico", "Saldo import/export",
]
COLORS = {
    "Termoelettrico tradizionale": "#6b7280",
    "Idrico rinnovabile": "#3b82f6",
    "Fotovoltaico": "#f59e0b",
    "Eolico": "#059669",
    "Bioenergie": "#8b5cf6",
    "Geotermoelettrico": "#ef4444",
    "Saldo import/export": "#9ca3af",
}

all_data = []
for y in range(2015, 2025):
    try:
        df_y = load_copertura(y)
        if not df_y.empty:
            tot = df_y["copertura_gwh"].sum()
            for _, row in df_y.iterrows():
                if row["fonte"] in fonti_order:
                    all_data.append({
                        "anno": y,
                        "fonte": row["fonte"],
                        "gwh": row["copertura_gwh"],
                        "pct": row["copertura_gwh"] / tot * 100 if tot > 0 else 0,
                    })
    except Exception:
        pass

if all_data:
    fig = go.Figure()
    for fonte in reversed(fonti_order):
        pts = [d for d in all_data if d["fonte"] == fonte]
        if pts:
            fig.add_trace(go.Bar(
                x=[d["anno"] for d in pts],
                y=[d["pct"] for d in pts],
                name=fonte,
                marker_color=COLORS.get(fonte, "#ccc"),
            ))
    fig.update_layout(
        barmode="stack",
        height=450,
        margin={"t": 20, "b": 40},
        yaxis_title="% della domanda",
        xaxis=dict(dtick=1),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, width="stretch")

# ── Dettaglio regionale ──────────────────────────────────────────────
st.subheader("Dettaglio regionale")

anno_sel = st.selectbox("Anno", list(range(2015, 2025)), index=9, key="mix_anno")
try:
    df_reg = load_copertura_regione(anno_sel)
    if not df_reg.empty:
        regioni = sorted(df_reg["regione"].unique())
        regione = st.selectbox("Regione", regioni, key="mix_regione")
        df_r = df_reg[df_reg["regione"] == regione]
        if not df_r.empty:
            fig2 = go.Figure(go.Bar(
                x=df_r["copertura_gwh"],
                y=df_r["fonte"],
                orientation="h",
                marker_color="#6366f1",
            ))
            fig2.update_layout(
                height=300,
                margin={"t": 10, "b": 10, "l": 200},
                xaxis_title="GWh",
            )
            st.plotly_chart(fig2, width="stretch")
    else:
        st.info("Nessun dato regionale disponibile.")
except Exception as e:
    st.warning(f"Errore caricamento: {e}")

st.caption("Fonti: Terna Download Center · CC BY 4.0")
