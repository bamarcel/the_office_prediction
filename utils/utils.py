import pandas as pd
import plotly.express as px
import streamlit as st

import datetime

from database.connect_db import connect_db

# Exécuteur de requêtes SQL
def run_query(query, params=None, fetch="all"):
    conn = connect_db()
    if not conn:
        print("[" + str(datetime.datetime.now()) + "] — DB connection failed")
        return None

    try:
        cur = conn.cursor()
        
        cur.execute(query, params or ())
        
        if fetch == "one":
            return cur.fetchone()
        return cur.fetchall()
    
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — SQL Error: {e}")
        return None
    finally:
        conn.close()


# Récupère la liste de tous les magasins
@st.cache_data(ttl=300)
def getStores():
    rows = run_query("SELECT store_id, store_name, city, manager FROM stores")
    if not rows:
        return None

    return pd.DataFrame([{
        "store_id": r[0],
        "store_name": r[1],
        "city": r[2],
        "manager": r[3],
    } for r in rows])


# Récupère les données de ventes pour un mois donné
### number_sales : nombre de ventes
### amount_sales : montant des ventes
@st.cache_data(ttl=300)
def getMonthData(store_id, month, year):
    print("Fetching month data for store_id:", store_id, "month:", month, "year:", year)
    row = run_query("""
        SELECT
            COUNT(*) AS number_sales,
            SUM(total_amount) AS amount_sales
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
          AND strftime('%Y', o.order_date) = ?
          AND strftime('%m', o.order_date) = ?
    """, (int(store_id), str(year), f"{month:02d}"), fetch="one")

    print("Query result:", row)

    if not row:
        return {"number_sales": 0, "amount_sales": 0.0}

    return {
        "number_sales": int(row[0]),
        "amount_sales": float(row[1])
    }


# Récupère les données de ventes pour tous les mois disponibles
### number_sales : nombre de ventes
### amount_sales : montant des ventes
@st.cache_data(ttl=300)
def getAllMonthsNumberAndAmount(store_id):
    rows = run_query("""
        SELECT
            strftime('%m-%Y', o.order_date) AS month,
            COUNT(*) AS number_sales,
            SUM(total_amount) AS amount_sales
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
        GROUP BY month
        ORDER BY month ASC
    """, (int(store_id),))

    if not rows:
        return None

    df = pd.DataFrame([{
        "date": r[0][5:7] + "/" + r[0][:4],     # Conversion to MM/YYYY format
        "number_sales": int(r[1]),
        "amount_sales": float(r[2])
    } for r in rows])


    return df


# Récupère le nombre de produits vendus pour un mois donné
### product_name : nom du produit
### total_quantity_sold : quantité totale vendue
@st.cache_data(ttl=300)
def getNumberOfProductsSold(store_id, month, year):
    rows = run_query("""
        SELECT p.product_name, SUM(oi.quantity) AS total_quantity_sold
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN sellers s ON o.seller_id = s.seller_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE s.store_id = ?
          AND strftime('%Y', o.order_date) = ?
          AND strftime('%m', o.order_date) = ?
        GROUP BY p.product_name
        ORDER BY total_quantity_sold DESC
    """, (int(store_id), str(year), f"{month:02d}"))

    if not rows:
        return None

    return pd.DataFrame([{
        "product_name": r[0],
        "total_quantity_sold": int(r[1])
    } for r in rows])


# Récupère la valeur moyenne du panier pour un mois donné
@st.cache_data(ttl=300)
def getAverageBasketValue(store_id, month, year):
    row = run_query("""
        SELECT AVG(o.total_amount)
        FROM orders o
        JOIN sellers s ON o.seller_id = s.seller_id
        WHERE s.store_id = ?
            AND strftime('%Y', o.order_date) = ?
            AND strftime('%m', o.order_date) = ?
    """, (int(store_id), str(year), f"{month:02d}"), fetch="one")

    return float(row[0]) if row and row[0] else 0.0


# Récupère les KPIs du dashboard pour le magasin et les périodes données
### current_sales : nombre de ventes du mois courant
### sales_change : variation des ventes par rapport au mois précédent
### current_amount : montant total des ventes du mois courant
### amount_change : variation du montant des ventes par rapport au mois précédent
### last_year_amount : montant total des ventes du même mois l'année précédente
### year_amount_change : variation du montant des ventes par rapport au même mois l'année précédente
@st.cache_data(ttl=300)
def getDashboardKPIs(store_id, current_month, current_year, last_month, last_month_year, last_year):
    current = getMonthData(store_id, current_month, current_year)
    last = getMonthData(store_id, last_month, last_month_year)
    year_back = getMonthData(store_id, current_month, last_year)

    current_sales = current["number_sales"]
    last_sales = last["number_sales"]
    sales_change = ((current_sales - last_sales) / last_sales * 100) if last_sales else 0

    current_amount = current["amount_sales"]
    last_amount = last["amount_sales"]
    amount_change = ((current_amount - last_amount) / last_amount * 100) if last_amount else 0

    last_year_amount = year_back["amount_sales"]
    year_amount_change = ((current_amount - last_year_amount) / last_year_amount * 100) if last_year_amount else 0

    return (
        current_sales,
        sales_change,
        current_amount,
        amount_change,
        last_year_amount,
        year_amount_change
    )


# Création du line chart pour les ventes et montants sur les mois
# INFO : utilisation de plotly pour un graphique avec double y-axes
def createLineChart(sales_data):
    # Création du graphique avec plotly
    fig = px.line(sales_data, x='date', y=['number_sales', 'amount_sales'], labels={
        'date': 'Date',
        'value': 'Value',
        'variable': 'Metric'
    })

    # Configurer les axes y pour avoir deux échelles différentes
    fig.update_layout(
        yaxis=dict(
            title='Number of Sales',
            side='left'
        ),
        yaxis2=dict(
            title='Amount Sold ($)',
            overlaying='y',
            side='right'
        )
    )

    # Assigner chaque série de données à l'axe y approprié
    fig.update_traces(yaxis='y1', selector=dict(name='number_sales'))
    fig.update_traces(yaxis='y2', selector=dict(name='amount_sales'))

    # Personnalisation des couleurs
    fig.update_traces(
        line=dict(color='#1f77b4'),         # bleu
        selector=dict(name='number_sales')
    )
    fig.update_traces(
        line=dict(color='#ff7f0e'),         # orange
        selector=dict(name='amount_sales')
    )

    return fig