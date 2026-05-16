import pandas as pd
import streamlit as st

from database.query_runner import run_query


@st.cache_data(ttl=300)
def get_stores() -> pd.DataFrame | None:
    """Retourne la liste de tous les magasins."""
    rows = run_query("SELECT store_id, store_name, city, manager FROM stores")
    if not rows:
        return None

    return pd.DataFrame(rows, columns=["store_id", "store_name", "city", "manager"])
