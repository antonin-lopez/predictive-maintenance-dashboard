"""Industrial telemetry data loading and preprocessing module."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "ai4i2020.csv"

_RENAME_MAPPING = {
    "UDI": "record_id",
    "Product ID": "product_id",
    "Type": "product_type",
    "Air temperature [K]": "air_temp_k",
    "Process temperature [K]": "process_temp_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "failure_any",
    "TWF": "failure_tool_wear",
    "HDF": "failure_heat_dissipation",
    "PWF": "failure_power",
    "OSF": "failure_overstrain",
    "RNF": "failure_random",
}

_FAILURE_COLUMNS = [
    "failure_any",
    "failure_tool_wear",
    "failure_heat_dissipation",
    "failure_power",
    "failure_overstrain",
    "failure_random",
]

_PRODUCT_TYPE_DTYPE = pd.CategoricalDtype(categories=["L", "M", "H"], ordered=True)


def _validate_raw_schema(df: pd.DataFrame) -> None:
    """Fail fast if the source CSV is empty or lacks required telemetry columns."""
    if df.empty:
        raise ValueError("Source CSV contains no data rows.")
    missing = set(_RENAME_MAPPING.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Source CSV missing required column(s): {sorted(missing)}")


@st.cache_data
def load_data(filepath: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load raw telemetry data, standardize schema, and compute engineering features."""
    df = pd.read_csv(filepath)
    _validate_raw_schema(df)
    df = df.rename(columns=_RENAME_MAPPING).set_index("record_id")

    # Types optimization
    df[_FAILURE_COLUMNS] = df[_FAILURE_COLUMNS].astype(bool)
    df["product_type"] = df["product_type"].astype(_PRODUCT_TYPE_DTYPE)

    # Physical indicators
    df["temp_diff_k"] = (df["process_temp_k"] - df["air_temp_k"]).round(2)
    omega_rad_s = df["rotational_speed_rpm"] * (2 * np.pi / 60)
    df["mechanical_power_w"] = (df["torque_nm"] * omega_rad_s).round(2)

    return df
