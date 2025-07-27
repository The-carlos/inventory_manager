import os
import sys
import yaml
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Ajustar sys.path para incluir la raíz del proyecto ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# --- Carga de configuración ---
config_path = os.path.join(BASE_DIR, "config", "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# --- Carga de datos de SKUs ---
skus_path = os.path.join(BASE_DIR, "data", "raw", "skus.csv")
df_skus = pd.read_csv(skus_path)
if "ave_sales" in df_skus.columns:
    df_skus = df_skus.rename(columns={"ave_sales": "avg_daily_sales"})

# --- Barra lateral para parámetros ---
st.sidebar.header("Parámetros de simulación")
period = st.sidebar.number_input(
    "Días de análisis",
    min_value=1,
    max_value=365,
    value=int(config.get("analysis_period_days", 30)),
    step=1
)
selected_skus = st.sidebar.multiselect(
    "Selecciona SKUs para comparar DOH",
    options=df_skus["sku_id"].tolist()
)

# --- Simulación de inventario ---
from src.inventory.simulation import simulate_inventory

df_sim = simulate_inventory(
    df_skus=df_skus,
    analysis_days=period
)

# --- Título y configuración ---
st.title("Inventory Manager 🚀")
st.subheader("Configuración actual")
st.json(config)

# --- Inventario actual por SKU ---
st.subheader("Inventario actual por SKU")
st.dataframe(df_skus)

# --- Evolución del Stock Total ---
st.header("Evolución del Stock Total")
df_total = df_sim.groupby("date")["stock_level"].sum().reset_index()
fig1, ax1 = plt.subplots()
ax1.plot(df_total["date"], df_total["stock_level"], marker='o', label='Stock real')
# Etiquetas de valores
for idx, row in df_total.iterrows():
    ax1.annotate(
        f"{row['stock_level']}",
        (row['date'], row['stock_level']),
        textcoords="offset points",
        xytext=(0, 5),
        ha='center',
        fontsize=8
    )
# Forzar eje y desde 0\ax1.set_ylim(bottom=0)
# Forzar todas las etiquetas del eje x
ticks1 = df_total['date'].tolist()
labels1 = [d.strftime('%Y-%m-%d') for d in ticks1]
ax1.set_xticks(ticks1)
ax1.set_xticklabels(labels1, rotation=90, ha='right')

ax1.set_xlabel("Fecha")
ax1.set_ylabel("Nivel de stock")
ax1.legend()
plt.tight_layout()
st.pyplot(fig1)

# --- Comparativa por SKU vs DOH ---
st.header("Comparativa por SKU vs DOH")
if selected_skus:
    for sku in selected_skus:
        df_plot = df_sim[df_sim["sku_id"] == sku]
        fig2, ax2 = plt.subplots()
        ax2.plot(
            df_plot["date"],
            df_plot["stock_level"],
            marker='o',
            label='Stock real'
        )
        # Etiquetas de valores
        for idx, row in df_plot.iterrows():
            ax2.annotate(
                f"{row['stock_level']}",
                (row['date'], row['stock_level']),
                textcoords="offset points",
                xytext=(0, 5),
                ha='center',
                fontsize=8
            )
        # Stock necesario para DOH
        avg = df_skus.loc[df_skus["sku_id"] == sku, "avg_daily_sales"].iat[0]
        required = avg * config["default_doh"]
        ax2.axhline(
            y=required,
            linestyle='--',
            label=f"Necesario: {config['default_doh']} días ({required} uds)"
        )
        # Forzar eje y desde 0
        ax2.set_ylim(bottom=0)
        # Forzar todas las etiquetas del eje x
        ticks2 = df_plot['date'].tolist()
        labels2 = [d.strftime('%Y-%m-%d') for d in ticks2]
        ax2.set_xticks(ticks2)
        ax2.set_xticklabels(labels2, rotation=90, ha='right')

        ax2.set_title(f"SKU {sku}")
        ax2.set_xlabel("Fecha")
        ax2.set_ylabel("Nivel de stock")
        ax2.legend()
        plt.tight_layout()
        st.pyplot(fig2)
else:
    st.info("Selecciona uno o varios SKUs en la barra lateral para ver la comparativa con DOH objetivo.")
