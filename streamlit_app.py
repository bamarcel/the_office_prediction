import streamlit as st
from app import home, prediction

st.set_page_config(page_title="Paper Company Dashboard", layout="wide")

# Navigation
pages = {
    "Dashboard": home,
    "Sales Prediction": prediction,
}

st.sidebar.title("Navigation")

page = st.sidebar.radio("Pages", list(pages.keys()))

pages[page].render()
