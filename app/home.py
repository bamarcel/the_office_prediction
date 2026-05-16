import streamlit as st

from services.stores import get_stores
from services.dashboard_loader import load_dashboard_data
from components import dashboard


def render():
    stores = get_stores()

    # CORRECTION : vérification None ET empty (l'ancienne version plantait si la DB était down)
    if stores is None or stores.empty:
        st.error("No store data found. Please check the database connection.")
        return

    wanted_store  = st.selectbox("Select a store:", stores["store_name"])
    selected_store = stores[stores["store_name"] == wanted_store].iloc[0]

    st.header(f"Store: {selected_store['store_name']} — Manager: {selected_store['manager']}")

    with st.spinner("Loading dashboard data...", ):
        data = load_dashboard_data(int(selected_store["store_id"]))

    dashboard.render(data)
