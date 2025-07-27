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

# --- Simulación y recomendaciones ---
from src.inventory.simulation import simulate_inventory
from src.inventory.recommendation import recommend_purchases_time

df_sim = simulate_inventory(
    df_skus=df_skus,
    analysis_days=period
)
df_time_rec = recommend_purchases_time(
    df_sim=df_sim,
    df_skus=df_skus,
    default_doh=config['default_doh']
)

# --- UI Principal ---
st.title("Inventory Manager 🚀")
st.subheader("Configuración actual")
st.json(config)

st.subheader("Inventario actual por SKU")
st.dataframe(df_skus)

# --- Gráfico 1: Stock vs Compra Total por Día ---
st.header("Stock vs Compra Total por Día")
df_total = df_sim.groupby("date")["stock_level"].sum().reset_index()
df_purchase_total = df_time_rec.groupby("date")["purchase_qty"].sum().reset_index()
fig1, ax1 = plt.subplots()
# Línea de Stock Total
a1 = ax1.plot(df_total['date'], df_total['stock_level'], marker='o', label='Stock Total')
# Anotaciones de stock
def annotate_points(ax, x, y):
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi}", (xi, yi), textcoords='offset points', xytext=(0,5), ha='center', fontsize=8)
annotate_points(ax1, df_total['date'], df_total['stock_level'])
# Línea de Compra Total
a2 = ax1.bar(df_purchase_total['date'], df_purchase_total['purchase_qty'], alpha=0.5, label='Compra Total')
# Anotaciones de compra
annotate_points(ax1, df_purchase_total['date'], df_purchase_total['purchase_qty'])
# Línea de saturación objetivo del FC
stock_target = config['max_capacity'] * config['saturation_target']
ax1.axhline(
    y=stock_target,
    linestyle='--',
    color='red',
    label=f"Saturación objetivo ({int(config['saturation_target']*100)}%): {int(stock_target)} uds"
)
ax1.set_ylim(bottom=0)
# Formateo del eje X
ax1.set_xticks(df_total['date'])
ax1.set_xticklabels([d.strftime('%Y-%m-%d') for d in df_total['date']], rotation=45, ha='right')
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Unidades")
ax1.legend(loc='upper left')
plt.tight_layout()
st.pyplot(fig1)

# --- Gráfico 2: Stock vs Compra vs DOH por SKU ---
st.header("Stock y Compra vs DOH por SKU")
if selected_skus:
    for sku in selected_skus:
        df_plot = df_sim[df_sim['sku_id']==sku]
        df_purchase = df_time_rec[df_time_rec['sku_id']==sku]
        fig, ax = plt.subplots()
        # Stock nivel
        ax.plot(df_plot['date'], df_plot['stock_level'], marker='o', label='Stock')
        annotate_points(ax, df_plot['date'], df_plot['stock_level'])
        # Compra recomendada
        ax.plot(df_purchase['date'], df_purchase['purchase_qty'], marker='s', linestyle='--', label='Compra')
        annotate_points(ax, df_purchase['date'], df_purchase['purchase_qty'])
        # Línea de DOH requerido
        avg = df_skus.loc[df_skus['sku_id']==sku, 'avg_daily_sales'].iat[0]
        required = avg * config['default_doh']
        ax.axhline(
            y=required,
            linestyle=':',
            color='gray',
            label=f"Requerido DOH ({config['default_doh']} días): {int(required)} uds"
        )
        ax.set_ylim(bottom=0)
        ax.set_xticks(df_plot['date'])
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df_plot['date']], rotation=45, ha='right')
        ax.set_title(f"SKU {sku}")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Unidades")
        ax.legend(loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)
else:
    st.info("Selecciona uno o varios SKUs en la barra lateral para ver stock, compra y DOH.")
