"""Fleet health and failure distribution page."""

import plotly.express as px
import streamlit as st

from src.data_loader import load_data

st.title("Fleet Health")
st.write("Fleet-wide failure rates, quality grades, and operational statuses.")

df = load_data()


total_machines = len(df)
total_failures = int(df["failure_any"].sum())
failure_rate = total_failures / total_machines

col1, col2, col3 = st.columns(3)
col1.metric("Fleet size", f"{total_machines:,}")
col2.metric("Failures recorded", f"{total_failures:,}")
col3.metric("Overall failure rate", f"{failure_rate:.2%}")

st.divider()


st.subheader("Failure rate by quality grade")
st.write(
    "Quality grade reflects the product variant milled by the machine "
    "(Low, Medium, High). Comparing failure rates across grades shows whether "
    "one variant is more failure-prone than the others."
)

failure_by_grade = df.groupby("product_type")["failure_any"].agg(
    machines="count", failures="sum"
)
failure_by_grade["failure_rate_pct"] = (
    failure_by_grade["failures"] / failure_by_grade["machines"] * 100
)

st.dataframe(
    failure_by_grade.reset_index(),
    column_config={
        "product_type": "Product type",
        "machines": st.column_config.NumberColumn("Machines", format="%d"),
        "failures": st.column_config.NumberColumn("Failures", format="%d"),
        "failure_rate_pct": st.column_config.NumberColumn(
            "Failure rate", format="%.2f%%"
        ),
    },
    hide_index=True,
)

st.divider()


st.subheader("Failure mode breakdown")
st.write(
    "Each bar is a distinct physical failure mechanism. A single record can "
    "trigger more than one mode at once."
)

failure_mode_labels = {
    "failure_tool_wear": "Tool Wear (TWF)",
    "failure_heat_dissipation": "Heat Dissipation (HDF)",
    "failure_power": "Power (PWF)",
    "failure_overstrain": "Overstrain (OSF)",
    "failure_random": "Random (RNF)",
}

mode_counts = (
    df[list(failure_mode_labels)]
    .sum()
    .rename(failure_mode_labels)
    .sort_values(ascending=True)
)

fig = px.bar(
    x=mode_counts.values,
    y=mode_counts.index,
    orientation="h",
    labels={"x": "Occurrences", "y": "Failure"},
)

st.plotly_chart(fig)

st.divider()


st.subheader("Failure incident log")
st.write(
    "Every record where at least one failure mode was triggered, most worn tool first."
)

flagged_machines = df[df["failure_any"]].sort_values("tool_wear_min", ascending=False)

st.dataframe(
    flagged_machines,
    column_config={
        "product_id": "Product ID",
        "product_type": "Type",
        "air_temp_k": st.column_config.NumberColumn(
            "Air Temp",
            help="ambient temperature around the machine",
            format="%.1f K",
        ),
        "process_temp_k": st.column_config.NumberColumn(
            "Process Temp",
            help="temperature of the milling process itself",
            format="%.1f K",
        ),
        "rotational_speed_rpm": st.column_config.NumberColumn(
            "Speed",
            help="spindle rotation speed",
            format="%d rpm",
        ),
        "torque_nm": st.column_config.NumberColumn(
            "Torque",
            help="torque applied during milling",
            format="%.1f Nm",
        ),
        "tool_wear_min": st.column_config.NumberColumn(
            "Tool Wear",
            help="cumulative time the current tool has been in use",
            format="%d min",
        ),
        "failure_any": st.column_config.CheckboxColumn("Failed?"),
        "failure_tool_wear": st.column_config.CheckboxColumn(
            "TWF", help="Tool Wear Failure"
        ),
        "failure_heat_dissipation": st.column_config.CheckboxColumn(
            "HDF", help="Heat Dissipation Failure"
        ),
        "failure_power": st.column_config.CheckboxColumn("PWF", help="Power Failure"),
        "failure_overstrain": st.column_config.CheckboxColumn(
            "OSF", help="Overstrain Failure"
        ),
        "failure_random": st.column_config.CheckboxColumn("RNF", help="Random Failure"),
        "temp_diff_k": st.column_config.NumberColumn(
            "Temp Diff",
            help="process minus air temperature",
            format="%.1f K",
        ),
        "mechanical_power_w": st.column_config.NumberColumn(
            "Mechanical Power",
            help="torque x rotational speed",
            format="%.0f W",
        ),
    },
    hide_index=True,
)
