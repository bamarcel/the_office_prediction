import pandas as pd
import streamlit as st

from database.query_runner import run_query


@st.cache_data(ttl=300)
def get_month_data(store_id: int, month: int, year: int) -> dict:
    """
    Retourne le nombre de ventes et le montant total pour un mois donné.
    Retourne {"number_sales": 0, "amount_sales": 0.0} si aucune donnée.
    """
    row = run_query("""
        SELECT
            COUNT(*)           AS number_sales,
            SUM(total_amount)  AS amount_sales
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
          AND strftime('%Y', o.order_date) = ?
          AND strftime('%m', o.order_date) = ?
    """, (store_id, str(year), f"{month:02d}"), fetch="one")

    if not row or row[0] == 0:
        return {"number_sales": 0, "amount_sales": 0.0}

    return {
        "number_sales": int(row[0]),
        "amount_sales": float(row[1]) if row[1] else 0.0,
    }


@st.cache_data(ttl=300)
def get_all_months_data(store_id: int) -> pd.DataFrame | None:
    """
    Retourne le nombre de ventes et le montant total pour chaque mois disponible.
    Colonnes : date (MM/YYYY), number_sales, amount_sales.
    """
    rows = run_query("""
        SELECT
            strftime('%m', o.order_date) AS month,
            strftime('%Y', o.order_date) AS year,
            COUNT(*)                     AS number_sales,
            SUM(total_amount)            AS amount_sales
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
        GROUP BY year, month
        ORDER BY year, month ASC
    """, (store_id,))

    if not rows:
        return None

    return pd.DataFrame([{
        "date":          f"{r[0]}/{r[1]}",
        "number_sales":  int(r[2]),
        "amount_sales":  float(r[3]),
    } for r in rows])


@st.cache_data(ttl=300)
def get_products_sold(store_id: int, month: int, year: int) -> pd.DataFrame | None:
    """
    Retourne les produits vendus et leur quantité totale pour un mois donné.
    Colonnes : product_name, total_quantity_sold.
    """
    rows = run_query("""
        SELECT p.product_name, SUM(oi.quantity) AS total_quantity_sold
        FROM order_items oi
        JOIN orders o   ON oi.order_id  = o.order_id
        JOIN sellers s  ON o.seller_id  = s.seller_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE s.store_id = ?
          AND strftime('%Y', o.order_date) = ?
          AND strftime('%m', o.order_date) = ?
        GROUP BY p.product_name
        ORDER BY total_quantity_sold DESC
    """, (store_id, str(year), f"{month:02d}"))

    if not rows:
        return None

    return pd.DataFrame([{
        "product_name":        r[0],
        "total_quantity_sold": int(r[1]),
    } for r in rows])


@st.cache_data(ttl=300)
def get_average_basket(store_id: int, month: int, year: int) -> float:
    """Retourne la valeur moyenne du panier pour un mois donné."""
    row = run_query("""
        SELECT AVG(o.total_amount)
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
          AND strftime('%Y', o.order_date) = ?
          AND strftime('%m', o.order_date) = ?
    """, (store_id, str(year), f"{month:02d}"), fetch="one")

    return float(row[0]) if row and row[0] else 0.0


def get_dashboard_kpis(store_id, current_month, current_year, last_month, last_month_year, last_year) -> dict:
    """
    Calcule les KPIs du dashboard en comparant le mois courant
    avec le mois précédent et le même mois l'année dernière.
    """
    current   = get_month_data(store_id, current_month, current_year)
    last      = get_month_data(store_id, last_month, last_month_year)
    year_back = get_month_data(store_id, current_month, last_year)

    def pct_change(new, old):
        return ((new - old) / old * 100) if old else 0.0

    return {
        "current_sales":      current["number_sales"],
        "sales_change":       pct_change(current["number_sales"], last["number_sales"]),
        "current_amount":     current["amount_sales"],
        "amount_change":      pct_change(current["amount_sales"], last["amount_sales"]),
        "last_year_amount":   year_back["amount_sales"],
        "year_amount_change": pct_change(current["amount_sales"], year_back["amount_sales"]),
    }
