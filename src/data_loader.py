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

_FAILURE_COLUMNS = list(_FAILURE_LABELS.keys())
_FAILURE_LABEL_ARRAY = np.array(list(_FAILURE_LABELS.values()))
_BINARY_COLUMNS = ["failure_any", *_FAILURE_COLUMNS]

_RPM_TO_RAD_PER_S = 2 * np.pi / 60
_PRODUCT_TYPE_DTYPE = pd.CategoricalDtype(categories=["L", "M", "H"], ordered=True)


def _validate_raw_schema(df: pd.DataFrame) -> None:
    """Fail fast if the source CSV is empty or lacks required telemetry columns."""
    if df.empty:
        raise ValueError("Source CSV contains no data rows.")
    missing = set(_RENAME_MAPPING.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Source CSV missing required column(s): {sorted(missing)}")


def _build_operational_status(df: pd.DataFrame) -> pd.Series:
    """Derive operational status labels from failure flags using NumPy indexing."""
    failure_mask = df[_FAILURE_COLUMNS].to_numpy(dtype=bool)
    has_specific = failure_mask.any(axis=1)
    is_failure = has_specific | df["failure_any"].to_numpy(dtype=bool)

    result = np.full(len(df), "Normal operation", dtype=object)
    for idx in np.flatnonzero(is_failure):
        result[idx] = (
            ", ".join(_FAILURE_LABEL_ARRAY[failure_mask[idx]])
            if has_specific[idx]
            else "Unknown failure"
        )

    return pd.Series(result, index=df.index)


@st.cache_data
def load_data(filepath: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load raw telemetry data, standardize schema, and compute engineering features."""
    df = pd.read_csv(filepath)
    _validate_raw_schema(df)
    df = df.rename(columns=_RENAME_MAPPING)

    df[_BINARY_COLUMNS] = df[_BINARY_COLUMNS].astype(bool)
    df["product_type"] = df["product_type"].astype(_PRODUCT_TYPE_DTYPE)

    df["temp_diff_k"] = (df["process_temp_k"] - df["air_temp_k"]).round(2)
    rotational_speed_rad_s = df["rotational_speed_rpm"] * _RPM_TO_RAD_PER_S
    df["mechanical_power_w"] = (df["torque_nm"] * rotational_speed_rad_s).round(2)

    df["operational_status"] = _build_operational_status(df)

    return df
