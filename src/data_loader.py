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

_FAILURE_LABELS = {
    "failure_tool_wear": "Tool wear (TWF)",
    "failure_heat_dissipation": "Heat dissipation (HDF)",
    "failure_power": "Power failure (PWF)",
    "failure_overstrain": "Overstrain (OSF)",
    "failure_random": "Random failure (RNF)",
}

_PRODUCT_TYPE_DTYPE = pd.CategoricalDtype(categories=["L", "M", "H"], ordered=True)


def _validate_raw_schema(df: pd.DataFrame) -> None:
    """Fail fast if the source CSV is empty or lacks required telemetry columns."""
    if df.empty:
        raise ValueError("Source CSV contains no data rows.")
    missing = set(_RENAME_MAPPING.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Source CSV missing required column(s): {sorted(missing)}")


def _get_operational_status(row: pd.Series) -> str:
    """Map binary failure flags to human-readable labels."""
    if not row["failure_any"]:
        return "Normal operation"

    causes = [label for col, label in _FAILURE_LABELS.items() if row[col]]
    return ", ".join(causes) if causes else "Unknown failure"


@st.cache_data
def load_data(filepath: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load raw telemetry data, standardize schema, and compute engineering features."""
    df = pd.read_csv(filepath)
    _validate_raw_schema(df)
    df = df.rename(columns=_RENAME_MAPPING)

    # Types optimization
    failure_cols = ["failure_any", *_FAILURE_LABELS.keys()]
    df[failure_cols] = df[failure_cols].astype(bool)
    df["product_type"] = df["product_type"].astype(_PRODUCT_TYPE_DTYPE)

    # Physical indicators
    df["temp_diff_k"] = (df["process_temp_k"] - df["air_temp_k"]).round(2)
    omega_rad_s = df["rotational_speed_rpm"] * (2 * np.pi / 60)
    df["mechanical_power_w"] = (df["torque_nm"] * omega_rad_s).round(2)

    # Qualitative operational state
    df["operational_status"] = df.apply(_get_operational_status, axis=1)

    return df
