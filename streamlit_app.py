import streamlit as st
from app import home

st.set_page_config(page_title="Paper Company Dashboard", layout="wide")

pages = {
    "Dashboard":       home,
    "Sales Prediction": None,   # à venir
}

st.sidebar.title("Navigation")
page = st.sidebar.radio("Pages", list(pages.keys()))

module = pages[page]
if module:
    module.render()
else:
    st.info("🚧 This page is under construction.")
