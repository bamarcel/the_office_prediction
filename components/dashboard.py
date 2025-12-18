import streamlit as st
import datetime
import utils.utils as u

def render(data):

    # On récupère toutes les données reçues pour le dashboard
    current_month = data["current_month"]                             # Défini le mois courant
    current_year = data["current_year"]                               # Défini l'année courante              
    last_month = data["last_month"]                                   # Défini le mois précédent 
    last_month_year = data["last_month_year"]                         # Défini l'année du mois précédent
    last_year = data["last_year"]                                     # Défini l'année précédente       

    (
        current_month_sales,                                          # Nombre de ventes du mois courant
        month_sales_change,                                           # Variation des ventes par rapport au mois précédent
        current_month_amount,                                         # Montant total des ventes du mois courant
        month_amount_change,                                          # Variation du montant des ventes par rapport au mois précédent
        last_year_month_amount,                                       # Montant total des ventes du même mois l'année précédente
        year_amount_change                                            # Variation du montant des ventes par rapport au même mois l'année précédente
    ) = data["kpis"]

    sales_data = data["sales_data"]                                   # Données de ventes pour le graphique
    products_sold = data["products_sold"]                             # Produits vendus ce mois-ci    
    current_month_average_basket = data["current_avg_basket"]         # Valeur moyenne du panier ce mois-ci
    last_month_average_basket = data["last_avg_basket"]               # Valeur moyenne du panier le mois précédent

    # Gestion des KPIs principaux
    if current_month_sales is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Number of Sales - {datetime.date(1900, current_month, 1).strftime('%B')} {current_year}",
                value=f"{current_month_sales}",
                delta=f"{month_sales_change:.2f} % vs {datetime.date(1900, last_month, 1).strftime('%B')} {last_month_year}",
                border=True
            )

        with col2:
            st.metric(
                label=f"Total Amount Sold - {datetime.date(1900, current_month, 1).strftime('%B')} {current_year}",
                value=f"${current_month_amount:,.2f}",
                delta=f"{month_amount_change:.2f} % vs {datetime.date(1900, last_month, 1).strftime('%B')} {last_month_year}",
                border=True
            )

        with col3:
            st.metric(
                label=f"Total Amount Sold - {datetime.date(1900, current_month, 1).strftime('%B')} {last_year}",
                value=f"${last_year_month_amount:,.2f}",
                delta=f"{year_amount_change:.2f} % vs {datetime.date(1900, current_month, 1).strftime('%B')} {current_year}",
                border=True
            )
    else:
        st.info("No sales data available to display KPIs.")

    # Gestion du graphique des ventes et montants sur les mois
    if sales_data is not None and not sales_data.empty:
        st.subheader("Sales and Amount Over the Months")
        line_chart = u.createLineChart(sales_data)
        st.plotly_chart(line_chart, width='stretch')
    else:
        st.info("No sales data available to display the chart.")

    # Gestin des KPIs secondaires
    col1, col2 = st.columns(2)

    with col1:
        if products_sold is not None:
            st.subheader("Top Products Sold This Month")
            st.bar_chart(products_sold.set_index('product_name'), horizontal=True)
        else:
            st.info("No product sales data available for this month.")

    with col2:
        if current_month_average_basket is not None:
            basket_change = ((current_month_average_basket - last_month_average_basket) / last_month_average_basket * 100) if last_month_average_basket != 0 else 0
            st.subheader("Average Basket Value This Month")
            st.metric(
                label=f"Average Basket Value - {datetime.date(1900, current_month, 1).strftime('%B')} {current_year}",
                value=f"${current_month_average_basket:,.2f}",
                delta=f"{basket_change:.2f} % vs {datetime.date(1900, last_month, 1).strftime('%B')} {last_month_year}",
                border=True
            )
        else:
            st.info("No average basket value data available for this month.")