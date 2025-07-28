import os
import sys
import yaml
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --- Ajustar sys.path para incluir la raíz del proyecto ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# --- Carga de configuración ---
config_path = os.path.join(BASE_DIR, "config", "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# --- Función para cargar SKUs ---
def load_skus():
    skus_path = os.path.join(BASE_DIR, "data", "raw", "skus.csv")
    df = pd.read_csv(skus_path)
    if "ave_sales" in df.columns:
        df = df.rename(columns={"ave_sales": "avg_daily_sales"})
    return df

df_skus = load_skus()

# --- Sidebar: Parámetros de simulación ---
st.sidebar.header("🔧 Parámetros de simulación")
period = st.sidebar.number_input(
    "Días de análisis:", min_value=1, max_value=365,
    value=int(config.get("analysis_period_days", 30)), step=1,
    help="Selecciona cuántos días quieres simular la evolución de inventario."
)
selected_skus = st.sidebar.multiselect(
    "Selecciona SKUs (para mostrar DOH):", options=df_skus["sku_id"].tolist(),
    help="Elige uno o más SKUs para comparar nivel de stock con los DOH requeridos."
)

# --- Simulación y recomendaciones ---
from src.inventory.simulation import simulate_inventory
from src.inventory.recommendation import recommend_purchases_time

df_sim = simulate_inventory(df_skus, analysis_days=period)
df_time_rec = recommend_purchases_time(
    df_sim, df_skus, default_doh=config['default_doh']
)

# --- Botón de descarga (siempre visible) ---
csv_data = df_time_rec.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Descargar simulación",
    data=csv_data,
    file_name="simulacion_inventario.csv",
    mime="text/csv",
    help="Descarga los resultados completos de la simulación en CSV."
)

# --- UI Principal ---
st.title("🚀 Inventory Manager")
st.markdown(
    "Bienvenido a **Inventory Manager**, la herramienta interactiva para simular tu inventario. "
    "Ajusta parámetros en la barra lateral y explora los resultados. 👇"
)

# --- Configuración actual ---
st.subheader("⚙️ Configuración actual")
st.markdown(
    "La configuración cargada desde `config/config.yaml` define la capacidad máxima, saturación objetivo, "
    "días on hand (`DOH`) y periodo de análisis por defecto."
)
st.json(config)

# --- Inventario inicial ---
st.subheader("📦 Inventario actual por SKU")
st.markdown(
    "A continuación, se muestran los SKUs y su stock inicial junto con la venta diaria promedio."
)
st.dataframe(df_skus)

# --- Gráfico Principal: Stock vs Compra Total ---
st.header("📈 Stock vs Compra Total por Día")
st.markdown(
    "Este gráfico muestra la evolución del stock total en el almacén y la cantidad de inventario "
    "que se recomienda comprar para mantener niveles óptimos."
)
# Datos agregados
df_total = df_sim.groupby("date")["stock_level"].sum().reset_index()
df_purchase = df_time_rec.groupby("date")["purchase_qty"].sum().reset_index()
target_level = config['max_capacity'] * config['saturation_target']

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=df_purchase['date'], y=df_purchase['purchase_qty'], name='Compra Total', opacity=0.5,
    hoverinfo='skip'
))
fig1.add_trace(go.Scatter(
    x=df_total['date'], y=df_total['stock_level'], mode='lines+markers', name='Stock Total',
    customdata=df_purchase['purchase_qty'], hovertemplate=(
        "Stock: %{y:,.0f}<br>Compra necesaria: %{customdata:,.0f}<extra></extra>"
    )
))
fig1.add_trace(go.Scatter(
    x=[df_total['date'].min(), df_total['date'].max()],
    y=[target_level, target_level], mode='lines', line=dict(dash='dash', color='red'),
    name=f"Saturación objetivo ({int(config['saturation_target']*100)}%)"
))
fig1.update_layout(
    xaxis_title='Fecha', yaxis_title='Unidades', hovermode='x unified',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
st.plotly_chart(fig1, use_container_width=True)

# --- Gráfico Secundario: Stock vs Compra vs DOH por SKU ---
st.header("🔍 Stock y Compra vs DOH por SKU")
st.markdown(
    "Selecciona uno o más SKUs en la barra lateral para ver la comparación entre stock, compra recomendada, "
    "y DOH (`Days On Hand`) requerido."
)
if selected_skus:
    for sku in selected_skus:
        df_plot = df_sim[df_sim['sku_id'] == sku]
        df_purchase_sku = df_time_rec[df_time_rec['sku_id'] == sku]
        doh_req = int(df_skus.loc[df_skus['sku_id'] == sku, 'avg_daily_sales'].iat[0] * config['default_doh'])

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_purchase_sku['date'], y=df_purchase_sku['purchase_qty'], mode='lines+markers', name='Compra', hoverinfo='skip'
        ))
        fig2.add_trace(go.Scatter(
            x=df_plot['date'], y=df_plot['stock_level'], mode='lines+markers', name='Stock', customdata=df_purchase_sku['purchase_qty'],
            hovertemplate=(
                "Stock: %{y:,.0f}<br>Compra necesaria: %{customdata:,.0f}<br>" +
                f"DOH requerido ({config['default_doh']} días): {doh_req:,}" +
                "<extra></extra>"
            )
        ))
        fig2.add_trace(go.Scatter(
            x=[df_plot['date'].min(), df_plot['date'].max()], y=[doh_req, doh_req], mode='lines',
            line=dict(dash='dot', color='gray'), name=f"DOH requerido ({config['default_doh']} días)"
        ))
        fig2.update_layout(
            xaxis_title='Fecha', yaxis_title='Unidades', hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Selecciona uno o varios SKUs en la barra lateral para ver stock, compra y DOH.")

# --- Tabla de resultados de simulación ---
st.header("📊 Resultados de la Simulación")
st.markdown(
    "Visualiza en formato de tabla los valores diarios por SKU: stock, compra recomendada y estado."
)
df_results = df_time_rec[['date','sku_id','stock_level','purchase_qty','status']].copy()
df_results = df_results.rename(columns={
    'date':'Fecha','sku_id':'SKU','stock_level':'Stock',
    'purchase_qty':'Compra Necesaria','status':'Status'
})
st.dataframe(df_results)

# --- Pie de página ---
st.markdown("---")
st.markdown("💡 **Tip:** Ajusta los parámetros y explora diferentes escenarios para optimizar tu inventario.")
