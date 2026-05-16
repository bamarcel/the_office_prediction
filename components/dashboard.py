import datetime
import streamlit as st

from components.charts import create_sales_line_chart


def _month_label(month: int, year: int) -> str:
    return f"{datetime.date(1900, month, 1).strftime('%B')} {year}"


def render(data: dict):
    current_month    = data["current_month"]
    current_year     = data["current_year"]
    last_month       = data["last_month"]
    last_month_year  = data["last_month_year"]
    last_year        = data["last_year"]
    kpis             = data["kpis"]
    sales_data       = data["sales_data"]
    products_sold    = data["products_sold"]
    current_avg      = data["current_avg_basket"]
    last_avg         = data["last_avg_basket"]

    current_label   = _month_label(current_month, current_year)
    last_label      = _month_label(last_month, last_month_year)
    last_year_label = _month_label(current_month, last_year)

    # ── KPIs principaux ──────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label=f"Number of Sales — {current_label}",
            value=f"{kpis['current_sales']}",
            delta=f"{kpis['sales_change']:.2f} % vs {last_label}",
            border=True,
        )

    with col2:
        st.metric(
            label=f"Total Amount — {current_label}",
            value=f"${kpis['current_amount']:,.2f}",
            delta=f"{kpis['amount_change']:.2f} % vs {last_label}",
            border=True,
        )

    with col3:
        # CORRECTION : value = montant N-1, delta = évolution N vs N-1
        # (dans l'ancienne version le delta était inversé)
        st.metric(
            label=f"Total Amount — {last_year_label} (N-1)",
            value=f"${kpis['last_year_amount']:,.2f}",
            delta=f"{kpis['year_amount_change']:.2f} % vs {last_year_label}",
            border=True,
        )

    # ── Graphique des ventes dans le temps ───────────────────────────────────
    if sales_data is not None and not sales_data.empty:
        st.subheader("Sales and Amount Over the Months")
        st.plotly_chart(create_sales_line_chart(sales_data), use_container_width=True)
    else:
        st.info("No sales data available to display the chart.")

    # ── KPIs secondaires ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        if products_sold is not None and not products_sold.empty:
            st.subheader("Top Products Sold This Month")
            st.bar_chart(products_sold.set_index("product_name"), horizontal=True)
        else:
            st.info("No product sales data available for this month.")

    with col2:
        if current_avg is not None:
            basket_change = (
                ((current_avg - last_avg) / last_avg * 100)
                if last_avg else 0.0
            )
            st.subheader("Average Basket Value")
            st.metric(
                label=f"Average Basket — {current_label}",
                value=f"${current_avg:,.2f}",
                delta=f"{basket_change:.2f} % vs {last_label}",
                border=True,
            )
        else:
            st.info("No average basket value data available for this month.")
