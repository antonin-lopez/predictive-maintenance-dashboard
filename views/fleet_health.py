"""Fleet health and failure distribution page."""

import streamlit as st

from src.data_loader import load_data

st.title("Fleet Health")
st.write("Fleet-wide failure rates, quality grades, and operational statuses.")

df = load_data()
