import datetime
import utils.utils as u

def load_dashboard_data(store_id):
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    last_year = current_year - 1

    # On retrouve toutes les données nécessaires pour le dashboard
    kpis = u.getDashboardKPIs(store_id, current_month, current_year, last_month, last_month_year, last_year)
    sales_data = u.getAllMonthsNumberAndAmount(store_id)
    products_sold = u.getNumberOfProductsSold(store_id, current_month, current_year)
    current_avg_basket = u.getAverageBasketValue(store_id, current_month, current_year)
    last_avg_basket = u.getAverageBasketValue(store_id, last_month, last_month_year)

    return {
        "current_month": current_month,
        "current_year": current_year,
        "last_month": last_month,
        "last_month_year": last_month_year,
        "last_year": last_year,

        "kpis": kpis,
        "sales_data": sales_data,
        "products_sold": products_sold,
        "current_avg_basket": current_avg_basket,
        "last_avg_basket": last_avg_basket,
    }
