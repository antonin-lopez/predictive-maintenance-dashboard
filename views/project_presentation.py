"""Project presentation and dataset overview page."""

import pandas as pd
import streamlit as st

from src.data_loader import load_data

df = load_data()

st.title("Project Presentation")

st.write(
    """
    This project works with the **AI4I 2020 Predictive Maintenance Dataset**, a synthetic dataset
    published on the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset).
    It reproduces realistic sensor readings from an industrial milling machine, along with the
    failures that occurred during operation.

    The goal is to predict, from live sensor readings, whether the machine is heading towards a
    failure — and if so, which failure mode is responsible.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Records", f"{len(df):,}")
col2.metric("Sensor features", "5")
col3.metric("Failure rate", f"{df['failure_any'].mean() * 100:.1f}%")

st.subheader("A look at the raw data")
st.dataframe(df.head(10))

st.subheader("What each column means")
st.write(
    """
    - **Type** — product quality variant: Low (L), Medium (M) or High (H)
    - **Air temperature [K]** — ambient temperature around the machine
    - **Process temperature [K]** — temperature of the milling process itself
    - **Rotational speed [rpm]** — spindle rotation speed
    - **Torque [Nm]** — torque applied during milling
    - **Tool wear [min]** — cumulative time the current tool has been in use

    Two columns are engineered from the raw sensors, matching the definitions used for HDF and PWF:
    - **temp_diff_k** — process minus air temperature
    - **mechanical_power_w** — torque * rotational speed (converted to rad/s)
    """
)

st.subheader("Failure modes")
st.write(
    "A machine failure (`failure_any`) is triggered by one of these five physical mechanisms "
    "(with 9 rare events left unassigned in the original dataset):"
)

failure_taxonomy = pd.DataFrame(
    [
        {
            "Code": "TWF",
            "Failure": "Tool Wear Failure",
            "Cause": "Tool degrades past a critical wear threshold (~200-240 min).",
        },
        {
            "Code": "HDF",
            "Failure": "Heat Dissipation Failure",
            "Cause": "Air/process temperature difference too small (< 8.6 K) at low speed.",
        },
        {
            "Code": "PWF",
            "Failure": "Power Failure",
            "Cause": "Mechanical power (torque * speed) outside the 3,500-9,000 W operating range.",
        },
        {
            "Code": "OSF",
            "Failure": "Overstrain Failure",
            "Cause": "Combination of high torque and tool wear causes fatigue.",
        },
        {
            "Code": "RNF",
            "Failure": "Random Failure",
            "Cause": "Rare failure with no identifiable sensor signature (~0.1% of records).",
        },
    ]
)

st.dataframe(failure_taxonomy, hide_index=True)
