# src/inventory/recommendation.py
"""
Recomendaciones de compra dinámicas basadas en evolución de inventario por fecha.
"""
import pandas as pd
from typing import Optional


def recommend_purchases_time(
    df_sim: pd.DataFrame,
    df_skus: pd.DataFrame,
    default_doh: int
) -> pd.DataFrame:
    """
    Para cada registro de simulación (fecha, SKU), determina si se debe comprar,
    la cantidad necesaria para cumplir el DOH mínimo y el estado de stock.

    Parámetros
    ----------
    df_sim : pd.DataFrame
        DataFrame en formato “long” con columnas ['date', 'sku_id', 'stock_level'].
    df_skus : pd.DataFrame
        DataFrame con columnas ['sku_id', 'avg_daily_sales'].
    default_doh : int
        Días On Hand deseados por SKU.

    Devuelve
    -------
    pd.DataFrame
        DataFrame con columnas:
        ['date', 'sku_id', 'stock_level', 'required_for_doh', 'purchase_qty', 'status']
    """
    # Unir ventas diarias promedio
    df = df_sim.merge(
        df_skus[['sku_id', 'avg_daily_sales']],
        on='sku_id',
        how='left'
    )

    # Calcular requerimiento para DOH
    df['required_for_doh'] = df['avg_daily_sales'] * default_doh

    # Cantidad a comprar si stock < requerido
    df['purchase_qty'] = (
        df['required_for_doh'] - df['stock_level']
    ).clip(lower=0).astype(int)

    # Determinar estado de stock
    def get_status(row):
        if row['purchase_qty'] > 0:
            return 'en escasez'
        elif row['stock_level'] > row['required_for_doh']:
            return 'en exceso'
        else:
            return 'sin cambio'

    df['status'] = df.apply(get_status, axis=1)

    # Seleccionar y ordenar columnas
    return df[
        ['date', 'sku_id', 'stock_level', 'required_for_doh', 'purchase_qty', 'status']
    ]
