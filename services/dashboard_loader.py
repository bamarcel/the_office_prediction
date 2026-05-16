import datetime
from services import sales


def load_dashboard_data(store_id: int) -> dict:
    """
    Charge toutes les données nécessaires au dashboard pour un magasin donné.
    datetime.now() est appelé une seule fois pour éviter toute incohérence
    si le script tourne autour du changement de mois/d'année.
    """
    now = datetime.datetime.now()

    current_year  = now.year
    current_month = now.month
    last_month      = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year      if current_month > 1 else current_year - 1
    last_year       = current_year - 1

    kpis = sales.get_dashboard_kpis(
        store_id,
        current_month, current_year,
        last_month,    last_month_year,
        last_year,
    )

    return {
        # Périodes
        "current_month":   current_month,
        "current_year":    current_year,
        "last_month":      last_month,
        "last_month_year": last_month_year,
        "last_year":       last_year,

        # Données
        "kpis":            kpis,
        "sales_data":      sales.get_all_months_data(store_id),
        "products_sold":   sales.get_products_sold(store_id, current_month, current_year),
        "current_avg_basket": sales.get_average_basket(store_id, current_month, current_year),
        "last_avg_basket":    sales.get_average_basket(store_id, last_month, last_month_year),
    }
