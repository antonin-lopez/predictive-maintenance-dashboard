"""Sensor telemetry and physical indicators diagnostic page."""

import plotly.express as px
import streamlit as st

from src.data_loader import load_data

st.title("Sensor Diagnostics")
st.write("Bivariate analysis, thermal dissipation, and mechanical power envelopes.")

df = load_data()

SENSOR_LABELS = {
    "air_temp_k": "Air temperature (K)",
    "process_temp_k": "Process temperature (K)",
    "rotational_speed_rpm": "Rotational speed (rpm)",
    "torque_nm": "Torque (Nm)",
    "tool_wear_min": "Tool wear (min)",
    "temp_diff_k": "Temperature difference (K)",
    "mechanical_power_w": "Mechanical power (W)",
}

STATUS_LABELS = {True: "Failed", False: "OK"}
COLOR_MAP = {"OK": "gray", "Failed": "red"}


st.subheader("Sensor correlation matrix")
st.write(
    "Linear correlations between physical measurements. Notice the inverse "
    "relationship between speed and torque (constant power curve)."
)

corr = df[list(SENSOR_LABELS)].corr()
corr.index = [SENSOR_LABELS[c] for c in corr.index]
corr.columns = [SENSOR_LABELS[c] for c in corr.columns]

fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    zmin=-1,
    zmax=1,
    labels={"color": "Correlation"},
)

st.plotly_chart(fig_corr)

st.divider()


st.subheader("Bivariate sensor analysis")
st.write(
    "Pick two sensors to see how they relate, and select a failure mode "
    "to highlight its cluster."
)

FAILURE_TARGETS = {
    "failure_any": "All failures (Any)",
    "failure_tool_wear": "Tool Wear (TWF)",
    "failure_heat_dissipation": "Heat Dissipation (HDF)",
    "failure_power": "Power (PWF)",
    "failure_overstrain": "Overstrain (OSF)",
    "failure_random": "Random (RNF)",
}

col1, col2, col3 = st.columns(3)
x_axis = col1.selectbox(
    "X axis", options=list(SENSOR_LABELS), format_func=SENSOR_LABELS.get, index=0
)
y_axis = col2.selectbox(
    "Y axis", options=list(SENSOR_LABELS), format_func=SENSOR_LABELS.get, index=1
)
target_failure = col3.selectbox(
    "Highlight failure",
    options=list(FAILURE_TARGETS),
    format_func=FAILURE_TARGETS.get,
    index=0,
)

df_bivariate = df.assign(status=df[target_failure].map(STATUS_LABELS)).sort_values(
    target_failure
)

fig_bivariate = px.scatter(
    df_bivariate,
    x=x_axis,
    y=y_axis,
    color="status",
    color_discrete_map=COLOR_MAP,
    category_orders={"status": ["OK", "Failed"]},
    labels={
        x_axis: SENSOR_LABELS[x_axis],
        y_axis: SENSOR_LABELS[y_axis],
        "status": "Machine status",
    },
    opacity=0.5,
)
st.plotly_chart(fig_bivariate, use_container_width=True)

st.divider()


st.subheader("Thermal dissipation")
st.write(
    "A Heat Dissipation Failure (HDF) occurs when the air/process temperature "
    "difference drops below 8.6 K while the spindle turns below 1,380 rpm."
)

df_thermal = df.assign(
    status=df["failure_heat_dissipation"].map(STATUS_LABELS)
).sort_values("failure_heat_dissipation")

fig_thermal = px.scatter(
    df_thermal,
    x="rotational_speed_rpm",
    y="temp_diff_k",
    color="status",
    color_discrete_map=COLOR_MAP,
    category_orders={"status": ["OK", "Failed"]},
    labels={
        "rotational_speed_rpm": "Rotational speed (rpm)",
        "temp_diff_k": "Temperature difference (K)",
        "status": "HDF status",
    },
    opacity=0.5,
)
fig_thermal.add_hline(
    y=8.6, line_dash="dash", line_color="red", annotation_text="Limit: 8.6 K"
)
fig_thermal.add_vline(
    x=1380, line_dash="dash", line_color="red", annotation_text="Limit: 1,380 rpm"
)
st.plotly_chart(fig_thermal)

st.divider()


st.subheader("Mechanical power envelope")
st.write(
    "A Power Failure (PWF) occurs when mechanical power falls outside the "
    "3,500-9,000 W operating envelope."
)

df_power = df.assign(status=df["failure_power"].map(STATUS_LABELS)).sort_values(
    "failure_power"
)

fig_power = px.scatter(
    df_power,
    x="rotational_speed_rpm",
    y="mechanical_power_w",
    color="status",
    color_discrete_map=COLOR_MAP,
    category_orders={"status": ["OK", "Failed"]},
    labels={
        "rotational_speed_rpm": "Rotational speed (rpm)",
        "mechanical_power_w": "Mechanical power (W)",
        "status": "PWF status",
    },
    opacity=0.5,
)
fig_power.add_hline(
    y=3500,
    line_dash="dash",
    line_color="red",
    annotation_text="Lower limit: 3,500 W",
)
fig_power.add_hline(
    y=9000,
    line_dash="dash",
    line_color="red",
    annotation_text="Upper limit: 9,000 W",
)
st.plotly_chart(fig_power)

st.divider()

st.subheader("Overstrain envelope")
st.write(
    "An Overstrain Failure (OSF) is triggered when the product of Tool Wear and "
    "Torque exceeds critical thresholds."
)

df_overstrain = df.assign(
    status=df["failure_overstrain"].map(STATUS_LABELS)
).sort_values("failure_overstrain")

fig_osf = px.scatter(
    df_overstrain,
    x="tool_wear_min",
    y="torque_nm",
    color="status",
    color_discrete_map=COLOR_MAP,
    category_orders={"status": ["OK", "Failed"]},
    labels={
        "tool_wear_min": "Tool wear (min)",
        "torque_nm": "Torque (Nm)",
        "status": "OSF status",
    },
    opacity=0.5,
)

st.plotly_chart(fig_osf)
