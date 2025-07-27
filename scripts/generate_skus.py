import pandas as pd
import numpy as np

# Número de SKUs de ejemplo
num_skus = 100

# Generar IDs tipo SKU0001, SKU0002, …
skus = [f"SKU{str(i).zfill(4)}" for i in range(1, num_skus + 1)]

# Stock aleatorio entre 0 y 300
stocks = np.random.randint(0, 301, size=num_skus)

# Ventas diarias promedio aleatorias entre 0 y 20 unidades
avg_sales = np.random.randint(0, 21, size=num_skus)

df = pd.DataFrame({
    "sku_id": skus,
    "stock": stocks,
    "avg_daily_sales": avg_sales
})

# Guardar CSV en data/raw
df.to_csv("data/raw/skus.csv", index=False)

print("CSV generado en data/raw/skus.csv con columnas sku_id, stock, avg_daily_sales")
