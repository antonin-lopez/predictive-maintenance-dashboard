"""Project presentation and industrial context page."""

import streamlit as st

from src.data_loader import load_data

st.title("Project Presentation")
st.write("Industrial context, objectives, and dataset scope.")

df = load_data()
