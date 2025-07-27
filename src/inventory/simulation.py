# src/inventory/simulation.py

"""
Simulación de evolución de inventario por SKU con fechas.
"""

from typing import Optional
import pandas as pd
from datetime import date, timedelta

def simulate_inventory(
    df_skus: pd.DataFrame,
    analysis_days: int,
    start_date: Optional[date] = None,
) -> pd.DataFrame:
    """
    Simula cómo varía el inventario de cada SKU día a día.

    Parámetros
    ----------
    df_skus : pd.DataFrame
        DataFrame con columnas ['sku_id', 'stock', 'avg_daily_sales'].
    analysis_days : int
        Número de días a simular.
    start_date : date, opcional
        Fecha inicial para la simulación. Si es None, se usa la fecha de hoy.
    lead_time_days : int, opcional
        Tiempo de reposición (en días) para nuevos pedidos.

    Devuelve
    -------
    pd.DataFrame
        DataFrame formato “long” con columnas:
        ['date' (datetime.date), 'sku_id' (str), 'stock_level' (int)].
    """

    # Fecha de inicio
    if start_date is None:
        start_date = date.today()

    # Estado inicial
    stock = dict(zip(df_skus['sku_id'], df_skus['stock']))
    sales = dict(zip(df_skus['sku_id'], df_skus['avg_daily_sales']))

    records = []

    # Simular día a día
    for day in range(1, analysis_days + 1):
        # Fecha para este día de simulación
        record_date = start_date + timedelta(days=day)

        for sku_id in stock.keys():
            sold = sales.get(sku_id, 0)
            new_level = max(stock[sku_id] - sold, 0)
            stock[sku_id] = new_level

            records.append({
                'date': record_date,
                'sku_id': sku_id,
                'stock_level': new_level
            })


    return pd.DataFrame(records)
