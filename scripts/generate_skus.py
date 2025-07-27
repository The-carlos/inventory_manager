import pandas as pd
import numpy as np
import yaml
import os

# --- Leer configuración ---
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Capacidad inicial total definida en config
initial_capacity = config.get('initial_capacity', None)
if initial_capacity is None:
    raise ValueError("'initial_capacity' no está definido en config/config.yaml")

# Número de SKUs de ejemplo (puedes ajustar este valor)
num_skus = 100

# Generar IDs tipo SKU0001, SKU0002, …
skus = [f"SKU{str(i).zfill(4)}" for i in range(1, num_skus + 1)]

# Distribuir la capacidad inicial entre SKUs (sumarán exactamente initial_capacity)
probabilities = np.ones(num_skus) / num_skus
stocks = np.random.multinomial(initial_capacity, probabilities)

# Ventas diarias promedio aleatorias entre 0 y 20 unidades
avg_sales = np.random.randint(0, 400, size=num_skus)

# Crear DataFrame
df = pd.DataFrame({
    'sku_id': skus,
    'stock': stocks,
    'avg_daily_sales': avg_sales
})

# Guardar CSV en data/raw
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw', 'skus.csv')
df.to_csv(output_path, index=False)

print(f"CSV generado en {output_path} con sum(stock) = {df['stock'].sum()}")
