"""
Module C: Rock & Fluid Data Dashboard

Lets the user upload a CSV of rock/fluid core data (must contain at
least 'porosity' and 'permeability' columns), shows summary statistics,
lets the user filter by a minimum porosity threshold, plots a porosity
histogram and a porosity-permeability crossplot, and lets the user
download the filtered data as CSV.
"""

import io

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="🪨", layout="wide")
st.title("🪨 Rock & Fluid Data Dashboard")
st.caption(
    "Upload a CSV of rock/core or fluid sample data to explore, filter, "
    "and visualise it."
)

st.info(
    "Expected columns: a **porosity** column (fraction or %) and a "
    "**permeability** column (mD), plus any other columns you like "
    "(sample ID, depth, lithology, etc.). Column name matching is "
    "case-insensitive and tolerant of common variants."
)

uploaded_file = st.file_uploader("Upload rock/fluid data CSV", type=["csv"])


def find_column(df: pd.DataFrame, candidates):
    """Return the first column in df whose name matches (case-insensitive,
    substring) one of the candidate strings, or None if none match."""
    lower_cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_cols:
            return lower_cols[cand]
    for col_lower, original in lower_cols.items():
        for cand in candidates:
            if cand in col_lower:
                return original
    return None


if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read this file as a CSV: {e}")
        st.stop()

    if df.empty:
        st.error("The uploaded CSV appears to be empty.")
        st.stop()

    st.subheader("Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Summary statistics")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)

    porosity_col = find_column(df, ["porosity", "poro", "phi"])
    permeability_col = find_column(df, ["permeability", "perm", "k"])

    if porosity_col is None:
        st.warning(
            "Couldn't automatically detect a porosity column. Please "
            "select it manually below."
        )
        porosity_col = st.selectbox("Porosity column", df.columns)
    if permeability_col is None:
        st.warning(
            "Couldn't automatically detect a permeability column. Please "
            "select it manually below."
        )
        permeability_col = st.selectbox("Permeability column", df.columns)

    # Coerce to numeric, dropping rows that can't be parsed for these two
    # columns so filtering/plots don't break on stray text values.
    df[porosity_col] = pd.to_numeric(df[porosity_col], errors="coerce")
    df[permeability_col] = pd.to_numeric(df[permeability_col], errors="coerce")
    n_dropped = df[[porosity_col, permeability_col]].isna().any(axis=1).sum()
    if n_dropped:
        st.caption(
            f"⚠️ {n_dropped} row(s) had non-numeric porosity/permeability "
            f"values and are excluded from the charts/filter below."
        )
    clean_df = df.dropna(subset=[porosity_col, permeability_col]).copy()

    st.divider()
    st.subheader("Filter")

    poro_min = float(clean_df[porosity_col].min())
    poro_max = float(clean_df[porosity_col].max())
    threshold = st.slider(
        f"Show only samples where {porosity_col} >",
        min_value=poro_min,
        max_value=poro_max,
        value=poro_min,
        help="Drag to set a minimum porosity threshold. Only rows above "
             "this value are kept in the charts and the download below.",
    )

    filtered_df = clean_df[clean_df[porosity_col] > threshold]
    st.write(
        f"**{len(filtered_df)}** of **{len(clean_df)}** samples pass the filter "
        f"({porosity_col} > {threshold:.3g})."
    )

    st.divider()
    st.subheader("Charts")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.write(f"**{porosity_col} histogram**")
        if len(filtered_df) > 0:
            hist_data = filtered_df[porosity_col]
            bin_count = min(20, max(5, len(hist_data) // 3))
            counts, bin_edges = pd.cut(hist_data, bins=bin_count, retbins=True)
            hist_df = counts.value_counts().sort_index()
            hist_df.index = [f"{interval.left:.3g}-{interval.right:.3g}" for interval in hist_df.index]
            st.bar_chart(hist_df)
        else:
            st.write("No data to display after filtering.")

    with chart_col2:
        st.write(f"**{porosity_col} vs {permeability_col} crossplot**")
        if len(filtered_df) > 0:
            st.scatter_chart(
                filtered_df, x=porosity_col, y=permeability_col,
            )
        else:
            st.write("No data to display after filtering.")

    st.divider()
    st.subheader("Download filtered data")

    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_buffer.getvalue(),
        file_name="filtered_rock_fluid_data.csv",
        mime="text/csv",
    )

else:
    st.write("👆 Upload a CSV file to get started.")
    st.write(
        "Don't have one handy? A `sample_rock_data.csv` file is included "
        "in the GitHub repository's `sample_data/` folder for testing."
    )
