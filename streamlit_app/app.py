import streamlit as st
import pandas as pd
import yaml

# --- Carga de configuración ---
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

st.title("Inventory Manager 🚀")
st.markdown("**Configuración actual:**")
st.json(config)

# --- Carga de datos de SKUs ---
df = pd.read_csv("data/raw/skus.csv")
st.markdown("**Inventario actual por SKU:**")
st.dataframe(df)

# Aquí luego añadiremos controles (selector de período, botones, gráficos…)
