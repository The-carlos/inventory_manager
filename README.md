# Inventory Manager 🚀

## Descripción  
**Inventory Manager** es una herramienta interactiva para simular la evolución de inventario en bodegas de Mercado Libre y sugerir automáticamente recomendaciones de compra por SKU según **Days On Hand** (DOH), capacidad máxima y saturación objetivo.  

**Tecnologías empleadas:**  
- 🐍 Python 3.11+  
- ⚡️ Streamlit  
- 📈 Plotly  
- 🐳 Docker  
- 🔄 Google Cloud Build  
- ☁️ Google Cloud Run  

---

## 🚀 Características principales  
- **Simulación de stock por SKU**: análisis diario del nivel de inventario.  
- **Recomendaciones de compra**: calcula unidades necesarias para cubrir DOH y mantener saturación óptima.  
- **Visualizaciones interactivas**: gráficos combinados de stock y compra con Plotly en Streamlit.  
- **Exportación CSV**: descarga todo el resultado de la simulación.  
- **CI/CD completo**: Docker → Cloud Build → Artifact Registry → Cloud Run.  

---

## 🏗️ Arquitectura del Proyecto  
- **config/**: Parámetros de simulación  
  - `config/config.yaml`  
- **data/**: Datos de ejemplo (SKUs CSV)  
- **src/**: Lógica de simulación y recomendaciones  
- **streamlit_app/**: Aplicación Streamlit (UI)  
- **scripts/**: Generadores y notebooks de prueba  
- **Dockerfile.prod**: Imagen de producción  
- **cloudbuild.yaml**: Pipeline de CI  
- **service.yaml**: Manifest de Cloud Run  
- **.gcloudignore**, **.dockerignore**, **.gitignore**  

### 🌐 Entorno de Producción  
1. **CI/CD**: Cloud Build lee `cloudbuild.yaml`, construye la imagen con `Dockerfile.prod`, etiqueta y envia a Artifact Registry.  
2. **Artifact Registry**: almacena `us-central1-docker.pkg.dev/.../inventory-manager:vX`.  
3. **Despliegue**: Cloud Run consume la imagen, corre el contenedor con `$PORT`.  
4. **Escalabilidad**: autoescalado según tráfico.  
5. **Seguridad**: rol `roles/run.invoker` asignado a `allUsers` para acceso público.  
6. **Monitoreo**: Cloud Logging & Monitoring recolectan logs y métricas.  

# Principales componentes técnologicos utilizados en el despliegue a producción.
![🌐 Diagrama del entorno de producción](images/diagrama_entorno_produccion.png)

# Flujo de trabajo y despliegue del modelo.
![Diagrama de despliegue en español](images/diagrama_despliegue.png)

---

## 🔄 Flujo de Datos  
1. **Generación de SKUs**  
   - `scripts/generate_skus.py` → `data/raw/skus.csv` (campos `sku_id`, `stock`, `avg_daily_sales`).  
2. **Carga de configuración**  
   - `config/config.yaml` (capacidad, saturación, DOH, período).  
3. **Simulación**  
   - `src/inventory/simulation.py` → `simulate_inventory(df_skus, days)` → `df_sim` (`date`, `sku_id`, `stock_level`).  
4. **Recomendación**  
   - `src/inventory/recommendation.py` → `recommend_purchases_time(df_sim, df_skus, default_doh)` → `df_time_rec` (`purchase_qty`, `status`).  
5. **Visualización**  
   - Streamlit carga `df_sim` + `df_time_rec`, genera gráficos Plotly y tabla de resultados.  
6. **Descarga**  
   - Botón lateral → `df_time_rec.to_csv()` para análisis externo.  
7. **Contenerización**  
   - Docker empaqueta código, dependencias y `config/`.  
8. **CI/CD & Despliegue**  
   - Cloud Build + Cloud Run despliegan automáticamente tras cada push a `main`.  

![📊 Diagrama del flujo de datos completo](images/diagrama_flujo_de_datos.png)

---

## ⚙️ Configuración  
Archivo `config/config.yaml`:

```yaml
max_capacity: 650000         # Capacidad máxima total
initial_capacity: 400000     # Stock inicial total
saturation_target: 0.95      # Saturación objetivo (95%)
default_doh: 7               # Días On Hand por SKU
analysis_period_days: 30     # Días a simular por defecto
