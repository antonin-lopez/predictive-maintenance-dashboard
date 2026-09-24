"""Main application entry point and navigation orchestrator."""

import streamlit as st

st.set_page_config(
    page_title="Predictive Maintenance",
    layout="wide",
    initial_sidebar_state="expanded",
)

nav = st.navigation(
    [
        st.Page(
            "views/project_presentation.py",
            title="Project Presentation",
            default=True,
        ),
        st.Page(
            "views/fleet_health.py",
            title="Fleet Health",
        ),
        st.Page(
            "views/sensor_diagnostics.py",
            title="Sensor Diagnostics",
        ),
    ]
)

nav.run()
