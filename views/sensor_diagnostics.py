"""Sensor telemetry and physical indicators diagnostic page."""

import streamlit as st

from src.data_loader import load_data

st.title("Sensor Diagnostics")
st.write("Bivariate analysis, thermal dissipation, and mechanical power envelopes.")

df = load_data()
