import streamlit as st
import utils.utils as u

import components.dashboard as dashboard
from services.dashboard_loader import load_dashboard_data

def render():
    stores = u.getStores()

    if stores.empty:
        st.error("No store names found in the database.")
        return
    
    wanted_store = st.selectbox("Select a store:", stores['store_name'])
    selected_store = stores[stores["store_name"] == wanted_store].iloc[0]
    
    st.header(f"Store: {selected_store['store_name']} - Manager: {selected_store['manager']}")

    # On charge proprement les données du magasin sélectionné
    with st.spinner("Loading dashboard data...", width="stretch"):
        data_loaded = load_dashboard_data(selected_store["store_id"])

    # qu'on peut ensuite afficher dans le dashboard
    dashboard.render(data_loaded)
